# TD Compass — Talent Development Intelligence

A conversational AI assistant that gives **Project Managers** and **Talent
Development (TD) Managers** one place to understand an associate's profile, TD
efforts, and relevant HR policies — and to make smarter nomination and
career-progression decisions.

Instead of manually compiling data from Learning Hours reports, certification
trackers, competency sheets, headcount data and shared drives, TD Compass
aggregates everything into a single conversational + dashboard experience.

> All data in this project is **illustrative dummy data**, generated locally.

## Features

- **Conversational assistant** — ask in plain English about any associate or
  team. The AI calls live data tools (it does not hallucinate numbers) and
  answers with compact tables and recommendations.
- **Consolidated associate profile** — learning hours (vs target), internal &
  external certifications, competencies with **E1 / E2** levels and expiry,
  upcoming TD programs, performance and tenure — all in one view.
- **Competency & certification expiry reminders** — proactive alerts for items
  that are expiring soon or already expired, org-wide or per team.
- **Career-progression readiness** — every associate scored against the
  promotion policy (learning hours, an E2 competency, performance, tenure) with
  explicit gaps.
- **Nomination recommendations** — ask the assistant to recommend associates for
  a TD program based on skill gaps and policy.
- **Two role modes** — *TD Manager* (org-wide) and *Project Manager* (their
  team only).

## Architecture

```
frontend/  Next.js 16 + React 19 + Tailwind (chat UI, dashboards, profile drawer)
   └── app/api/[...path]  same-origin proxy → backend
backend/   FastAPI (data store, aggregation, expiry logic, AI agent)
   ├── app/data/seed.py   deterministic dummy-data generator
   ├── app/data/store.py  in-memory store + query/aggregation helpers
   └── app/ai/            LLM agent (OpenAI/Anthropic) with tool-calling + rule-based fallback
```

The AI layer auto-detects the provider from the `LLM_API_KEY` prefix
(`sk-ant-` → Anthropic, `gsk_` → Groq, otherwise OpenAI). Groq uses its
OpenAI-compatible endpoint. If no key is set, it falls back to a deterministic
rule-based responder so the app is always demoable.

## Quick start

```bash
# 1. (optional) add your LLM key for full conversational intelligence
cp backend/.env.example backend/.env   # then edit LLM_API_KEY

# 2. run both services
./dev.sh
```

Then open http://localhost:3000.

### Run services individually

Backend:

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export LLM_API_KEY=sk-...        # optional
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
BACKEND_URL=http://localhost:8000 npm run dev
```

## Key API endpoints

| Endpoint | Description |
|---|---|
| `GET /api/summary` | Org metrics (headcount, avg learning hours, E1/E2 totals) |
| `GET /api/associates?manager=` | List associates (optionally a manager's team) |
| `GET /api/associates/{id}` | Full consolidated profile |
| `GET /api/reminders?within_days=&manager=` | Expiring/expired competencies & certs |
| `GET /api/progression?manager=&only_ready=` | Career-progression readiness |
| `GET /api/policies` | HR / TD policies |
| `POST /api/chat` | Conversational assistant (LLM with data tools) |

## Example questions

- "Which associates have certifications expiring in the next 90 days?"
- "Who is ready for promotion and who has gaps?"
- "Recommend nominations for the Applied GenAI program based on skill gaps."
- "Summarise Aarav Sharma's profile and TD efforts."
