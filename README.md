# positive-psychology

Agent Skills for Claude Code and Codex, built on what positive psychology can
actually measure. A skill here isn't only a prompt file. It ships its own
database, backend and frontend, and Claude drives all three from the
conversation.

---

# learn-optimism

It reads how optimistic you are from the way you explain real events. Then it
teaches you to hear the difference yourself.

Here are two ways of explaining the same missed deadline.

> *I always leave things too late.*
>
> *I left that one too late.*

The first one can never stop being true, because "always" has no end in it.
The second one is already finished. Most people reach for one of those more
than the other without noticing, and that habit can be measured.
Psychologists call it explanatory style. They ask three things about a cause.
Does it last. How far does it reach. Is it you, or the situation.

So you talk about real things in chat. The skill finds the reason you gave
and stores that sentence word for word. Then it scores it, and starts
teaching you to hear that difference before it ever gives you a term for it.

## The app inside the skill

![The Optimism Map](docs/optimism-map.png)

Three parts, one shared file.

| Part | Where | What it holds |
|---|---|---|
| **Database** | SQLite, in a folder of your own, outside the plugin | Every sentence you've given it, what you've practised, and any question still waiting on you |
| **Backend** | FastAPI on `:8787` | Read-only. Hands over your current scores and how they've moved |
| **Frontend** | React on `:5173` | The page above. Your result in a sentence, a bar for each of the three questions, and what you're practising |

You say `/learn-optimism`, and it opens your file and starts the page if it
isn't already running. If a question was left unanswered last time, it comes
back before anything new starts.

Chat is the only thing that ever writes. The page refreshes itself every few
seconds, so what you're practising moves while you're still talking. Both sides
read the same numbers out of the same file, so they can't tell you different
things. The page has no buttons because it has nothing to write with.

## How the teaching works

**It listens before it teaches.** Six things that went wrong and six that
went right, which is the same number of examples the original test uses.
Until it has those, it only collects. No scores, no practice, no terms.

**Practice is built from your own sentences.** Yours is one version of the
event. It writes a second one that changes a single thing, and asks you
something you can answer on gut feel. It never repeats itself, because it
keeps every question it has asked and every sentence it has used.

**Terms come last.** First you notice the two sentences feel different. Then
you say what the difference is in your own words. Then you retell your own
event the other way. The last step is catching yourself doing it in normal
conversation, with nobody asking. Reading about any of this moves nothing,
and getting one wrong sets you back a step.

**Questions get harder as you go.** You get one question with two answers to
choose from, and it's always the first one on a given idea. After that they
open up, because a two-answer question can be solved from the wording alone,
and then it's testing your reading instead of your ear. Get one wrong and the
easy kind comes back.

**Your answers become tomorrow's material.** When you retell an event during
practice, that new sentence gets kept as practice. It joins the pool the
questions come from. It never counts toward your scores, because a sentence
you were talked into isn't evidence of how you talk on your own.

**Your scores move when you do.** They only look at your latest six of each
kind, compared against the six before those. Recent change shows up instead
of getting buried under a lifetime average.

## What the code enforces

Written rules kept getting ignored out of habit, so the ones that matter now
live in the code.

It won't give you a two-answer question once you're past the first one on an
idea, and it tells you why when it refuses. It won't take a score outside the
scale, or record growth on something that went well, because there's nothing
to grow from there. Only one question can be open at a time, and the code
blocks a second one rather than trusting anyone to remember. A sentence you
were talked into can't get into your scores.

## Install

The repo is a plugin marketplace, so Claude Code can install it directly:

```
/plugin marketplace add sirajfarhan/positive-psychology
/plugin install positive-psychology@positive-psychology
```

Codex and the other [Agent Plugins 1.0](https://agent-plugins.org) clients
read the same tree. The plugin ships one manifest for each of the two specs,
and both look for skills the same way, in folders sitting directly inside
`skills/` with a `SKILL.md` in them.

To take one skill on its own:

```bash
git clone git@github.com:sirajfarhan/positive-psychology.git
cp -R positive-psychology/plugins/positive-psychology/skills/learn-optimism \
      ~/.claude/skills/
```

Copy it as a real folder, since the skill scanner won't follow a link. You'll
need `python3` and `node`, and it installs its own dependencies the first
time it runs. Then say `/learn-optimism` in any session and it opens with one
question.

## Your file

It lives at `~/.local/share/positive-psychology/optimism.db`, which is nobody's
private corner. Claude and Codex read that same file, so it doesn't matter
which one you happen to be talking to, and installing or removing the plugin
doesn't reach it. Set `XDG_DATA_HOME` and it follows. If you'd used this
before it moved there, it brings your old file along the first time it runs.

Pull a newer version and your history comes with it. The file updates itself
the next time you run anything, keeps a dated copy of the old one, and says a
single line about what it did. Nothing you've told it is lost, however old the
version you're coming from.

## Where it stops

It isn't therapy, and it never scores how you feel. When something heavier
than an explanation comes up, it stops and says so. It points you at real help
instead of scoring it or arguing with it.

## What it can't do

One automated rater does the scoring, working from example sentences written
for this skill. Nobody has checked whether a second rater would agree, and
there's no baseline from other people to compare you against. Trust the
direction, the gap between how you tell the bad ones and how you tell the
good ones, and the change against your own history. Don't trust the number
itself, and don't compare it to anyone.

## Layout

```
.claude-plugin/marketplace.json        the catalogue Claude Code reads
plugins/positive-psychology/
  .claude-plugin/plugin.json           Claude Code manifest
  plugin.json                          Agent Plugins 1.0, for Codex and the rest
  skills/
    learn-optimism/
      SKILL.md                         what it does each turn, and how it talks
      references/                      the voice, the teaching, the scoring
      scripts/optimism_db.py           your file, and the only thing that writes
      scripts/migrations.py            keeps older files working
      app/backend/                     FastAPI, read-only
      app/frontend/                    React, the page
      app/run.sh                       starts it, safe to run twice
scripts/sync.sh                        copies the live skill back into the repo
```

Another skill drops in beside `learn-optimism/`. Neither manifest needs
touching, and both ecosystems find it.
