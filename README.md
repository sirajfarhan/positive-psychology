# positive-psychology

Skills for Claude Code and Codex, built on what positive psychology can
actually measure.

A skill is a folder of instructions you drop into Claude, and usually that
is all it is. It follows a new architecture where a skill is an app. This
one has its own user interface, database and backend service, along with its
instructions, and all of them together drive the model to train optimism.

---

# learn-optimism

It reads how optimistic you are from the way you explain real events, then
teaches you to hear the difference yourself.

Someone who missed a deadline can explain it two ways.

> *I always leave things too late.*
>
> *I left that one too late.*

The first has no end in it, so there's nothing to fix and nothing to do
differently tomorrow. The second one already finished, which leaves you a
next deadline to plan for. Most people lean one way without noticing, and
that lean is what Martin Seligman's research ties to how well people keep
going after things go wrong.

Psychologists call it explanatory style, and they ask three things about
any reason you give. Does it last? How far does it spread? Is it you, or
the situation?

So you tell it, in chat, what actually happened to you. It finds the
reason you gave, stores that sentence word for word, and scores it. Then
it starts teaching you to hear the difference yourself, before it ever
hands you a term for it.

## The app

![The Optimism Map](docs/optimism-map.png)

| Part | What it does |
|---|---|
| **The database** | Every sentence you've given it, word for word. Every question it has asked and how you answered. How far you've got with each idea it teaches |
| **The backend service** | Reads the database and works out your current scores, plus which way they've moved once there's enough history to compare against |
| **The user interface** | The picture above: your result in a sentence, a bar for each of the three questions, and what you're practising |
| **The instructions** | How to score a sentence, what to ask next, and how to say it so it sounds like a person |

`/learn-optimism` starts the skill as an app, and it continues from where
you left off, across any session.

A pattern across twelve sentences is hard to see from inside the
conversation that produced them, which is what the page is for. It's read
only, and for now you interact with the app through chat, while the page
keeps itself up to date every few seconds.

## How the teaching works

### It listens before it teaches you anything

For your first twelve stories it teaches you nothing. It has to hear how
you already talk before it can show you anything about it. Six things that
went wrong, six that went right, and it reflects each one back to you as
you go.

### Nothing it asks you is made up

It reads back through everything you've told it, picks one thing to work
on, and builds the question out of an event you actually lived. Your own
sentences are the only material that tests whether you can hear yourself.

### Every question asks what you'd do next

Your explanation decides what you do tomorrow, so that's what the
questions get at. One will ask what you'd actually do about the next
deadline, and only your memory of the last one can answer that.

### You answer in your own words

There's no A or B to pick. A sentence back gives it two things at once:
how you heard the question, and fresh material for the next one. Your
scores stay built from the events you brought in yourself.

### Sessions are short on purpose

A session is two or three questions, each one waiting on your answer
before the next arrives. Then it stops for the day, because practice
spaced across days is what sticks.

### You learn to hear it before you learn to name it

First you notice two of your own sentences pulling in different directions.
Then you can say what one of those words is doing. Then you can tell an
event again with a single thing moved and the rest untouched. Last, you
catch yourself doing it mid-conversation with nobody asking. The vocabulary
arrives at step two, once your ear is already there, because a word you can
define and can't hear is worth nothing. Get a question wrong after that
first step and you go back one.

### Your scores follow your latest six

Only your six most recent setbacks and six most recent wins count toward the
score, so older sentences drop out and the number moves when you do. The
part worth watching is the distance between the two sides: how you explain
the bad ones against how you explain the good ones.

### Fifteen ideas get taught, six of them get charted

The six are the three questions above, asked separately about your
setbacks and about your wins, and those are the bars on the page. The
nine that never appear there get taught the same way: whether you've
stopped arguing with what happened, what you're quietly measuring yourself
against, where the next move sits, and six more like them. You meet those
in the questions.

## What the code enforces

A few rules matter enough that they live in the code instead of the
instructions, because instructions get skipped. Questions stay open-ended,
and any attempt at a multiple choice gets turned down with a reason.
Scores stay inside the one-to-seven range the researchers use. And one
question stays open at a time, so you always know which one you're
answering.

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
one, however old the version you're coming from.

## Where it stops

It isn't therapy, and it never scores how you feel. When something heavier
than an explanation comes up, it stops, says so, and points you at real
help instead of scoring it or arguing with it.

## How far to trust it

The model does the scoring itself, working from example sentences written
for this skill. Nobody has checked whether a second rater would
agree, and there's no baseline from other people to compare you against.
Trust the direction, the gap between how you tell the bad ones and how you
tell the good ones, and the change against your own history. Don't trust
the number itself, and don't compare it to anyone.

More skills can drop in beside this one, each with its own four parts, and
everything above stays true for each of them.
