"""REST API routes for TD Compass."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..ai.agent import detect_provider, run_agent
from ..data.store import get_store

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_provider": detect_provider() or "rule-based"}


@router.get("/summary")
def summary() -> dict:
    return get_store().org_summary()


@router.get("/managers")
def managers() -> dict:
    store = get_store()
    return {
        "project_managers": sorted(set(store.project_managers.values())),
        "td_managers": sorted(set(store.td_managers)),
    }


@router.get("/associates")
def associates(manager: str | None = None, q: str | None = None) -> dict:
    store = get_store()
    if manager:
        items = store.team_for_manager(manager)
    elif q:
        items = store.search_associates(q)
    else:
        items = store.list_associates()
    return {"count": len(items), "associates": [a.model_dump() for a in items]}


@router.get("/associates/{associate_id}")
def associate(associate_id: str) -> dict:
    a = get_store().get_associate(associate_id)
    if not a:
        raise HTTPException(status_code=404, detail="Associate not found")
    return a.model_dump()


@router.get("/reminders")
def reminders(within_days: int = 90, manager: str | None = None) -> dict:
    store = get_store()
    items = store.expiring_items(within_days=within_days)
    if manager:
        m = manager.lower()
        items = [i for i in items if m in i["project_manager"].lower()
                 or m in i["td_manager"].lower()]
    expired = [i for i in items if i["days_to_expiry"] < 0]
    soon = [i for i in items if i["days_to_expiry"] >= 0]
    return {"count": len(items), "expired": expired, "expiring_soon": soon}


@router.get("/progression")
def progression(manager: str | None = None, only_ready: bool = False) -> dict:
    store = get_store()
    cands = store.progression_candidates()
    if manager:
        team_ids = {a.id for a in store.team_for_manager(manager)}
        cands = [c for c in cands if c["associate_id"] in team_ids]
    if only_ready:
        cands = [c for c in cands if c["ready"]]
    return {"count": len(cands), "candidates": cands}


@router.get("/policies")
def policies() -> dict:
    return {"policies": [p.model_dump() for p in get_store().policies]}


@router.post("/chat")
def chat(req: ChatRequest) -> dict:
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    result = run_agent([m.model_dump() for m in req.messages])
    return result
