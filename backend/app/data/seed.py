"""Deterministic dummy-data generator for TD Compass.

Produces a realistic-looking talent-development dataset for a services company:
associates with learning hours, certifications, competencies (E1/E2), upcoming
TD programs, plus org headcount and HR policies. All data is fake.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

SEED = 42

FIRST_NAMES = [
    "Aarav", "Diya", "Vivaan", "Ananya", "Aditya", "Ishita", "Karthik", "Meera",
    "Rohan", "Sneha", "Arjun", "Priya", "Siddharth", "Kavya", "Rahul", "Nisha",
    "Vikram", "Pooja", "Aniket", "Shreya", "Manish", "Divya", "Sanjay", "Tara",
    "Harish", "Lakshmi", "Naveen", "Ritu", "Gaurav", "Anjali", "Deepak", "Swathi",
    "Varun", "Neha", "Akash", "Sania", "Praveen", "Komal", "Rakesh", "Bhavna",
]
LAST_NAMES = [
    "Sharma", "Reddy", "Nair", "Iyer", "Patel", "Gupta", "Menon", "Rao",
    "Verma", "Joshi", "Mehta", "Pillai", "Bose", "Kulkarni", "Chopra", "Das",
    "Banerjee", "Kapoor", "Mishra", "Naidu",
]

DESIGNATIONS = [
    ("Associate Engineer", "B3", 1.5),
    ("Software Engineer", "B4", 3.0),
    ("Senior Software Engineer", "B5", 6.0),
    ("Tech Lead", "B6", 9.0),
    ("Senior Tech Lead", "B7", 12.0),
]

DEPARTMENTS = ["Cloud & Infra", "Data & AI", "Digital Engineering", "Quality Engineering", "Enterprise Apps"]
LOCATIONS = ["Bengaluru", "Hyderabad", "Pune", "Chennai", "Gurugram"]

PROJECTS = [
    ("Atlas - BFSI Modernization", "Cloud & Infra"),
    ("Helix - Healthcare Analytics", "Data & AI"),
    ("Orion - Retail Commerce", "Digital Engineering"),
    ("Nova - Insurance Platform", "Enterprise Apps"),
    ("Quasar - Telecom OSS", "Quality Engineering"),
    ("Pulse - Banking Data Lake", "Data & AI"),
]

PROJECT_MANAGERS = {
    "Atlas - BFSI Modernization": "Suresh Krishnan",
    "Helix - Healthcare Analytics": "Anita Deshpande",
    "Orion - Retail Commerce": "Mohan Subramanian",
    "Nova - Insurance Platform": "Rekha Balachandran",
    "Quasar - Telecom OSS": "Imran Sheikh",
    "Pulse - Banking Data Lake": "Anita Deshpande",
}

TD_MANAGERS = ["Lalitha Venkatesh", "Praveen Kumar", "Sandhya Raghavan"]

COMPETENCY_CATALOG = [
    ("AWS Cloud Foundations", "Cloud", "E1"),
    ("AWS Solutions Architecture", "Cloud", "E2"),
    ("Azure Administration", "Cloud", "E1"),
    ("Azure Solution Design", "Cloud", "E2"),
    ("Kubernetes & Containers", "DevOps", "E2"),
    ("CI/CD Engineering", "DevOps", "E1"),
    ("Python Programming", "Programming", "E1"),
    ("Java Enterprise", "Programming", "E1"),
    ("Advanced Java Architecture", "Programming", "E2"),
    ("React Frontend", "Programming", "E1"),
    ("Data Engineering", "Data & AI", "E1"),
    ("Machine Learning", "Data & AI", "E2"),
    ("Generative AI Foundations", "Data & AI", "E1"),
    ("Applied GenAI Solutions", "Data & AI", "E2"),
    ("Solution Architecture", "Architecture", "E2"),
    ("Microservices Design", "Architecture", "E2"),
    ("Cybersecurity Fundamentals", "Security", "E1"),
    ("Application Security", "Security", "E2"),
    ("BFSI Domain", "Domain", "E1"),
    ("Healthcare Domain", "Domain", "E1"),
    ("Agile & Scrum", "Process", "E1"),
    ("Project Management", "Process", "E2"),
]

CERT_CATALOG = [
    ("AWS Certified Solutions Architect - Associate", "Amazon Web Services", "External", 1095),
    ("AWS Certified Developer - Associate", "Amazon Web Services", "External", 1095),
    ("Microsoft Certified: Azure Administrator", "Microsoft", "External", 365),
    ("Microsoft Certified: Azure Solutions Architect", "Microsoft", "External", 365),
    ("Google Professional Cloud Architect", "Google Cloud", "External", 730),
    ("Certified Kubernetes Administrator (CKA)", "CNCF", "External", 1095),
    ("Professional Scrum Master I", "Scrum.org", "External", None),
    ("PMP", "PMI", "External", 1095),
    ("Oracle Certified Professional: Java SE", "Oracle", "External", None),
    ("Databricks Certified Data Engineer", "Databricks", "External", 730),
    ("Internal: Cloud Practitioner Bootcamp", "TD Academy", "Internal", 730),
    ("Internal: GenAI Builder Program", "TD Academy", "Internal", 365),
    ("Internal: Full-Stack Mastery", "TD Academy", "Internal", 730),
    ("Internal: Secure Coding Certification", "TD Academy", "Internal", 365),
]

TD_PROGRAM_CATALOG = [
    ("Cloud Architecture Masterclass", "Cloud"),
    ("Applied GenAI for Engineers", "Data & AI"),
    ("Leadership Essentials for Tech Leads", "Leadership"),
    ("Advanced Kubernetes in Production", "DevOps"),
    ("Data Engineering with Spark", "Data & AI"),
    ("Microservices & System Design", "Architecture"),
    ("Secure Coding Practices", "Security"),
    ("Scrum Master Certification Prep", "Process"),
]

PROGRAM_STATUSES = ["Nominated", "Confirmed", "Waitlisted", "Recommended"]
PERF_RATINGS = ["Exceeds Expectations", "Meets Expectations", "Meets Expectations", "Outstanding", "Developing"]


def _iso(d: date) -> str:
    return d.isoformat()


def generate_dataset(today: date | None = None) -> dict:
    today = today or date.today()
    rng = random.Random(SEED)
    associates: list[dict] = []

    num = 36
    for i in range(num):
        fn = rng.choice(FIRST_NAMES)
        ln = rng.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        emp_id = f"TG{10001 + i}"
        designation, band, base_exp = rng.choice(DESIGNATIONS)
        exp = round(base_exp + rng.uniform(-1.0, 3.0), 1)
        exp = max(0.5, exp)
        project, dept = rng.choice(PROJECTS)
        pm = PROJECT_MANAGERS[project]
        tdm = rng.choice(TD_MANAGERS)
        location = rng.choice(LOCATIONS)
        doj = today - timedelta(days=int(exp * 365) + rng.randint(0, 200))
        email = f"{fn.lower()}.{ln.lower()}@example.com"

        # Learning hours: last 4 quarters
        learning = []
        year = today.year
        for q in range(1, 5):
            target = 40.0
            hours = round(rng.uniform(8, 60), 1)
            learning.append({"year": year, "quarter": f"Q{q}", "hours": hours, "target_hours": target})

        # Competencies
        comp_count = rng.randint(2, 6)
        chosen = rng.sample(COMPETENCY_CATALOG, comp_count)
        competencies = []
        for cname, ccat, clevel in chosen:
            # ~65% of competencies have a validity window (need refresh). Cluster
            # expiry near 'today' so reminders show a realistic mix of active,
            # expiring-soon, and recently-expired items.
            if rng.random() < 0.65:
                validity = rng.choice([365, 540, 730])
                days_to_expiry = rng.randint(-150, 400)
                expiry = today + timedelta(days=days_to_expiry)
                acquired = expiry - timedelta(days=validity)
            else:
                expiry = None
                acquired = today - timedelta(days=rng.randint(120, 1400))
            competencies.append({
                "name": cname, "category": ccat, "level": clevel,
                "acquired_date": _iso(acquired),
                "expiry_date": _iso(expiry) if expiry else None,
            })

        # Certifications
        cert_count = rng.randint(1, 4)
        cert_choices = rng.sample(CERT_CATALOG, cert_count)
        certifications = []
        for cname, provider, ctype, validity in cert_choices:
            if validity:
                days_to_expiry = rng.randint(-120, 420)
                expiry = today + timedelta(days=days_to_expiry)
                completed = expiry - timedelta(days=validity)
            else:
                expiry = None
                completed = today - timedelta(days=rng.randint(60, 1200))
            certifications.append({
                "name": cname, "provider": provider, "type": ctype,
                "completed_date": _iso(completed),
                "expiry_date": _iso(expiry) if expiry else None,
            })

        # Upcoming TD programs
        prog_count = rng.randint(0, 3)
        programs = []
        for pname, pcat in rng.sample(TD_PROGRAM_CATALOG, prog_count):
            start = today + timedelta(days=rng.randint(7, 120))
            programs.append({
                "name": pname, "category": pcat,
                "start_date": _iso(start),
                "mode": rng.choice(["Classroom", "Virtual", "Self-paced"]),
                "duration_days": rng.choice([1, 2, 3, 5]),
                "status": rng.choice(PROGRAM_STATUSES),
            })

        associates.append({
            "id": emp_id,
            "name": name,
            "email": email,
            "designation": designation,
            "band": band,
            "department": dept,
            "project": project,
            "project_manager": pm,
            "td_manager": tdm,
            "location": location,
            "date_of_joining": _iso(doj),
            "total_experience_years": exp,
            "performance_rating": rng.choice(PERF_RATINGS),
            "learning_hours": learning,
            "certifications": certifications,
            "competencies": competencies,
            "upcoming_td_programs": programs,
        })

    headcount = _build_headcount(associates)
    policies = _build_policies()
    return {
        "generated_for": _iso(today),
        "associates": associates,
        "headcount": headcount,
        "policies": policies,
        "project_managers": PROJECT_MANAGERS,
        "td_managers": TD_MANAGERS,
    }


def _build_headcount(associates: list[dict]) -> dict:
    by_dept: dict[str, int] = {}
    by_project: dict[str, int] = {}
    by_band: dict[str, int] = {}
    for a in associates:
        by_dept[a["department"]] = by_dept.get(a["department"], 0) + 1
        by_project[a["project"]] = by_project.get(a["project"], 0) + 1
        by_band[a["band"]] = by_band.get(a["band"], 0) + 1
    return {
        "total": len(associates),
        "by_department": by_dept,
        "by_project": by_project,
        "by_band": by_band,
    }


def _build_policies() -> list[dict]:
    return [
        {
            "id": "POL-LH-01",
            "title": "Annual Learning Hours Policy",
            "category": "Learning & Development",
            "body": (
                "Every associate is expected to complete a minimum of 40 learning hours "
                "per quarter (160 hours annually). Learning hours include instructor-led "
                "training, self-paced courses, certifications, and internal knowledge "
                "sessions. Associates below 60% of the quarterly target are flagged for a "
                "development conversation with their TD Manager. Learning hours are a "
                "mandatory input for annual career-progression review."
            ),
        },
        {
            "id": "POL-CERT-02",
            "title": "Certification Reimbursement & Validity Policy",
            "category": "Certifications",
            "body": (
                "External certifications from approved providers (AWS, Microsoft, Google, "
                "CNCF, PMI, Oracle, Databricks) are reimbursed 100% on first attempt and "
                "50% on a second attempt. Associates must maintain at least one active, "
                "role-relevant external certification. Certifications within 90 days of "
                "expiry must be renewed; lapsed certifications are not counted toward "
                "competency requirements for progression."
            ),
        },
        {
            "id": "POL-COMP-03",
            "title": "Competency Framework (E1 / E2)",
            "category": "Competency",
            "body": (
                "Competencies are assessed at two proficiency levels. E1 (Foundation) "
                "indicates the ability to work on guided tasks within a skill area. E2 "
                "(Advanced) indicates the ability to independently design and lead work in "
                "that skill area. Competencies have a validity window and must be "
                "re-validated before expiry. A competency within 90 days of its expiry is "
                "marked 'Expiring Soon'."
            ),
        },
        {
            "id": "POL-PROG-04",
            "title": "Career Progression & Promotion Eligibility",
            "category": "Career Progression",
            "body": (
                "Eligibility for promotion to the next band requires: (a) meeting the annual "
                "learning-hours target, (b) at least one E2 competency relevant to the target "
                "role, (c) a performance rating of 'Meets Expectations' or higher for the "
                "latest cycle, and (d) typically 24+ months in the current band. Promotion to "
                "Tech Lead (B6) and above additionally requires demonstrated leadership and "
                "completion of a leadership development program."
            ),
        },
        {
            "id": "POL-NOM-05",
            "title": "TD Program Nomination Guidelines",
            "category": "Talent Development",
            "body": (
                "Project Managers and TD Managers nominate associates for TD programs based "
                "on skill gaps, project demand, and career aspirations. Priority is given to "
                "associates with an upcoming role change, those whose competencies/certs are "
                "expiring, and high performers identified for accelerated growth. Nominations "
                "should align the associate's current competencies with target-role "
                "requirements."
            ),
        },
    ]


if __name__ == "__main__":
    import json
    print(json.dumps(generate_dataset(), indent=2)[:2000])
