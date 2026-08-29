#!/usr/bin/env python3
"""Store and read the optimism ledger.

One SQLite file holds both halves of the system:

  explanation  the scored causal statements  (the reading)
  concept      the learner ledger            (the learning)
  attempt      every performance, kept       (the evidence)

Scores are stored RAW, on the CAVE 1-7 convention:

    7 = permanent / general / personal
    1 = temporary / specific / situational

Orientation to pessimistic-optimistic is a read concern, not a storage
concern, because the optimistic pole depends on the event's valence:

    oriented = (raw - 4) * (+1 if valence == 'good' else -1)

Positive oriented values are always the optimistic direction. That is what
the display shows and what the composite averages.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import migrations

# Where the corpus lives.
#
# The store is the user's, not the client's, so it sits in the place that
# platform's own conventions put user data -- outside every plugin folder, so
# Claude Code, Codex and anything else that can run this script read and write
# one file. Installing, updating or removing a plugin never touches it.
#
# The resolution order below is the one platformdirs, appdirs and Rust's dirs
# crate all implement, which is why it is worth matching exactly rather than
# inventing something:
#
#   1. OPTIMISM_DB          an explicit answer beats every guess. Tests use it.
#   2. XDG_DATA_HOME        honoured on every platform when it is set, because
#                           someone who sets it has said where they want data.
#   3. the platform default
#        macOS    ~/Library/Application Support/positive-psychology
#        Windows  %LOCALAPPDATA%\positive-psychology
#        else     ~/.local/share/positive-psychology   (XDG default)
#
# Anything that has ever been a default stays in LEGACY_DBS so an existing
# store is carried forward instead of being abandoned next to a new empty one.

APP_DIR = "positive-psychology"
DB_NAME = "optimism.db"


def data_home() -> Path:
    """The platform's directory for user data, per the XDG/Apple/MS conventions."""
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if local:
            return Path(local)
    return Path.home() / ".local" / "share"


def cache_home() -> Path:
    """The platform's directory for regenerable files.

    The venv and node_modules go here rather than beside the store, because
    they are large and can always be rebuilt, while the store cannot.

    On macOS it also drops "Application Support" from the venv path, and with
    it one guaranteed space. That is a smaller win than it looks: a home
    directory can contain a space too, so run.sh installs with `python -m pip`
    rather than `bin/pip`, which is what actually makes the venv safe there.
    """
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches"
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if local:
            return Path(local) / "Cache"
    return Path.home() / ".cache"


def platform_db() -> Path:
    """Where the store goes when nobody has said otherwise."""
    return data_home() / APP_DIR / DB_NAME


def _default_db() -> Path:
    override = os.environ.get("OPTIMISM_DB")
    if override:
        # resolve(): a relative OPTIMISM_DB would otherwise mean a different
        # file depending on which directory the caller happened to be in
        return Path(override).expanduser().resolve()
    return platform_db()


DEFAULT_DB = _default_db()

# Every location this store has ever defaulted to, oldest last. Order is only
# a tiebreak; in practice at most one of these exists.
LEGACY_DBS = [
    Path.home() / ".local" / "share" / APP_DIR / DB_NAME,
    Path.home() / ".claude" / "state" / "optimism" / DB_NAME,
]


def adopt_legacy_store(path: Path) -> Path | None:
    """Move a store left at an older location, once, rather than orphan it.

    Someone who used this before the path was tool-neutral has real sentences
    at the old address. Starting a fresh empty store beside them would lose
    the history silently, which is the failure worth the extra code.
    """
    # Adopt only into the path this script would have picked on its own.
    #
    # Checking "was OPTIMISM_DB set" is not the same question, and getting it
    # wrong is expensive: a caller who says --db /tmp/scratch.db is asking to
    # look somewhere else, and moving their real store into a scratch file
    # because they asked is the worst thing this script could do. Comparing
    # against platform_db() covers --db and OPTIMISM_DB in one test, and still
    # adopts correctly when an override happens to name the real location.
    if path != platform_db() or path.exists():
        return None

    found = [old for old in LEGACY_DBS
             if old.exists() and old.stat().st_size > 0]
    if not found:
        return None

    old, rest = found[0], found[1:]
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(old), str(path))
    for extra in old.parent.glob(f"{old.stem}.*.bak"):
        shutil.move(str(extra), str(path.parent / extra.name))
    print(f"moved your store from {old} to {path}", file=sys.stderr)

    # Say so when a second one exists. Adoption never runs again once the
    # destination is there, so anything left behind is invisible from here on,
    # and silence would read as "there was only ever one".
    for other in rest:
        print(f"note: another store is still at {other}. Nothing was taken "
              f"from it. To use that one instead, move it to {path} while "
              f"{path.name} is not there.", file=sys.stderr)
    return old

# id, name, what a performance looks like, source, kind
#   kind 'dimension' -> scored 1-7, drives the chart
#   kind 'principle' -> taught and tracked, never charted
CONCEPTS = [
    # --- the scored dimensions (Seligman) ---
    ("perm-bad", "a setback: over, or still running",
     "hears whether a setback's cause is described as lasting or as over",
     "seligman", "dimension"),
    ("perm-good", "a win: still going, or a one-off",
     "hears whether a win's cause is described as lasting or as a one-off",
     "seligman", "dimension"),
    ("perv-bad", "a setback: one corner, or everywhere",
     "hears whether a setback's cause is described as general or as contained",
     "seligman", "dimension"),
    ("perv-good", "a win: everywhere, or one night",
     "hears whether a win's cause is described as general or as contained",
     "seligman", "dimension"),
    ("pers-bad", "a setback: what you did, or what you are",
     "separates naming your specific part from declaring yourself defective",
     "seligman", "dimension"),
    ("pers-good", "a win: your doing, or luck",
     "hears whether a win is credited to you or to circumstances",
     "seligman", "dimension"),

    # --- structural (Seligman) ---
    ("inversion", "wins and setbacks, told in opposite directions",
     "knows the optimistic pole depends on whether the event was good or bad",
     "seligman", "principle"),
    ("dispute", "arguing back at yourself",
     "argues against a pessimistic explanation the way they would for a friend",
     "seligman", "principle"),

    # --- the principles from the book ---
    ("accept", "accepting the fact itself",
     "states what happened without protesting that it happened",
     "sage", "principle"),
    ("compare", "the hidden yardstick",
     "spots the imagined alternative a sentence is measuring against, and can "
     "choose a different one on purpose",
     "sage", "principle"),
    ("agency", "the move that's still yours",
     "names a move that is theirs to make, without forcing and without waiting",
     "sage", "principle"),
    ("question", "which question you're asking yourself",
     "notices which question they are putting to themselves, and asks a better one",
     "sage", "principle"),
    ("weight", "how much it was made to matter",
     "notices the importance assigned to something, and whether the reaction "
     "matches the actual stake",
     "sage", "principle"),
    ("seed", "what the setback built",
     "states what a setback produced or taught, without erasing the cost",
     "sage", "principle"),
]

# The ladder. Each state is reached only by performing at it.
# Reading about a concept never moves it past 'new'.
MASTERY = ["new", "discriminate", "detect", "produce", "live"]

DIMENSIONS = ("permanence", "pervasiveness", "personalization", "builds")

# The ASQ presents 12 hypothetical events, half good and half bad, one causal
# statement each. That is the instrument's own sample size, so it is ours: below
# it there is no profile, only noise, and nothing should be taught off it.
# Balance matters as much as the total -- eight setbacks and no wins leaves the
# composite half-blind, because the good-event poles are never observed.
NEED_PER_VALENCE = 6

# Attributions vary by domain -- work-related and interpersonal styles can
# diverge -- and domain-specific ASQ variants exist for exactly that reason. A
# corpus drawn entirely from one domain trains an ear that may not carry to the
# others, so the spread is reported even though it does not gate anything.
DOMAINS = ("work", "relationships", "health", "money", "self", "other")

LEGACY_SCHEMA_UNUSED = """
CREATE TABLE IF NOT EXISTS explanation (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at     TEXT    NOT NULL,
    event           TEXT    NOT NULL,
    valence         TEXT    NOT NULL CHECK (valence IN ('good','bad')),
    quote           TEXT    NOT NULL,
    kind            TEXT    NOT NULL DEFAULT 'event'
                    CHECK (kind IN ('event','practice')),
    domain          TEXT,
    permanence      REAL,
    pervasiveness   REAL,
    personalization REAL,
    builds          REAL,
    note            TEXT
);

CREATE TABLE IF NOT EXISTS concept (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    performance   TEXT NOT NULL,
    source        TEXT NOT NULL DEFAULT 'seligman',
    kind          TEXT NOT NULL DEFAULT 'principle',
    mastery       TEXT NOT NULL DEFAULT 'new',
    seen          INTEGER NOT NULL DEFAULT 0,
    correct       INTEGER NOT NULL DEFAULT 0,
    last_seen     TEXT,
    next_due      TEXT,
    interval_days REAL NOT NULL DEFAULT 0,
    ease          REAL NOT NULL DEFAULT 2.3
);

CREATE TABLE IF NOT EXISTS attempt (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_id     TEXT NOT NULL REFERENCES concept(id),
    at             TEXT NOT NULL,
    stage          TEXT NOT NULL,
    result         TEXT NOT NULL CHECK (result IN ('correct','partial','incorrect')),
    prompt         TEXT,
    evidence       TEXT,
    explanation_id INTEGER REFERENCES explanation(id)
);

-- at most one drill may be open at a time, which is the one-concept-per-turn
-- rule made structural rather than remembered
CREATE TABLE IF NOT EXISTS pending (
    id             INTEGER PRIMARY KEY CHECK (id = 1),
    concept_id     TEXT NOT NULL REFERENCES concept(id),
    prompt         TEXT NOT NULL,
    explanation_id INTEGER REFERENCES explanation(id),
    asked_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_expl_valence ON explanation(valence);
CREATE INDEX IF NOT EXISTS idx_attempt_concept ON attempt(concept_id);
CREATE INDEX IF NOT EXISTS idx_expl_captured ON explanation(captured_at);
"""


def now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def connect(path: Path) -> sqlite3.Connection:
    adopt_legacy_store(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init(con: sqlite3.Connection, path: Path | None = None) -> dict:
    """Bring the store up to date, then seed the concept rows.

    Schema shape is the migration runner's job now. This keeps only the seed,
    which is data rather than structure, and is safe to re-run.
    """
    report = migrations.migrate(con, path)
    for cid, name, performance, source, kind in CONCEPTS:
        con.execute(
            """INSERT INTO concept (id, name, performance, source, kind)
               VALUES (?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name, performance=excluded.performance,
                 source=excluded.source, kind=excluded.kind""",
            (cid, name, performance, source, kind),
        )
    con.commit()
    return report


def orient(raw: float | None, valence: str, dim: str = "permanence") -> float | None:
    """Raw score -> signed distance from neutral, + is always optimistic.

    The three CAVE dimensions flip: a permanent *setback* is pessimistic, a
    permanent *win* is optimistic. Growth does not flip -- 7 always means more
    was built -- and it is only ever scored on setbacks anyway.
    """
    if raw is None:
        return None
    if dim == "builds":
        return raw - 4.0
    # + 0.0 normalises the -0.0 that 0.0 * -1.0 produces
    return (raw - 4.0) * (1.0 if valence == "good" else -1.0) + 0.0


# --------------------------------------------------------------------------
# recording explanations
# --------------------------------------------------------------------------

def add_explanation(con, event, valence, quote, scores, note=None,
                    domain=None, kind="event") -> int:
    if kind not in ("event", "practice"):
        raise SystemExit("kind must be event or practice")
    if domain is not None and domain not in DOMAINS:
        raise SystemExit(f"domain must be one of: {', '.join(DOMAINS)}")
    # growth is only scoreable on setbacks; refuse it loudly rather than
    # storing a value that reading() would silently drop
    if valence == "good" and scores.get("builds") is not None:
        raise SystemExit("builds is scored only on setbacks - there is nothing "
                         "to grow from in a win")
    for dim, raw in scores.items():
        if raw is not None and not (1 <= raw <= 7):
            raise SystemExit(f"{dim}={raw} is outside the 1-7 scale")
    cur = con.execute(
        """INSERT INTO explanation
           (captured_at, event, valence, quote, kind, domain,
            permanence, pervasiveness, personalization, builds, note)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (iso(now()), event, valence, quote, kind, domain,
         scores.get("permanence"), scores.get("pervasiveness"),
         scores.get("personalization"), scores.get("builds"), note),
    )
    con.commit()
    return cur.lastrowid


def readiness(con) -> dict:
    """How close the store is to a profile worth reading."""
    counts = {"bad": 0, "good": 0}
    for r in con.execute(
            "SELECT valence, COUNT(*) c FROM explanation WHERE kind='event' GROUP BY valence"):
        counts[r["valence"]] = r["c"]
    need = NEED_PER_VALENCE
    return {
        "ready": counts["bad"] >= need and counts["good"] >= need,
        "bad": {"have": counts["bad"], "need": need},
        "good": {"have": counts["good"], "need": need},
        "total": {"have": counts["bad"] + counts["good"], "need": need * 2},
    }


def profile(con) -> dict:
    """Everything the teaching needs to know about the person.

    Not a personality inventory. Direct tests of moderation mostly fail -- the
    Twins Wellbeing study tested fifteen baseline characteristics and none
    predicted response during the intervention -- so goals, values, strengths
    and wellbeing baselines are deliberately absent. What is here is only what
    the drill machinery actually consumes.
    """
    ready = readiness(con)

    spread = {}
    for r in con.execute(
            """SELECT COALESCE(domain,'untagged') d, valence, COUNT(*) c
               FROM explanation GROUP BY d, valence"""):
        spread.setdefault(r["d"], {"bad": 0, "good": 0})[r["valence"]] = r["c"]

    # which dimension leans most pessimistic RIGHT NOW -- same window the
    # reading uses, so teaching tracks current behaviour. Lifetime leans would
    # keep drilling a dimension the learner has already moved.
    live = []
    for valence in ("bad", "good"):
        recent = window(con, valence)
        for dim in ("permanence", "pervasiveness", "personalization"):
            vals = [orient(r[dim], valence, dim) for r in recent
                    if r[dim] is not None]
            if vals:
                live.append({"dimension": dim, "valence": valence,
                             "lean": round(sum(vals) / len(vals), 2), "n": len(vals)})
    live.sort(key=lambda x: x["lean"])

    # their own words, for writing pair counterparts that sound like them
    register = [dict(r) for r in con.execute(
        "SELECT quote, valence, domain, kind FROM explanation "
        "ORDER BY captured_at DESC, id DESC LIMIT 6")]

    return {
        "readiness": ready,
        "phase": "profile" if not ready["ready"] else "teaching",
        "domains": spread,
        "domains_covered": len([d for d in spread if d != "untagged"]),
        "live_dimensions": live[:3],
        "register": register,
    }


def window(con, valence: str, offset: int = 0) -> list:
    """The most recent NEED_PER_VALENCE statements of one valence.

    The reading uses a window, not all history, because explanatory style is
    trainable -- a lifetime average buries the change you are training for. The
    window size is the instrument's own half-sample rather than a number I
    picked. offset=NEED_PER_VALENCE gives the preceding window, for the trend.
    """
    return con.execute(
        """SELECT * FROM explanation WHERE valence = ? AND kind = 'event'
           ORDER BY captured_at DESC, id DESC LIMIT ? OFFSET ?""",
        (valence, NEED_PER_VALENCE, offset)).fetchall()


def score_block(rows: list, valence: str) -> tuple[dict, list]:
    """Mean per dimension for one set of rows, plus the values that composite."""
    block: dict = {"n": len(rows)}
    values: list[float] = []
    for dim in DIMENSIONS:
        if dim == "builds" and valence == "good":
            continue  # growth only applies to setbacks
        scored = [orient(r[dim], valence, dim) for r in rows if r[dim] is not None]
        if scored:
            mean = sum(scored) / len(scored)
            block[dim] = {"value": round(mean, 2), "n": len(scored)}
            # 'builds' is a different instrument: reported, never composited
            if dim != "builds":
                values.append(mean)
    return block, values


def composite(con, offset: int = 0) -> float | None:
    vals: list[float] = []
    for valence in ("bad", "good"):
        vals += score_block(window(con, valence, offset), valence)[1]
    return round(sum(vals) / len(vals), 2) if vals else None


def reading(con) -> dict:
    """The whole display state, in one object."""
    rows = con.execute("SELECT * FROM explanation WHERE kind='event'").fetchall()

    ready = readiness(con)
    out: dict = {"n": len(rows), "since": None, "bad": {}, "good": {},
                 "overall": None, "finding": "Nothing scored yet.",
                 "readiness": ready}
    if not rows:
        return out

    if not ready["ready"]:
        # below the instrument's own sample size there is no reading to give
        out["since"] = min(r["captured_at"] for r in rows)[:10]
        out["finding"] = "Still listening."
        return out

    values: list[float] = []
    used: list = []
    for valence in ("bad", "good"):
        w = window(con, valence)
        used += w
        block, vals = score_block(w, valence)
        values += vals
        out[valence] = block
    out["since"] = min(r["captured_at"] for r in used)[:10]
    out["window"] = len(used)

    if values:
        out["overall"] = round(sum(values) / len(values), 2)

    # trend: this window against the one before it, same size, same method,
    # and only when the one before it exists in full. A real page once said
    # "up 20% since the 12 before these" while the previous window held a
    # single sentence: the arithmetic ran on whatever was there, and the
    # label lied about the sample.
    prev_full = all(
        len(window(con, v, offset=NEED_PER_VALENCE)) == NEED_PER_VALENCE
        for v in ("bad", "good"))
    prev = composite(con, offset=NEED_PER_VALENCE) if prev_full else None
    out["trend"] = (None if prev is None or out["overall"] is None
                    else round(out["overall"] - prev, 2))
    out["previous"] = prev

    out["finding"] = finding(out)
    return out


# how far from neutral a side has to lean before it is worth naming
LEAN = 0.4

# (positive phrasing, negative phrasing) as clause fragments
PHRASING = {
    "bad":  ("handle setbacks well", "take setbacks harder than you need to"),
    "good": ("own your wins", "give away your wins"),
}


def finding(r: dict) -> str:
    """The one sentence, derived here so the page and chat cannot disagree.

    Each side is read on its own and the two are joined. A strong lean on one
    side is still a finding when the other side is flat -- requiring both would
    bury exactly the lopsided patterns worth naming.
    """
    leans: list[tuple[str, bool]] = []
    for valence in ("bad", "good"):
        block = r.get(valence) or {}
        core = [block[d]["value"] for d in
                ("permanence", "pervasiveness", "personalization") if d in block]
        if not core:
            continue
        mean = sum(core) / len(core)
        if abs(mean) <= LEAN:
            continue
        up, down = PHRASING[valence]
        leans.append((up if mean > 0 else down, mean > 0))

    if not leans:
        return "No strong lean either way yet."
    if len(leans) == 1:
        return f"You {leans[0][0]}."
    # 'but' when the two sides disagree -- the contrast is the whole finding
    joiner = "and" if leans[0][1] == leans[1][1] else "but"
    return f"You {leans[0][0]} {joiner} {leans[1][0]}."


# --------------------------------------------------------------------------
# the ledger
# --------------------------------------------------------------------------

def advance(current: str, result: str) -> str:
    i = MASTERY.index(current) if current in MASTERY else 0
    if result == "correct":
        return MASTERY[min(i + 1, len(MASTERY) - 1)]
    if result == "partial":
        return MASTERY[max(i, 1)]
    # Wrong answers cost a rung, down to `discriminate`. The bottom two states
    # never demote: `new` means never drilled, and history does not un-happen.
    # A miss there lands on the schedule instead -- the interval collapses to
    # about thirty minutes and ease drops.
    return MASTERY[max(1, i - 1)] if i > 1 else "discriminate" if i == 1 else "new"


def reschedule(row: sqlite3.Row, result: str) -> tuple[float, float]:
    ease = float(row["ease"])
    interval = float(row["interval_days"])
    if result == "correct":
        interval = 1.0 if interval < 1 else min(interval * ease, 60.0)
        ease = min(ease + 0.12, 3.0)
    elif result == "partial":
        interval = 0.25 if interval < 1 else max(1.0, interval * 0.6)
        ease = max(ease - 0.08, 1.4)
    else:
        interval = 0.02  # ~30 minutes
        ease = max(ease - 0.2, 1.3)
    return round(interval, 3), round(ease, 3)


# Picks are retired: every question is open, always. These markers exist so
# ask() can catch a prompt that still reads like a pick and refuse it, and
# --allow-pick is a manual escape hatch for the rare constructed fallback,
# not a scheduled return.
PICK_MARKERS = ("1 or 2", "2 or 1", "a or b", "which of those",
                "which of these", "which one", "which version", "either")


def looks_like_pick(prompt: str) -> bool:
    return any(m in prompt.lower() for m in PICK_MARKERS)


def required_form(con, concept_id: str) -> str:
    """Every question is open, always.

    Two-way picks used to be required for a concept's first question. They
    were retired: a pick yields one bit and teaches the learner to
    pattern-match the phrasing, while an open answer yields a sentence,
    which is at once the evidence for grading, tomorrow's drill material,
    and the only thing the instrument can actually score.
    """
    return "open"


def ask(con, concept_id: str, prompt: str, explanation_id: int | None = None,
        allow_pick: bool = False) -> dict:
    """Open a drill. Replaces any drill left open, since only one may run."""
    if con.execute("SELECT 1 FROM concept WHERE id = ?", (concept_id,)).fetchone() is None:
        raise SystemExit(f"unknown concept: {concept_id}")
    form = required_form(con, concept_id)
    if looks_like_pick(prompt) and not allow_pick:
        raise SystemExit(
            f"this reads as a two-way pick, and every question here is open.\n"
            f"A pick yields one bit and gets pattern-matched; an open answer "
            f"yields a sentence,\nwhich is the evidence, the material and the "
            f"scoreable thing all at once.\nRun one movie from their event and "
            f"leave the answer slot visible: what changes\nfirst, where does it "
            f"show up, what got you there.\n"
            f"(--allow-pick overrides this, for the rare constructed fallback "
            f"only.)")
    t = iso(now())
    con.execute(
        """INSERT INTO pending (id, concept_id, prompt, explanation_id, asked_at)
           VALUES (1,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET
             concept_id=excluded.concept_id, prompt=excluded.prompt,
             explanation_id=excluded.explanation_id, asked_at=excluded.asked_at""",
        (concept_id, prompt, explanation_id, t))
    con.commit()
    return {"open": concept_id, "asked_at": t, "form": form}


STOPWORDS = frozenset("""a an and are as at be because but by for from had has
have he her his i im it its me my not of on or our she so that the their them
they this to was we were what when which who will with you your just like feel
feels felt more much very really""".split())


def corpus(con) -> dict:
    """Every stored sentence, plus the words that keep coming back.

    Whole-file questioning starts here: a drill built on one event at a time
    never notices that "without money" is explaining a win and a setback in
    the same week. The repeats list is deliberately dumb, content words
    appearing in two or more event quotes, because the reading of what a
    repeat means belongs to the caller, not to string matching.
    """
    rows = [dict(r) for r in con.execute(
        """SELECT id, captured_at, event, valence, domain, kind, quote
           FROM explanation ORDER BY captured_at, id""")]
    seen: dict[str, set] = {}
    for r in rows:
        if r["kind"] != "event":
            continue
        words = {w.strip(".,;:!?\"'()").lower()
                 for w in r["quote"].split()}
        for w in words:
            if len(w) > 3 and w not in STOPWORDS:
                seen.setdefault(w, set()).add(r["id"])
    repeats = {w: sorted(ids) for w, ids in sorted(
        seen.items(), key=lambda kv: (-len(kv[1]), kv[0])) if len(ids) > 1}
    return {"n": len(rows), "explanations": rows, "repeats": repeats}


def pending(con) -> dict | None:
    r = con.execute(
        """SELECT p.*, c.name, c.mastery, e.quote
           FROM pending p JOIN concept c ON c.id = p.concept_id
           LEFT JOIN explanation e ON e.id = p.explanation_id
           WHERE p.id = 1""").fetchone()
    return dict(r) if r else None


def resume(con) -> dict:
    """Where things stand. Call this first, every invocation.

    One call answers: is there a profile yet, is a drill still open from last
    time, what is due, and what is being worked on. Nothing about the learner's
    position lives in conversation memory.
    """
    r = readiness(con)
    return {
        "readiness": r,
        "phase": "profile" if not r["ready"] else "teaching",
        "open_drill": pending(con),
        "due": due(con, 3),
        "focus": focus(con),
        "profile": profile(con),
        "finding": reading(con)["finding"],
    }


def _require_concept(con, concept_id: str) -> None:
    """One answer for a bad id, so a typo cannot read as 'nothing here'."""
    if con.execute("SELECT 1 FROM concept WHERE id = ?",
                   (concept_id,)).fetchone() is None:
        raise SystemExit(f"unknown concept: {concept_id}")


def asked(con, concept_id: str) -> dict:
    """What has already been put to the learner for this concept.

    Drills have to stay novel, so before composing one, check this: the prompts
    already used, and the explanations already drilled on.
    """
    _require_concept(con, concept_id)
    rows = con.execute(
        """SELECT a.at, a.stage, a.result, a.prompt, a.explanation_id, e.quote
           FROM attempt a LEFT JOIN explanation e ON e.id = a.explanation_id
           WHERE a.concept_id = ? ORDER BY a.at DESC, a.id DESC""", (concept_id,)).fetchall()
    return {
        "concept": concept_id,
        "attempts": [dict(r) for r in rows],
        "prompts_used": [r["prompt"] for r in rows if r["prompt"]],
        "explanations_used": sorted({r["explanation_id"] for r in rows
                                     if r["explanation_id"] is not None}),
    }


def unused_explanations(con, concept_id: str, limit: int = 5) -> list[dict]:
    """Stored sentences this concept has not been drilled on yet.

    A *-good concept only ever drills on wins and a *-bad concept only on
    setbacks, so the wrong valence is filtered out here rather than trusted
    to the caller.
    """
    _require_concept(con, concept_id)
    limit = max(1, limit)  # SQLite reads a negative LIMIT as unbounded
    valence = ("good" if concept_id.endswith("-good")
               else "bad" if concept_id.endswith("-bad") else None)
    q = """SELECT id, captured_at, event, valence, quote FROM explanation
           WHERE id NOT IN (SELECT explanation_id FROM attempt
                            WHERE concept_id = ? AND explanation_id IS NOT NULL)"""
    args: list = [concept_id]
    if valence:
        q += " AND valence = ?"
        args.append(valence)
    q += " ORDER BY captured_at DESC, id DESC LIMIT ?"
    args.append(limit)
    return [dict(r) for r in con.execute(q, args)]


def record(con, concept_id: str, result: str, evidence: str | None = None,
           prompt: str | None = None, explanation_id: int | None = None) -> dict:
    row = con.execute("SELECT * FROM concept WHERE id = ?", (concept_id,)).fetchone()
    if row is None:
        raise SystemExit(f"unknown concept: {concept_id}")

    stage = row["mastery"]
    interval, ease = reschedule(row, result)
    t = now()
    mastery = advance(stage, result)

    con.execute(
        """UPDATE concept SET mastery=?, seen=seen+1, correct=correct+?,
           last_seen=?, next_due=?, interval_days=?, ease=? WHERE id=?""",
        (mastery, 1 if result == "correct" else 0, iso(t),
         iso(t + timedelta(days=interval)), interval, ease, concept_id),
    )
    con.execute(
        """INSERT INTO attempt (concept_id, at, stage, result, prompt, evidence,
                                explanation_id)
           VALUES (?,?,?,?,?,?,?)""",
        (concept_id, iso(t), stage, result, prompt, evidence, explanation_id),
    )
    # Resolve the open drill only if THIS concept is the one that was asked.
    # Recording another concept -- say, live-stage evidence the learner just
    # produced unprompted -- must not destroy an unrelated unanswered drill.
    con.execute("DELETE FROM pending WHERE id = 1 AND concept_id = ?", (concept_id,))
    con.commit()
    return {"concept": concept_id, "was": stage, "now": mastery,
            "next_due": iso(t + timedelta(days=interval)), "ease": ease}


DIM_CONCEPT = {("permanence", "bad"): "perm-bad", ("permanence", "good"): "perm-good",
               ("pervasiveness", "bad"): "perv-bad", ("pervasiveness", "good"): "perv-good",
               ("personalization", "bad"): "pers-bad", ("personalization", "good"): "pers-good"}


def due(con, limit: int = 3) -> list[dict]:
    """What to drill next, worst-first.

    Ties among equally-due concepts are broken by the current window's lean,
    most pessimistic first, so the first row returned is the right one to
    take. Insertion order used to break these ties, which permanently hid the
    back half of the dimensions behind the front half at any small limit.
    Concepts without a lean (the principles, or dimensions with no data yet)
    follow the ranked dimensions.
    """
    limit = max(1, limit)  # SQLite reads a negative LIMIT as unbounded
    t = iso(now())
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM concept WHERE next_due IS NULL OR next_due <= ?", (t,))]

    leans = {}
    for item in profile(con)["live_dimensions"]:
        cid = DIM_CONCEPT.get((item["dimension"], item["valence"]))
        if cid:
            leans[cid] = item["lean"]

    def rank(r):
        return (MASTERY.index(r["mastery"]) if r["mastery"] in MASTERY else 0,
                leans.get(r["id"], float("inf")),
                r["next_due"] is not None, r["next_due"] or "", r["id"])

    rows.sort(key=rank)
    out = rows[:limit]
    for r in out:
        r["form"] = required_form(con, r["id"])
    return out


def focus(con, limit: int = 4) -> list[dict]:
    """What the learner is currently being tested on.

    Only concepts they have actually been drilled on and have not finished.
    A concept at 'new' has never been put to them, and one at 'live' is done --
    neither is under test, so neither belongs on the page.
    """
    limit = max(1, limit)  # SQLite reads a negative LIMIT as unbounded
    rows = con.execute(
        """SELECT id, name, performance, source, kind, mastery, seen, correct, next_due
           FROM concept
           WHERE seen > 0 AND mastery != 'live'
           ORDER BY next_due IS NULL, next_due
           LIMIT ?""", (limit,)).fetchall()
    return [dict(r) for r in rows]


def summary(con) -> dict:
    counts = {m: 0 for m in MASTERY}
    for r in con.execute("SELECT mastery, COUNT(*) c FROM concept GROUP BY mastery"):
        counts[r["mastery"]] = r["c"]
    return {"mastery": counts, "focus": focus(con), "reading": reading(con)}


# --------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    sub.add_parser("where")
    sub.add_parser("reading")
    sub.add_parser("readiness")
    sub.add_parser("migrate")
    sub.add_parser("profile")
    sub.add_parser("summary")

    d = sub.add_parser("due")
    d.add_argument("--limit", type=int, default=3)

    fo = sub.add_parser("focus")
    fo.add_argument("--limit", type=int, default=4)

    a = sub.add_parser("add")
    a.add_argument("--event", required=True, help="what happened, facts only")
    a.add_argument("--valence", required=True, choices=["good", "bad"])
    a.add_argument("--quote", required=True,
                   help="the causal statement, VERBATIM -- their words, not tidied")
    a.add_argument("--domain", choices=list(DOMAINS))
    a.add_argument("--kind", choices=["event", "practice"], default="event",
                   help="practice = their re-explanation during a drill; "
                        "drill material forever, never in the reading")
    a.add_argument("--permanence", type=float)
    a.add_argument("--pervasiveness", type=float)
    a.add_argument("--personalization", type=float)
    a.add_argument("--builds", type=float)
    a.add_argument("--note")

    r = sub.add_parser("record")
    r.add_argument("concept")
    r.add_argument("--result", required=True, choices=["correct", "partial", "incorrect"])
    r.add_argument("--evidence", help="what the learner actually said")
    r.add_argument("--prompt", help="the drill you gave, so it is not repeated")
    r.add_argument("--explanation", type=int, help="id of the sentence drilled on")

    sub.add_parser("resume")
    sub.add_parser("corpus")
    sub.add_parser("pending")

    ask_p = sub.add_parser("ask")
    ask_p.add_argument("concept")
    ask_p.add_argument("--prompt", required=True)
    ask_p.add_argument("--explanation", type=int)
    ask_p.add_argument("--allow-pick", action="store_true",
                       help="escape hatch for the rare constructed fallback; every question is open otherwise")

    ak = sub.add_parser("asked")
    ak.add_argument("concept")

    un = sub.add_parser("unused")
    un.add_argument("concept")
    un.add_argument("--limit", type=int, default=5)

    args = p.parse_args()

    if args.cmd == "where":
        # Answered before opening anything, so asking where the store is never
        # brings one into existence. run.sh reads this instead of reimplementing
        # the resolution, so there is one answer and not two that can drift.
        print(json.dumps({
            "db": str(args.db),
            "dir": str(args.db.parent),
            "data_home": str(data_home()),
            "deps": str(cache_home() / APP_DIR / "deps"),
            "exists": args.db.exists(),
            "platform": sys.platform,
            "source": ("--db" if args.db != DEFAULT_DB
                       else "OPTIMISM_DB" if os.environ.get("OPTIMISM_DB")
                       else "XDG_DATA_HOME" if os.environ.get("XDG_DATA_HOME")
                       else "platform default"),
            "adoptable": args.db == platform_db() and not args.db.exists(),
        }, indent=2))
        return 0

    con = connect(args.db)
    report = init(con, args.db)
    if report["applied"] and args.cmd != "migrate":
        # stderr: stdout is JSON that callers parse
        print(f"store migrated v{report['from']} -> v{report['to']}",
              file=sys.stderr, flush=True)

    if args.cmd == "migrate":
        print(json.dumps({**report, "latest": migrations.LATEST,
                          "at": migrations.current_version(con)}, indent=2))
    elif args.cmd == "init":
        print(json.dumps({"db": str(args.db), "concepts": len(CONCEPTS),
                          "schema_version": migrations.current_version(con)}, indent=2))
    elif args.cmd == "profile":
        print(json.dumps(profile(con), indent=2))
    elif args.cmd == "readiness":
        print(json.dumps(readiness(con), indent=2))
    elif args.cmd == "reading":
        print(json.dumps(reading(con), indent=2))
    elif args.cmd == "summary":
        print(json.dumps(summary(con), indent=2))
    elif args.cmd == "focus":
        print(json.dumps(focus(con, args.limit), indent=2))
    elif args.cmd == "due":
        print(json.dumps(due(con, args.limit), indent=2))
    elif args.cmd == "add":
        scores = {k: getattr(args, k) for k in DIMENSIONS}
        eid = add_explanation(con, args.event, args.valence, args.quote, scores,
                              args.note, args.domain, args.kind)
        print(json.dumps({"id": eid, "oriented": {
            k: orient(v, args.valence, k) for k, v in scores.items() if v is not None}}, indent=2))
    elif args.cmd == "corpus":
        print(json.dumps(corpus(con), indent=2))
    elif args.cmd == "resume":
        print(json.dumps(resume(con), indent=2))
    elif args.cmd == "pending":
        print(json.dumps(pending(con), indent=2))
    elif args.cmd == "ask":
        print(json.dumps(ask(con, args.concept, args.prompt, args.explanation,
                             args.allow_pick), indent=2))
    elif args.cmd == "asked":
        print(json.dumps(asked(con, args.concept), indent=2))
    elif args.cmd == "unused":
        print(json.dumps(unused_explanations(con, args.concept, args.limit), indent=2))
    elif args.cmd == "record":
        print(json.dumps(record(con, args.concept, args.result, args.evidence,
                                args.prompt, args.explanation), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
