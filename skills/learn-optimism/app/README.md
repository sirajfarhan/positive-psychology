# Optimism Map — app

The display surface for `learn-optimism`. Read-only by construction: every
route is a GET, and the skill is the only thing that writes.

```
app/
  backend/   FastAPI over the skill's SQLite store  (port 8787)
  frontend/  Vite + React, one page                 (port 5173)
```

The backend imports `scripts/optimism_db.py` rather than reimplementing
anything, so scoring and orientation have exactly one definition.

## Run

```bash
cd app
backend/.venv/bin/python backend/server.py &
cd frontend && npm run dev
```

Then open http://localhost:5173. Vite proxies `/api` to the backend.

Point it at a different store with `OPTIMISM_DB`:

```bash
OPTIMISM_DB=/tmp/longview-demo.db backend/.venv/bin/python backend/server.py
```

First run only:

```bash
python3 -m venv backend/.venv && backend/.venv/bin/pip install fastapi uvicorn
cd frontend && npm install
```

## Routes

| | |
|---|---|
| `GET /api/reading` | everything the page draws, oriented and ordered |
| `GET /api/ledger` | mastery state per concept |
| `GET /api/health` | which store is attached, and whether it exists |

## What the page does and does not do

Bars diverge from a centred spine because the data is bipolar — which side of
neutral you sit on matters more than how far along you are. Positive is always
the optimistic direction, in both blocks.

The pole words **swap sides between the blocks**, and that is correct rather
than a bug: a lasting cause is pessimistic for a setback and optimistic for a
win. Orienting both blocks by optimism is what makes the composite meaningful.

`builds` is drawn set apart from the three above it and is **never averaged
into the composite** — different construct, different instrument, weaker
method. It is reported, not composited.

The headline states the finding before the chart, because unlabelled bar
lengths teach nobody anything. It reads each valence independently, so a strong
lean on one side is still named when the other side is flat.

There is no input on this page and there never should be. Everything changes
through the skill in chat, which is also where the drills live — an instruction
with nowhere to comply is worse than no instruction.
