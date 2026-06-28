"""LLM agent for TD Compass.

Supports OpenAI and Anthropic, auto-detected from the LLM_API_KEY prefix
(Anthropic keys start with 'sk-ant-'). Runs a tool-calling loop so the model can
query the talent-development data store before answering. Falls back to a
deterministic rule-based responder when no API key is configured, so the app is
always usable.
"""
from __future__ import annotations

import json
import os
from typing import Any

from .tools import TOOL_SPECS, dispatch
from .fallback import rule_based_answer

SYSTEM_PROMPT = """You are TD Compass, an AI assistant for a technology services \
company. You help Project Managers and Talent Development (TD) Managers make \
informed decisions about employee development, TD program nominations, and career \
progression.

You have tools to look up consolidated associate data (learning hours, internal & \
external certifications, E1/E2 competencies and their expiry, upcoming TD programs, \
headcount) and HR/TD policies. Always ground answers in tool data — call tools to \
fetch real numbers instead of guessing. When asked for recommendations \
(nominations, promotions, skill gaps), reason against the relevant HR policy and \
cite the specific evidence (e.g. learning hours vs target, E2 competencies, \
expiring certifications).

Be concise and decision-oriented. Prefer compact markdown tables for lists of \
people or items. Proactively flag competencies/certifications that are expiring \
soon or expired. All data is illustrative dummy data."""

MAX_TOOL_ROUNDS = 6


def detect_provider() -> str | None:
    key = os.environ.get("LLM_API_KEY", "").strip()
    if not key:
        return None
    if key.startswith("sk-ant-"):
        return "anthropic"
    if key.startswith("gsk_"):
        return "groq"
    return "openai"


def _openai_tools() -> list[dict]:
    return [{"type": "function", "function": {
        "name": t["name"], "description": t["description"],
        "parameters": t["parameters"]}} for t in TOOL_SPECS]


def _anthropic_tools() -> list[dict]:
    return [{"name": t["name"], "description": t["description"],
             "input_schema": t["parameters"]} for t in TOOL_SPECS]


def run_agent(messages: list[dict[str, str]]) -> dict[str, Any]:
    """messages: list of {role: 'user'|'assistant', content: str}.
    Returns {answer: str, tool_calls: [..], provider: str}.
    """
    provider = detect_provider()
    if provider == "anthropic":
        return _run_anthropic(messages)
    if provider in ("openai", "groq"):
        return _run_openai(messages, provider)
    return {"answer": rule_based_answer(messages), "tool_calls": [], "provider": "rule-based"}


# OpenAI-compatible providers: (base_url, default model). OpenAI itself uses the
# SDK default base URL.
_OPENAI_COMPATIBLE = {
    "openai": (None, "gpt-4o-mini"),
    "groq": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
}


def _run_openai(messages: list[dict[str, str]], provider: str = "openai") -> dict[str, Any]:
    from openai import OpenAI

    base_url, default_model = _OPENAI_COMPATIBLE[provider]
    client = OpenAI(api_key=os.environ["LLM_API_KEY"], base_url=base_url)
    model = os.environ.get("LLM_MODEL", default_model)
    convo: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    convo += [{"role": m["role"], "content": m["content"]} for m in messages]
    used: list[dict] = []

    for _ in range(MAX_TOOL_ROUNDS):
        resp = client.chat.completions.create(
            model=model, messages=convo, tools=_openai_tools(),
            temperature=0.2,
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return {"answer": msg.content or "", "tool_calls": used, "provider": provider}
        convo.append({
            "role": "assistant", "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls],
        })
        for tc in msg.tool_calls:
            args = _safe_json(tc.function.arguments)
            result = dispatch(tc.function.name, args)
            used.append({"name": tc.function.name, "args": args})
            convo.append({
                "role": "tool", "tool_call_id": tc.id,
                "content": json.dumps(result, default=str),
            })
    final = client.chat.completions.create(model=model, messages=convo, temperature=0.2)
    return {"answer": final.choices[0].message.content or "", "tool_calls": used, "provider": provider}


def _run_anthropic(messages: list[dict[str, str]]) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["LLM_API_KEY"])
    model = os.environ.get("LLM_MODEL", "claude-3-5-sonnet-latest")
    convo: list[dict[str, Any]] = [
        {"role": m["role"], "content": m["content"]} for m in messages]
    used: list[dict] = []

    for _ in range(MAX_TOOL_ROUNDS):
        resp = client.messages.create(
            model=model, max_tokens=1500, system=SYSTEM_PROMPT,
            messages=convo, tools=_anthropic_tools(),
        )
        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        text = "".join(b.text for b in resp.content if b.type == "text")
        if not tool_uses:
            return {"answer": text, "tool_calls": used, "provider": "anthropic"}
        convo.append({"role": "assistant", "content": [b.model_dump() for b in resp.content]})
        results = []
        for tu in tool_uses:
            result = dispatch(tu.name, dict(tu.input))
            used.append({"name": tu.name, "args": dict(tu.input)})
            results.append({
                "type": "tool_result", "tool_use_id": tu.id,
                "content": json.dumps(result, default=str),
            })
        convo.append({"role": "user", "content": results})
    final = client.messages.create(
        model=model, max_tokens=1500, system=SYSTEM_PROMPT, messages=convo)
    text = "".join(b.text for b in final.content if b.type == "text")
    return {"answer": text, "tool_calls": used, "provider": "anthropic"}


def _safe_json(s: str) -> dict:
    try:
        return json.loads(s) if s else {}
    except json.JSONDecodeError:
        return {}
