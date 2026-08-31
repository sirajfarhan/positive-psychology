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

Psychologists call it explanatory style, and they ask three things about any
reason you give. Does it last? How far does it spread? Is it you, or the
situation?

So you tell it, in chat, what actually happened to you. It finds the reason
you gave, stores that sentence word for word, and scores it. Then it starts
teaching you to hear the difference yourself, before it ever hands you a
term for it.

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

For your first twelve stories it teaches you nothing. It has to hear how you
already talk before it can show you anything about it. Six things that went
wrong, six that went right, and it reflects each one back to you as you go.

### Nothing it asks you is made up

It reads back through everything you've told it, picks one thing to work on,
and builds the question out of an event you actually lived. Your own
sentences are the only material that tests whether you can hear yourself.

### Every question asks what you'd do next

Your explanation decides what you do tomorrow, so that's what the questions
get at. One will ask what you'd actually do about the next deadline, and
only your memory of the last one can answer that.

### You answer in your own words

Every question is open, so you write a sentence back. That sentence does two
jobs. It shows whether you heard the difference, which is how it grades you,
and a full one joins your file as material for a later question. The scores
keep reading only the sentences you volunteered on your own, because those
are the ones that show how you actually talk.

### Sessions are short on purpose

A session is two or three questions, each one waiting on your answer before
the next arrives. Then it stops for the day, because practice spaced across
days is what sticks.

### You learn to hear it before you learn to name it

Four stages, and the vocabulary only turns up at the second one.

**Hearing it.** Given two of your own sentences, you can tell which one
leaves you something to do tomorrow. No terminology needed, and none given.

**Naming it.** Shown the word doing the work in a sentence you wrote, you
can say what that word is doing. "Always" makes the cause permanent. The
names for those three questions arrive here, once your ear is already there.

**Producing it.** You can tell the same event again with one of those three
changed and everything else identical.

**Catching it.** You hear yourself do it in ordinary conversation, with
nobody asking.

Get a question wrong past the first stage and you drop back one.

### Your scores follow your latest six

Only your six most recent setbacks and six most recent wins count toward the
score, so older sentences drop out and the number moves when you do. The
part worth watching is the distance between the two sides: how you explain
the bad ones against how you explain the good ones.

### Fifteen ideas get taught, six of them get charted

The six are the three questions above, asked separately about your setbacks
and about your wins, and those are the bars on the page. The nine that never
appear there get taught the same way: whether you've stopped arguing with
what happened, what you're quietly measuring yourself against, where the
next move sits, and six more like them. You meet those in the questions.

## Install

The repo is a plugin marketplace, so Claude Code can install it directly:

```
/plugin marketplace add sirajfarhan/positive-psychology
/plugin install positive-psychology@positive-psychology
```

Codex reads the same folder, and both tools share the one database. You'll
need `python3` and `node`, and the app builds the rest of itself the first
time it runs. Say `/learn-optimism` and it opens with one question.

## The database

An app that measures you over months has to outlive its own installs, so the
database sits outside the plugin, where your operating system keeps things
like it.

| | |
|---|---|
| macOS | `~/Library/Application Support/positive-psychology/` |
| Linux | `~/.local/share/positive-psychology/` |
| Windows | `%LOCALAPPDATA%\positive-psychology\` |

It survives every install, update and removal, and a file left by an older
version gets brought forward on the first run.

## Where it stops

It isn't therapy, and it never scores how you feel. When something heavier
than an explanation comes up, it stops, says so, and points you at real help
instead of scoring it or arguing with it.

## How far to trust it

The model does the scoring itself, working from example sentences written
for this skill. Nobody has checked whether a second rater would agree, and
there's no baseline from other people to compare you against. Trust the
direction, the gap between how you tell the bad ones and how you tell the
good ones, and the change against your own history. Don't trust the number
itself, and don't compare it to anyone.