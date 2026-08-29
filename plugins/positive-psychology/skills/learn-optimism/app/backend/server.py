#!/usr/bin/env python3
"""HTTP layer over the optimism store, and it takes no orders.

Every route is a GET, so nothing the page does can change what the skill
captured. Honesty about the plumbing, though: con() runs store.init() on
each request, which catches up a pending migration and re-upserts the fixed
concept seed, then commits. Both are idempotent, both touch only the seed,
and the learner's sentences are never written from here.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# the skill's script is the single source of scoring and orientation logic
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import optimism_db as store  # noqa: E402

import os  # noqa: E402

# OPTIMISM_DB lets you point the page at a demo store without touching the real one
DB = Path(os.environ.get("OPTIMISM_DB", store.DEFAULT_DB)).expanduser()

app = FastAPI(title="Optimism Map", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def con():
    if not DB.exists():
        raise HTTPException(404, f"no store at {DB} - run: optimism_db.py init")
    c = store.connect(DB)
    store.init(c)
    return c


# rows in display order, with the pole words for each block
ROWS = [
    ("permanence", "permanent", "temporary"),
    ("pervasiveness", "general", "specific"),
    ("personalization", "personal", "situational"),
]


@app.get("/api/reading")
def reading():
    """Everything the page draws, already oriented and ordered."""
    c = con()
    r = store.reading(c)

    blocks = []
    for valence, heading in (("bad", "when things go wrong"),
                             ("good", "when things go right")):
        block = r.get(valence) or {}
        rows = []
        for dim, pessimistic, optimistic in ROWS:
            cell = block.get(dim)
            if not cell:
                continue
            # the optimistic pole sits on the right in both blocks, so for a
            # win the words swap sides -- same inversion the scores encode
            left, right = (pessimistic, optimistic) if valence == "bad" \
                else (optimistic, pessimistic)
            rows.append({"dim": dim, "left": left, "right": right,
                         "value": cell["value"], "n": cell["n"]})
        # 'builds' is still scored and stored, just not drawn for now
        if rows:
            blocks.append({"heading": heading, "n": block.get("n", 0), "rows": rows})

    c.close()
    return {"overall": r["overall"], "n": r["n"], "since": r["since"],
            "finding": r["finding"], "readiness": r["readiness"],
            "trend": r.get("trend"), "window": r.get("window"),
            "blocks": blocks, "scale": {"min": -3, "max": 3}}


@app.get("/api/focus")
def focus():
    """Only what the learner is currently being tested on."""
    c = con()
    rows = store.focus(c)
    c.close()
    return {"focus": [
        {"id": r["id"], "name": r["name"], "mastery": r["mastery"],
         "source": r["source"], "seen": r["seen"], "correct": r["correct"]}
        for r in rows], "states": store.MASTERY}


@app.get("/api/ledger")
def ledger():
    """Mastery state per concept. The page may show it; it never edits it."""
    c = con()
    rows = [dict(x) for x in c.execute(
        "SELECT id, name, mastery, seen, correct, next_due FROM concept ORDER BY id")]
    c.close()
    return {"concepts": rows, "states": store.MASTERY}


@app.get("/api/health")
def health():
    return {"ok": True, "db": str(DB), "exists": DB.exists()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8787, log_level="warning")
