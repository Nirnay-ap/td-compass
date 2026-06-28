"""Deterministic fallback responder used when no LLM_API_KEY is configured.

Provides basic intent matching over the same data tools so the product remains
demoable offline. Not as flexible as the LLM path.
"""
from __future__ import annotations

from .tools import dispatch


def rule_based_answer(messages: list[dict[str, str]]) -> str:
    q = ""
    for m in reversed(messages):
        if m["role"] == "user":
            q = m["content"].lower()
            break

    note = "_(LLM not configured — showing a rule-based answer. Add an API key for full conversational intelligence.)_\n\n"

    if any(w in q for w in ["expir", "renew", "lapse", "reminder"]):
        data = dispatch("get_expiring_items", {"within_days": 90})
        if not data["items"]:
            return note + "No competencies or certifications are expiring in the next 90 days."
        lines = ["**Expiring / expired items (next 90 days)**\n",
                 "| Associate | Item | Type | Expiry | Days | Status |",
                 "|---|---|---|---|---|---|"]
        for i in data["items"][:20]:
            lines.append(
                f"| {i['associate_name']} | {i['name']} | {i['item_type']} | "
                f"{i['expiry_date']} | {i['days_to_expiry']} | {i['status']} |")
        return note + "\n".join(lines)

    if any(w in q for w in ["promot", "progress", "career", "ready", "nominat"]):
        data = dispatch("get_progression_candidates", {"only_ready": True})
        lines = ["**Career-progression ready candidates**\n",
                 "| Associate | Band | LH (YTD/Target) | E2 | Rating |",
                 "|---|---|---|---|---|"]
        for c in data["candidates"][:20]:
            lines.append(
                f"| {c['associate_name']} | {c['band']} | "
                f"{c['ytd_learning_hours']}/{c['ytd_target_hours']} | "
                f"{c['e2_competencies']} | {c['performance_rating']} |")
        return note + "\n".join(lines)

    if any(w in q for w in ["headcount", "summary", "overview", "how many", "total"]):
        s = dispatch("get_org_summary", {})
        return note + (
            f"**Org summary (as of {s['as_of']})**\n\n"
            f"- Total headcount: {s['headcount']['total']}\n"
            f"- Avg YTD learning hours: {s['avg_ytd_learning_hours']}\n"
            f"- E1 competencies: {s['total_e1_competencies']}, "
            f"E2 competencies: {s['total_e2_competencies']}\n"
            f"- Items expiring/expired: {s['items_expiring_or_expired']}\n")

    # default: try to find a person mentioned
    results = dispatch("search_associates", {"query": q})
    if results:
        a = results[0]
        prof = dispatch("get_associate_profile", {"id_or_name": a["id"]})
        return note + _profile_md(prof)

    return note + (
        "Try asking about: an associate by name, expiring competencies/certifications, "
        "promotion-ready candidates, or an org summary.")


def _profile_md(p: dict) -> str:
    lines = [f"**{p['name']}** ({p['id']}) — {p['designation']}, {p['band']}",
             f"Project: {p['project']} · PM: {p['project_manager']} · TD: {p['td_manager']}",
             f"Experience: {p['total_experience_years']} yrs · Rating: {p['performance_rating']}",
             f"YTD learning hours: {p['ytd_learning_hours']}/{p['ytd_target_hours']} · "
             f"E1: {p['e1_competencies']}, E2: {p['e2_competencies']}\n"]
    if p["competencies"]:
        lines.append("**Competencies:** " + ", ".join(
            f"{c['name']} ({c['level']}, {c['status']})" for c in p["competencies"]))
    if p["certifications"]:
        lines.append("**Certifications:** " + ", ".join(
            f"{c['name']} ({c['type']}, {c['status']})" for c in p["certifications"]))
    return "\n".join(lines)
