# positive-psychology

Agent Skills built on what positive psychology can actually measure. A skill
here isn't only a prompt file. It ships its own database, backend and
frontend, and Claude drives all three from the conversation.

---

# learn-optimism

Reads how optimistic you are from the way you explain real events. Then
trains it, by ear.

> *I always leave things too late.*
>
> *I left that one too late.*

Same missed deadline. The first sentence can never stop being true. The
second already has. Which one you reach for by habit is measurable. The research calls it
**explanatory style**, and it asks three things of a cause. Does it last. How
far does it spread. Is it you or the situation.

So you talk about real things in chat. The skill finds the causal claim in
what you said and stores it word for word. Then it scores it, and teaches you
to hear that difference before it ever names a term.

## The app inside the skill

![The Optimism Map](docs/optimism-map.png)

Three parts, one store.

| Part | Where | What it holds |
|---|---|---|
| **Database** | SQLite, outside the repo | Every statement you've made, the learning ledger, the one open drill |
| **Backend** | FastAPI on `:8787` | Read-only. Serves the reading: window, trend, finding |
| **Frontend** | React on `:5173` | The map above. Your reading in a sentence, a bar per dimension, what you're working on |

A session runs like this. You say `/learn-optimism`, and the skill reads the
store and starts the page if it isn't already up. It picks up where the last
session stopped, mid-drill if one was open. Then you talk.

Chat is the only thing that ever writes. The page refreshes itself every few
seconds, so your progress moves while you're still talking.

Chat and the page read the same derived numbers from the same store, so the
two can't disagree. The page has no buttons because it has nothing to write
with.

## How the teaching works

**It gathers before it teaches.** Six setbacks and six wins, which is the
sample the instrument itself uses. Until then it only listens. No scores, no
drills, no vocabulary.

**Drills come from your own sentences.** Yours is one version. The other is
written to move exactly one thing, and the question is answerable on
instinct. Nothing repeats, because every prompt asked and every sentence used
is on record.

**Names come last.** First you hear the difference. Then you point at it in
your own words. Then you say the event the other way. Last rung is getting
caught doing it unprompted, in ordinary talk. Reading about it advances
nothing, and misses cost a rung.

**Questions open up as you climb.** A skill gets exactly one two-way pick,
its first. After that the questions go open, because a pick you can answer
from the words alone tests reading rather than your ear. A miss brings the
pick back.

**Your own answers become tomorrow's material.** When you re-explain an event
during a drill, that sentence is stored as practice. It joins the pool drills
draw from, and it never touches the reading, because a sentence you were
coached into isn't evidence of how you naturally talk.

**The reading moves when you do.** It's a rolling window of your latest six
per side, trended against the six before. Improvement shows instead of
drowning in a lifetime average.

## What the code enforces

Prose kept losing arguments to habit here, so the rules that mattered moved
into the script.

It won't ask you a two-way question once you're past the first one, and it
says why when it refuses. It won't accept a score off the scale, or a growth
score on a win, because there's nothing to grow from in a win. One drill can
be open at a time, and that's structural rather than remembered. A sentence
you were coached into can't leak into the reading.

## Install

It's a plugin marketplace, so Claude Code can install it:

```
/plugin marketplace add sirajfarhan/positive-psychology
/plugin install positive-psychology@positive-psychology
```

Codex and the other Agent Plugins 1.0 clients read the same tree. The plugin
carries both manifests, and both specs discover skills the same way, as
immediate child directories of `skills/` holding a `SKILL.md`.

To take one skill on its own:

```bash
git clone git@github.com:sirajfarhan/positive-psychology.git
cp -R positive-psychology/plugins/positive-psychology/skills/learn-optimism \
      ~/.claude/skills/
```

Copy it as a real directory, since the skill scanner won't follow a link.
Needs `python3` and `node`, and the venv and packages install themselves on
first run. Then say `/learn-optimism` in any session and it opens with one
question.

## Upgrading

Pull a newer version and your history comes with it. The store updates itself
on the next run, keeps a dated backup of the old file, and says one line about
what it did. Nothing you've said is lost, however old the version you're
coming from.

## Where it stops

It's not therapy, and it never scores your mood. When something heavier than
an explanation comes up, it stops, says so, and points at real help instead
of scoring or arguing with it.

## What it can't do

The scoring is one automated rater working from anchors written for this
skill. There's no inter-rater reliability behind it and no population norms.
Trust three things: the direction, the gap between how you tell setbacks and
how you tell wins, and the trend against your own history. Don't trust the
absolute number, and don't compare it to anyone.

## Layout

```
.claude-plugin/marketplace.json        the catalogue Claude Code reads
plugins/positive-psychology/
  .claude-plugin/plugin.json           Claude Code manifest
  plugin.json                          Agent Plugins 1.0, for Codex and the rest
  skills/
    learn-optimism/
      SKILL.md                         the route, the voice, the rules
      references/                      expression, learning loop, dimensions, principles
      scripts/optimism_db.py           the data layer, the only writer
      scripts/migrations.py            keeps old stores working
      app/backend/                     FastAPI, read-only
      app/frontend/                    React, the map
      app/run.sh                       starts the page, safe to re-run
scripts/sync.sh                        live copy back into the repo
```

Another skill drops in beside `learn-optimism/`. Neither manifest needs
touching, and both ecosystems find it.
