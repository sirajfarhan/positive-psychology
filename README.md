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

So you talk about real things in chat. The skill finds the reason you
gave, stores it word for word, scores it, and starts teaching you to hear
the difference before it ever gives you a term for it.

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
page refreshes every few seconds, so what you're practising moves while
you're still talking.

## How the teaching works

### It listens before it teaches

Six things that went wrong and six that went right, the same count the
questionnaire it's built on uses. Until it has those it only collects, and
the scores, the practice and the vocabulary all wait their turn.

### Then it practises on your own sentences

With twelve in hand it reads everything you've told it and finds the pairs
you already wrote, the same cause explaining a win and a setback. Then it
asks you one question built out of your own details, the kind you answer
on gut feel. It never repeats itself, because it keeps every question it
has asked and every sentence it has used.

### And every question it asks is open

Your answers come back as sentences, and a sentence carries three things
at once: the evidence for how you heard it, tomorrow's practice material,
and more of your own voice for the next question to stand on. A
multiple-choice answer would carry none of that.

### So your answers become tomorrow's material

When you retell an event during practice, that new sentence joins the pool
the questions come from. It never counts toward your scores, because a
sentence you were talked into isn't evidence of how you talk on your own.

### Over weeks the questions climb, and terms come last

First you notice the two sentences feel different. Then you say the
difference in your own words. Then you retell your own event the other
way. The last step is catching yourself doing it in normal conversation,
with nobody asking. You move up a step by doing it, and a wrong answer
costs you one once you've climbed high enough to have one to lose.

### Meanwhile your scores move when you do

They only look at your latest six of each kind, so recent change shows up
instead of getting buried under a lifetime average. Once six more of each
sit behind those, it shows which way you've moved. Until then it shows
where you stand.

## What the code enforces

Written rules kept getting ignored, so the ones that matter live in the
code.

It refuses multiple-choice questions and says why. It won't take a score
outside the scale, or record growth on a win, because there's nothing to
grow from there. Only one question stays open at a time, and the code
blocks a second rather than trusting anyone to remember.

## Install

The repo is a plugin marketplace, so Claude Code can install it directly:

```
/plugin marketplace add sirajfarhan/positive-psychology
/plugin install positive-psychology@positive-psychology
```

Codex reads the same folder as a local plugin, and both tools share the one
database, so whichever you talk to, you're carrying on the same
conversation. You'll need `python3` and `node`, and the app builds the
rest of itself the first time it runs. Say `/learn-optimism` and it opens
with one question.

## The database

An app that measures you over months has to outlive its own installs, so
the database sits outside the plugin, where your operating system keeps
things like it.

| | |
|---|---|
| macOS | `~/Library/Application Support/positive-psychology/` |
| Linux | `~/.local/share/positive-psychology/` |
| Windows | `%LOCALAPPDATA%\positive-psychology\` |

Installing, updating or removing the app never reaches it. If an older
version kept your file elsewhere, it brings it along on the first run. Ask
it where anything ended up and it'll tell you.

The file updates itself on the next run and keeps a dated copy of the old
one. Nothing is lost, however old the version you're coming from.

## Where it stops

It isn't therapy, and it never scores how you feel. When something heavier
than an explanation comes up, it stops, says so, and points you at real
help instead of scoring it or arguing with it.

## What it can't do

One automated rater does the scoring, working from example sentences
written for this skill. Nobody has checked whether a second rater would
agree, and there's no baseline from other people to compare you against.
Trust the direction, the gap between how you tell the bad ones and how you
tell the good ones, and the change against your own history. Don't trust
the number itself, and don't compare it to anyone.

More skills can drop in beside this one, each with its own four parts, and
everything above stays true for each of them.
