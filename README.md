# skill-as-an-app

Systems like Claude and ChatGPT already have a very minimal version of a
database. One part is categorised as memory, and the rest is generally known
as context. Personalisation is an emergent phenomenon of that memory and
context.

Memory, context and personalisation are still very general terms. As we get
more and more specific, more capabilities emerge out of these systems, and
they start solving a range of problems we face across individual lives and
businesses.

A skill is usually a folder of instructions you drop into Claude. This repo
follows a different architecture, where a skill is an app. It has its own
user interface, database and backend service, along with its instructions,
and all of them together drive the model.

You can technically get all of this working with scripts, JSON files and
Markdown. It's just that those components aren't made for the capabilities
we want out of the system. Using an actual database solves most of the
problems we already solved in the pre-AI era, and it makes room for emergent
capabilities that create a personalised learning experience.

---

# learn-optimism

The skill in this repo, published as an MVP.

Since AI can't look into our brains directly, the best way to understand
someone's current state of optimism is through how they explain their past
events. In positive psychology it's known as explanatory style.

It starts by onboarding you with questions about six wins and six setbacks
from the past, and drills into how you explain them.

Then it scores each explanation across three core dimensions:

1. **Personalisation:** whether you attribute it to yourself or to outside
   forces
2. **Permanence:** whether you consider it temporary or permanent
3. **Pervasiveness:** whether you consider it to apply to all aspects of
   your life or just one specific situation

Someone who's optimistic often attributes good events to themselves, thinks
they're permanent and knows they apply to all parts of their life, while
doing the opposite for bad events. For someone who's pessimistic, it's the
other way around.

Once that's done, the teaching phase begins. It uses principles taught by
life coaches like Peter Sage to help you see the same explanations
differently, nudging you closer to optimism.

To see that you're actually progressing, there's a minimal user interface:
an optimism map where you can see your current state, which keeps updating
as you go.

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

### Every question comes from something you actually lived

It reads back through everything you've told it, picks one thing to work on,
and builds the question out of one of your own events.

### You answer in your own words

You write a sentence back. That sentence shows whether you heard the
difference, which is how it grades you, and a full one joins your file as
material for a later question. Your scores read only what you volunteered
before any coaching.

### Sessions are short on purpose

Two or three questions, each waiting on your answer, then it stops for the
day.

### Your scores follow your latest six

Only your six most recent setbacks and six most recent wins count. The part
worth watching is the distance between them: how you explain the bad ones
against how you explain the good ones.

## Install

The repo is a plugin marketplace, so Claude Code can install it directly:

```
/plugin marketplace add sirajfarhan/skill-as-an-app
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

It survives every install, update and removal. If an older version kept your
file elsewhere, it brings it along on the first run. Ask it where anything
ended up and it'll tell you.

The file updates itself on the next run and keeps a dated copy of the old
one, however old the version you're coming from.

## Where it stops

It scores the explanation you gave for an event, and that's the whole of
what it does. When something heavier than an explanation comes up, it stops,
says so, and points you at real help instead of scoring it or arguing with
it.

## How far to trust it

The model does the scoring itself, working from example sentences written
for this skill. Nobody has checked whether a second rater would agree, and
there's no baseline from other people to compare you against. Trust the
direction, the gap between how you tell the bad ones and how you tell the
good ones, and the change against your own history. Don't trust the number
itself, and don't compare it to anyone.

More skills can drop in beside this one, each with its own four parts, and
everything above stays true for each of them.