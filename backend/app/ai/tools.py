"""Tool definitions and dispatch for the TD Compass AI agent.

Each tool reads from the in-memory DataStore. Tool schemas are provider-neutral
(JSON Schema) and adapted to OpenAI / Anthropic formats in llm.py.
"""
from __future__ import annotations

from typing import Any

from ..data.store import get_store

TOOL_SPECS: list[dict[str, Any]] = [
    {
        "name": "search_associates",
        "description": (
            "Search associates by any attribute: name, employee id, designation, "
            "band, department, project, manager, location, or performance rating. "
            "Returns lightweight matches. Use this to find people before fetching a "
            "full profile."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Free-text search term."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_associate_profile",
        "description": (
            "Get the complete consolidated profile for one associate by employee id "
            "or full/partial name: learning hours, certifications (internal/external), "
            "competencies with E1/E2 levels and expiry, upcoming TD programs, and "
            "rollups."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id_or_name": {"type": "string", "description": "Employee id (e.g. TG10001) or name."},
            },
            "required": ["id_or_name"],
        },
    },
    {
        "name": "get_team",
        "description": (
            "List all associates reporting to a given Project Manager or TD Manager "
            "(matched by name). Use for team-level questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "manager_name": {"type": "string", "description": "Project Manager or TD Manager name."},
            },
            "required": ["manager_name"],
        },
    },
    {
        "name": "get_expiring_items",
        "description": (
            "List competencies and certifications that are expiring soon or already "
            "expired across the org, sorted by urgency. Use for reminder / renewal "
            "questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "within_days": {"type": ["integer", "string"], "description": "Look-ahead window in days (default 90)."},
                "manager_name": {"type": "string", "description": "Optional: restrict to a manager's team."},
            },
            "required": [],
        },
    },
    {
        "name": "get_progression_candidates",
        "description": (
            "Assess career-progression readiness for associates against the promotion "
            "policy (learning hours, E2 competency, performance, tenure). Returns a "
            "readiness score and gaps per associate."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "manager_name": {"type": "string", "description": "Optional: restrict to a manager's team."},
                "only_ready": {"type": ["boolean", "string"], "description": "If true, only fully-ready candidates."},
            },
            "required": [],
        },
    },
    {
        "name": "get_org_summary",
        "description": "High-level org metrics: headcount breakdowns, average learning hours, E1/E2 totals, expiring items count.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "search_hr_policies",
        "description": (
            "Search HR / Talent Development policies (learning hours, certifications, "
            "competency framework, career progression, nominations) and return the "
            "relevant policy text."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Topic to look up, e.g. 'promotion eligibility'."},
            },
            "required": ["query"],
        },
    },
]


# Cap the number of records returned to the LLM to keep token usage well within
# provider rate limits (e.g. Groq free tier). The `count` field still reports the
# true total so the model can say "showing N of M".
MAX_ITEMS = 25


def _trim_reminder(i: dict) -> dict:
    return {
        "associate_name": i["associate_name"], "item_type": i["item_type"],
        "name": i["name"], "level": i["level"], "expiry_date": i["expiry_date"],
        "days_to_expiry": i["days_to_expiry"], "status": i["status"],
        "project": i["project"],
    }


def dispatch(name: str, args: dict[str, Any]) -> Any:
    store = get_store()
    if name == "search_associates":
        return [_brief(a) for a in store.search_associates(args.get("query", ""))][:MAX_ITEMS]
    if name == "get_associate_profile":
        a = store.get_associate(args.get("id_or_name", ""))
        return a.model_dump() if a else {"error": "Associate not found."}
    if name == "get_team":
        team = store.team_for_manager(args.get("manager_name", ""))
        return {"manager": args.get("manager_name"), "team_size": len(team),
                "members": [_brief(a) for a in team][:MAX_ITEMS]}
    if name == "get_expiring_items":
        within = _as_int(args.get("within_days"), 90)
        items = store.expiring_items(within_days=within)
        mgr = args.get("manager_name")
        if mgr:
            m = mgr.lower()
            items = [i for i in items if m in i["project_manager"].lower()
                     or m in i["td_manager"].lower()]
        return {"count": len(items), "within_days": within,
                "showing": min(len(items), MAX_ITEMS),
                "items": [_trim_reminder(i) for i in items[:MAX_ITEMS]]}
    if name == "get_progression_candidates":
        cands = store.progression_candidates()
        mgr = args.get("manager_name")
        if mgr:
            team_ids = {a.id for a in store.team_for_manager(mgr)}
            cands = [c for c in cands if c["associate_id"] in team_ids]
        if _as_bool(args.get("only_ready")):
            cands = [c for c in cands if c["ready"]]
        return {"count": len(cands), "showing": min(len(cands), MAX_ITEMS),
                "candidates": cands[:MAX_ITEMS]}
    if name == "get_org_summary":
        return store.org_summary()
    if name == "search_hr_policies":
        q = (args.get("query") or "").lower()
        matches = []
        for p in store.policies:
            hay = f"{p.title} {p.category} {p.body}".lower()
            if not q or any(tok in hay for tok in q.split()):
                matches.append(p.model_dump())
        if not matches:
            matches = [p.model_dump() for p in store.policies]
        return {"policies": matches}
    return {"error": f"Unknown tool: {name}"}


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def _brief(a) -> dict:
    return {
        "id": a.id, "name": a.name, "designation": a.designation, "band": a.band,
        "department": a.department, "project": a.project,
        "project_manager": a.project_manager, "td_manager": a.td_manager,
        "performance_rating": a.performance_rating,
        "ytd_learning_hours": a.ytd_learning_hours,
        "ytd_target_hours": a.ytd_target_hours,
        "e1_competencies": a.e1_competencies, "e2_competencies": a.e2_competencies,
    }
