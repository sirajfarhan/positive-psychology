# positive-psychology

Skills for Claude Code and Codex, built on what positive psychology can
actually measure.

It follows a new architecture where a skill is an app. This one has its own
user interface, database and backend service, along with its instructions,
and all of them together drive the model to train optimism.

---

# learn-optimism

It reads how optimistic you are from the way you explain real events. Then
it teaches you to hear the difference yourself.

Here are two ways of explaining the same missed deadline.

> *I always leave things too late.*
>
> *I left that one too late.*

The first one can never stop being true, because "always" has no end in it.
The second one is already finished. Most people reach for one of those more
than the other without noticing, and that habit can be measured.
Psychologists call it explanatory style, and they ask three things about a
cause. Does it last? How far does it reach? Is it you, or the situation?

So you talk about real things in chat. The skill finds the reason you gave
and stores that sentence word for word. Then it scores it, and starts
teaching you to hear the difference before it ever gives you a term for it.

## The app inside the skill

![The Optimism Map](docs/optimism-map.png)

Four parts, one job.

| Part | What it does |
|---|---|
| **The database** | Keeps every sentence you've given it, what you've practised, and any question still waiting on you |
| **The backend service** | Reads that database and hands the page your current scores, and the movement once there's history behind them |
| **The user interface** | The picture above: your result in a sentence, a bar for each of the three questions, and what you're practising |
| **The instructions** | How to score a sentence, what to ask next, and how to say it so it sounds like a person |

You say `/learn-optimism`, and it opens your file and starts the page if it
isn't already running. If a question was left unanswered last time, it
comes back before anything new starts.

Every sentence of yours enters through chat, and nothing else can touch
what you've said: the page reads, and it has no buttons because there's
nothing it could write with them. It refreshes itself every few seconds,
so what you're practising moves while you're still talking, and both sides
read the same numbers out of the same file, so they can't tell you
different things.

## How the teaching works

**It listens before it teaches.** Six things that went wrong and six that
went right, the same count the questionnaire it's built on uses. Until it
has those, it only listens, and the scores, the practice and the
vocabulary all wait their turn.

**Practice is built from your own sentences.** It reads everything you've
told it and finds the pairs you already wrote, the same cause explaining a
win and a setback, one week told two ways. Then it runs one question
forward from your own details, the kind you answer on gut feel, and it
never repeats itself, because it keeps every question it has asked and
every sentence it has used.

**Terms come last.** First you notice the two sentences feel different.
Then you say what the difference is in your own words. Then you retell
your own event the other way. The last step is catching yourself doing it
in normal conversation, with nobody asking. Reading about any of this
moves nothing, and a wrong answer costs a step once you've climbed high
enough to have one to lose.

**Every question is open.** Your answers come back as sentences, and a
sentence carries three things at once: the evidence for how you heard it,
tomorrow's practice material, and more of your own voice for the next
question to stand on. A multiple-choice answer carries none of them, so it
never asks one.

**Your answers become tomorrow's material.** When you retell an event
during practice, that new sentence gets kept as practice. It joins the
pool the questions come from, and it never counts toward your scores,
because a sentence you were talked into isn't evidence of how you talk on
your own.

**Your scores move when you do.** They only look at your latest six of
each kind, so recent change shows up instead of getting buried under a
lifetime average. Once you've been at it long enough to have six more of
each behind those, it starts showing which way you've moved, and until
then it shows where you stand and leaves it there.

## What the code enforces

Written rules kept getting ignored out of habit, so the ones that matter
now live in the code.

It refuses multiple-choice questions outright, and says why when it does.
It won't take a score outside the scale, or record growth on something
that went well, because there's nothing to grow from there. Only one
question can be open at a time, and the code blocks a second one rather
than trusting anyone to remember. A sentence you were talked into can't
get into your scores.

## Install

The repo is a plugin marketplace, so Claude Code can install it directly:

```
/plugin marketplace add sirajfarhan/positive-psychology
/plugin install positive-psychology@positive-psychology
```

Codex reads the same folder as a local plugin, and both tools share the one
database, so whichever you talk to, you're carrying on the same
conversation. You'll need `python3` and `node`; the app builds the rest of
itself the first time it runs, and starts its backend service and user
interface whenever you say `/learn-optimism`. It opens with one question.

## The database

An app that measures you over months has to outlive its own installs, so
the database sits outside the plugin entirely, where your operating system
already keeps things like it, which is nobody's private corner.

| | |
|---|---|
| macOS | `~/Library/Application Support/positive-psychology/` |
| Linux | `~/.local/share/positive-psychology/` |
| Windows | `%LOCALAPPDATA%\positive-psychology\` |

Installing, updating or removing the app never reaches it. If an older version
kept your file somewhere else, it brings it along the first time it runs,
and if you ever wonder where anything ended up, ask it and it'll tell you.

Pull a newer version and your history comes with it. The file updates
itself the next time you run anything, keeps a dated copy of the old one,
and says a single line about what it did. Nothing you've told it is lost,
however old the version you're coming from.

## Where it stops

It isn't therapy, and it never scores how you feel. When something heavier
than an explanation comes up, it stops and says so. It points you at real
help instead of scoring it or arguing with it.

## What it can't do

One automated rater does the scoring, working from example sentences
written for this skill. Nobody has checked whether a second rater would
agree, and there's no baseline from other people to compare you against.
Trust the direction, the gap between how you tell the bad ones and how you
tell the good ones, and the change against your own history. Don't trust
the number itself, and don't compare it to anyone.

More skills can drop in beside this one, each with its own user interface,
database and backend service, along with its own instructions, and
everything above stays true for each of them.
