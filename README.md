# positive-psychology

Agent Skills for Claude Code, built on positive psychology research. The
pattern this repo exists to show: a skill
doesn't have to be a prompt file. It can ship its own database, backend and
frontend, and Claude drives all three from chat.

---

# learn-optimism

Reads how optimistic you are from the way you explain real events. Then
trains it, by ear.

> *I always leave things too late.*
>
> *I left that one too late.*

Same missed deadline. The first sentence can never stop being true, the
second already has, and which one you reach for by habit is measurable. The
research calls it **explanatory style**: does the cause last, how far does
it spread, and is it you or the situation. You talk about real events in
chat. The skill finds the causal claim, stores it word for word, scores it,
and teaches you to hear the difference before it ever names a term.

## The app inside the skill

![The Optimism Map](docs/optimism-map.png)

One skill, three parts, one store:

| Part | Where | What it does |
|---|---|---|
| **Database** | SQLite, `~/.claude/state/optimism/` | Every statement you've made, the learning ledger, the one open drill. Survives sessions. |
| **Backend** | FastAPI, `localhost:8787` | Read-only API. Serves the derived reading: window, trend, finding. |
| **Frontend** | React, `localhost:5173` | The map above. Your reading in one sentence, one bar per dimension, what you're working on. |

How it works in practice:

1. You say `/learn-optimism`. The skill checks the store, brings both
   servers up with one idempotent script, and picks up exactly where the
   last session stopped, mid-drill if one was open.
2. You talk. Claude extracts and scores each causal statement through one
   CLI (`scripts/optimism_db.py`), which is the only thing that ever
   writes.
3. The map updates on refresh. Chat and the page read the same derived
   numbers from the same store, so they can't disagree, and the page has
   no buttons because it has nothing to write with.

## How the teaching works

- **Profile first.** Six setbacks and six wins, the instrument's own
  sample. Until then it only listens: no scores, no drills, no jargon.
- **Drills come from your own sentences.** Two spoken versions, one thing
  moved, one question you can answer on instinct. Nothing repeats; every
  prompt and sentence used is on record.
- **Names come last.** Hear the difference, point at it in your own words,
  say the event the other way, get caught doing it unprompted. Reading
  advances nothing. Misses demote.
- **The reading moves when you do.** A rolling window of your latest six
  per side, trended against the six before, so improvement shows instead
  of drowning in a lifetime average.
- **The voice is part of the design.** Quote-back questions the way Terry
  Gross asked them, drills the way Feynman showed a difference before
  naming it, pacing the way Wooden kept score, which was quietly.

## Install

```bash
git clone git@github.com:sirajfarhan/positive-psychology.git
cp -R positive-psychology/skills/learn-optimism ~/.claude/skills/
```

Copy it as a real directory, the skill scanner won't follow a link. Needs
`python3` and `node`; the venv and packages install themselves on first
run. Then say `/learn-optimism` in any session and it opens with one
question. Your data never enters the repo.

## Where it stops

It's not therapy, and it never scores your mood. Crisis content ends the
session and points at real help. The scoring is one uncalibrated rater:
trust the direction and the trend, not the absolute number.

## Layout

```
skills/learn-optimism/
  SKILL.md                      the route, the voice contract, the rules
  references/                   expression · learning loop · dimensions · principles
  scripts/optimism_db.py        the data layer, sole writer
  app/
    backend/                    FastAPI, read-only
    frontend/                   React, the map
    run.sh                      starts both, idempotent
```
