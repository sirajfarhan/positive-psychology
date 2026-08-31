# Optimism Map — app

The display surface for `learn-optimism`. Read-only by construction: every
route is a GET, and the skill is the only thing that writes.

```
app/
  run.sh     starts both halves, idempotent, owns where the deps go
  backend/   FastAPI over the skill's SQLite store  (port 8787)
  frontend/  Vite + React, one page                 (port 5173)
```

The backend imports the skill's `optimism_db.py` rather than reimplementing
anything, so scoring and orientation have exactly one definition. That import
goes one way only. The store belongs to the skill and this app just reads it,
while the venv and `node_modules` belong to this app and the skill has no
opinion about them.

Those two live in your cache directory rather than in the plugin folder,
because a plugin update replaces that folder wholesale and 122MB of frontend
packages should not be fetched again each time it does. `run.sh` resolves the
location, honours `XDG_CACHE_HOME`, and `run.sh status` prints it.

## Run

```bash
./run.sh
```

That is the whole thing. It starts whatever is missing, prints the URL, and
on a first run it builds the venv and installs the frontend packages itself.
Running it twice is safe. `run.sh status` says what is up and where the deps
live, `run.sh stop` shuts both down, and `--no-open` skips the browser.

Then open http://localhost:5173. Vite proxies `/api` to the backend.

Point it at a different store with `OPTIMISM_DB`, which the skill and the
app both read:

```bash
OPTIMISM_DB=/tmp/demo.db ./run.sh
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
