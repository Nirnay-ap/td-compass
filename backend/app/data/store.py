"""In-memory data store: builds enriched Associate models from the seed data
and exposes query helpers used by the API and the AI tool layer.

Expiry status and days-to-expiry are computed relative to the current date so
that competency/certification reminders are always accurate.
"""
from __future__ import annotations

from datetime import date

from ..models import Associate, Certification, Competency, Policy, TDProgram
from .seed import generate_dataset

EXPIRING_SOON_DAYS = 90


def _status_and_days(expiry_iso: str | None, today: date) -> tuple[str, int | None]:
    if not expiry_iso:
        return "Active", None
    expiry = date.fromisoformat(expiry_iso)
    days = (expiry - today).days
    if days < 0:
        return "Expired", days
    if days <= EXPIRING_SOON_DAYS:
        return "Expiring Soon", days
    return "Active", days


class DataStore:
    def __init__(self, today: date | None = None) -> None:
        self.today = today or date.today()
        raw = generate_dataset(self.today)
        self.raw = raw
        self.headcount = raw["headcount"]
        self.policies = [Policy(**p) for p in raw["policies"]]
        self.td_managers = raw["td_managers"]
        self.project_managers = raw["project_managers"]
        self.associates: dict[str, Associate] = {}
        for a in raw["associates"]:
            self.associates[a["id"]] = self._build_associate(a)

    def _build_associate(self, a: dict) -> Associate:
        certs = []
        for c in a["certifications"]:
            status, days = _status_and_days(c["expiry_date"], self.today)
            certs.append(Certification(
                name=c["name"], provider=c["provider"], type=c["type"],
                completed_date=c["completed_date"], expiry_date=c["expiry_date"],
                status=status, days_to_expiry=days,
            ))
        comps = []
        e1 = e2 = 0
        for c in a["competencies"]:
            status, days = _status_and_days(c["expiry_date"], self.today)
            comps.append(Competency(
                name=c["name"], category=c["category"], level=c["level"],
                acquired_date=c["acquired_date"], expiry_date=c["expiry_date"],
                status=status, days_to_expiry=days,
            ))
            if c["level"] == "E1":
                e1 += 1
            else:
                e2 += 1
        programs = [TDProgram(**p) for p in a["upcoming_td_programs"]]
        learning = a["learning_hours"]
        ytd_hours = round(sum(l["hours"] for l in learning), 1)
        ytd_target = round(sum(l["target_hours"] for l in learning), 1)
        return Associate(
            id=a["id"], name=a["name"], email=a["email"], designation=a["designation"],
            band=a["band"], department=a["department"], project=a["project"],
            project_manager=a["project_manager"], td_manager=a["td_manager"],
            location=a["location"], date_of_joining=a["date_of_joining"],
            total_experience_years=a["total_experience_years"],
            performance_rating=a["performance_rating"],
            learning_hours=learning, certifications=certs, competencies=comps,
            upcoming_td_programs=programs,
            ytd_learning_hours=ytd_hours, ytd_target_hours=ytd_target,
            e1_competencies=e1, e2_competencies=e2,
        )

    # ---- Query helpers (also used as AI tools) ----

    def list_associates(self) -> list[Associate]:
        return list(self.associates.values())

    def get_associate(self, id_or_name: str) -> Associate | None:
        if id_or_name in self.associates:
            return self.associates[id_or_name]
        q = id_or_name.strip().lower()
        # exact name match first, then contains
        for a in self.associates.values():
            if a.name.lower() == q:
                return a
        for a in self.associates.values():
            if q in a.name.lower():
                return a
        return None

    def search_associates(self, query: str) -> list[Associate]:
        q = query.strip().lower()
        out = []
        for a in self.associates.values():
            hay = " ".join([
                a.name, a.id, a.designation, a.band, a.department, a.project,
                a.project_manager, a.td_manager, a.location, a.performance_rating,
            ]).lower()
            if q in hay:
                out.append(a)
        return out

    def team_for_manager(self, manager_name: str) -> list[Associate]:
        q = manager_name.strip().lower()
        return [a for a in self.associates.values()
                if q in a.project_manager.lower() or q in a.td_manager.lower()]

    def expiring_items(self, within_days: int = EXPIRING_SOON_DAYS,
                       include_expired: bool = True) -> list[dict]:
        out = []
        for a in self.associates.values():
            for c in a.competencies:
                if c.days_to_expiry is None:
                    continue
                if c.days_to_expiry <= within_days and (include_expired or c.days_to_expiry >= 0):
                    out.append({
                        "associate_id": a.id, "associate_name": a.name,
                        "project": a.project, "project_manager": a.project_manager,
                        "td_manager": a.td_manager,
                        "item_type": "Competency", "name": c.name,
                        "level": c.level, "expiry_date": c.expiry_date,
                        "days_to_expiry": c.days_to_expiry, "status": c.status,
                    })
            for c in a.certifications:
                if c.days_to_expiry is None:
                    continue
                if c.days_to_expiry <= within_days and (include_expired or c.days_to_expiry >= 0):
                    out.append({
                        "associate_id": a.id, "associate_name": a.name,
                        "project": a.project, "project_manager": a.project_manager,
                        "td_manager": a.td_manager,
                        "item_type": "Certification", "name": c.name,
                        "level": c.type, "expiry_date": c.expiry_date,
                        "days_to_expiry": c.days_to_expiry, "status": c.status,
                    })
        out.sort(key=lambda x: x["days_to_expiry"])
        return out

    def progression_candidates(self) -> list[dict]:
        """Heuristic readiness for next-band promotion per POL-PROG-04."""
        out = []
        for a in self.associates.values():
            meets_lh = a.ytd_learning_hours >= a.ytd_target_hours
            has_e2 = a.e2_competencies >= 1
            good_perf = a.performance_rating in (
                "Meets Expectations", "Exceeds Expectations", "Outstanding")
            tenure_ok = a.total_experience_years >= 2.0
            score = sum([meets_lh, has_e2, good_perf, tenure_ok])
            reasons = []
            if not meets_lh:
                reasons.append("below annual learning-hours target")
            if not has_e2:
                reasons.append("no E2 competency yet")
            if not good_perf:
                reasons.append("performance rating below threshold")
            if not tenure_ok:
                reasons.append("under 24 months experience")
            out.append({
                "associate_id": a.id, "associate_name": a.name,
                "designation": a.designation, "band": a.band,
                "readiness_score": score, "max_score": 4,
                "ready": score == 4,
                "ytd_learning_hours": a.ytd_learning_hours,
                "ytd_target_hours": a.ytd_target_hours,
                "e2_competencies": a.e2_competencies,
                "performance_rating": a.performance_rating,
                "gaps": reasons,
            })
        out.sort(key=lambda x: (-x["readiness_score"], x["associate_name"]))
        return out

    def org_summary(self) -> dict:
        total_lh = sum(a.ytd_learning_hours for a in self.associates.values())
        expiring = self.expiring_items(include_expired=True)
        return {
            "headcount": self.headcount,
            "avg_ytd_learning_hours": round(
                total_lh / max(1, len(self.associates)), 1),
            "total_e1_competencies": sum(a.e1_competencies for a in self.associates.values()),
            "total_e2_competencies": sum(a.e2_competencies for a in self.associates.values()),
            "items_expiring_or_expired": len(expiring),
            "as_of": self.today.isoformat(),
        }


_store: DataStore | None = None


def get_store() -> DataStore:
    global _store
    if _store is None:
        _store = DataStore()
    return _store
