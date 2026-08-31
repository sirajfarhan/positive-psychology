# positive-psychology

Skills for Claude Code and Codex, built on what positive psychology can
actually measure.

It follows a new architecture where a skill is an app. This one has its own
user interface, database and backend service, along with its instructions,
and all of them together drive the model to train optimism.

---

# learn-optimism

It reads how optimistic you are from the way you explain real events, then
teaches you to hear the difference yourself.

Someone who missed a deadline can explain it two ways.

> *I always leave things too late.*
>
> *I left that one too late.*

The first one can never stop being true, because "always" has no end in it.
The second is already finished. Most people reach for one more than the
other without noticing, and that habit can be measured. Psychologists call
it explanatory style, and they ask three things about a cause. Does it last?
How far does it reach? Is it you, or the situation?

So you tell it, in chat, what actually happened to you. The skill finds the
reason you gave, stores it word for word, scores it, and starts teaching you
to hear the difference before it ever gives you a term for it.

## The app

![The Optimism Map](docs/optimism-map.png)

| Part | What it does |
|---|---|
| **The database** | Your sentences word for word, every question it has asked and what your answer showed, and where you've got to on each idea |
| **The backend service** | Reads that database and hands the page your current scores, and the movement once there's history behind them |
| **The user interface** | The picture above: your result in a sentence, a bar for each of the three questions, and what you're practising |
| **The instructions** | How to score a sentence, what to ask next, and how to say it so it sounds like a person |

`/learn-optimism` starts the skill as an app, and it continues from where
you left off, across any session.

The app is read only, and for now you interact with it through chat. The
page keeps itself up to date every few seconds.

## How the teaching works

### It listens first

It gathers six things that went wrong and six that went right. Until it
has those it mirrors your own sentences back to you. The teaching waits.

### Then every question comes out of your own file

It reads across everything you've told it. From that it picks one idea to
work on, then builds the question out of your own details.

### The questions run forward

Say the money lands next week. What's the first thing that changes? You
answer that from memory. Anything you could solve by reading the words
alone gets rewritten before you see it.

### Your answers come back as sentences

Every question is open. Each answer shows how you heard it. The rich ones
join the pool the next questions come from, while the scores keep reading
only the events you brought in yourself.

### Sessions are short on purpose

A session runs a few turns and stops. Practice spread across days is what
holds, so it finishes early by design.

### The climb takes weeks, and terms arrive late

The end of it is catching yourself doing this mid-conversation, on your
own. You get there by hearing two of your own explanations differ, then
naming what does the work in something you said, then retelling one of
your own events the other way. Terms turn up at that middle step, once you
can already hear the thing. Past the first step, a wrong answer costs you
one.

### Your scores follow your latest six

They only look at your latest six of each kind. Once six more sit behind
those, it starts showing which way you've moved. The interesting
part is usually the gap between them: setbacks told one way, wins told the
other.

### Six of the fifteen ideas reach the map

Those six are the scored dimensions behind the bars. The other nine get
taught and tracked the same way, living in the practice.

## What the code enforces

It keeps every question open, and says why when something tries to close
one. Scores stay inside the scale, and growth gets recorded only on a
setback, because there's nothing to grow from in a win. And one question
stays open at a time, so you always know which one you're answering.

## Install

The repo is a plugin marketplace, so Claude Code can install it directly:

```
/plugin marketplace add sirajfarhan/positive-psychology
/plugin install positive-psychology@positive-psychology
```

Codex reads the same folder, and both tools share the one database. You'll
need
`python3` and `node`, and the app builds the rest of itself the first time
it runs. Say `/learn-optimism` and it opens with one question.

## The database

An app that measures you over months has to outlive its own installs, so
the database sits outside the plugin, where your operating system keeps
things like it.

| | |
|---|---|
| macOS | `~/Library/Application Support/positive-psychology/` |
| Linux | `~/.local/share/positive-psychology/` |
| Windows | `%LOCALAPPDATA%\positive-psychology\` |

It survives every install, update and removal. If an older
version kept your file elsewhere, it brings it along on the first run. Ask
it where anything ended up and it'll tell you.

The file updates itself on the next run and keeps a dated copy of the old
one. Everything survives, however old the version you're coming from.

## Where it stops

It isn't therapy, and it never scores how you feel. When something heavier
than an explanation comes up, it stops, says so, and points you at real
help instead of scoring it or arguing with it.

## How far to trust it

One automated rater does the scoring, working from example sentences
written for this skill. Nobody has checked whether a second rater would
agree, and there's no baseline from other people to compare you against.
Trust the direction, the gap between how you tell the bad ones and how you
tell the good ones, and the change against your own history. Don't trust
the number itself, and don't compare it to anyone.

More skills can drop in beside this one, each with its own four parts, and
everything above stays true for each of them.
