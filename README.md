# skill-as-an-app

A skill for Claude Code and Codex, built on what positive psychology can
actually measure.

A skill is a folder of instructions you drop into Claude, and usually that
is all it is. This one follows a new architecture where a skill is an app.
It has its own user interface, database and backend service, along with its
instructions, and all of them together drive the model to train optimism.

---

# learn-optimism

Someone who missed a deadline can explain it two ways.

> *I always leave things too late.*
>
> *I left that one too late.*

The first has no end in it, so there's nothing to do differently tomorrow.
The second already finished, which leaves you a next deadline to plan for.
Same event, two different tomorrows.

That habit of explanation is what positive psychology calls explanatory
style. Since nothing can look into your head directly, the way you explain
what already happened to you is the closest available reading of how
optimistic you are, and Martin Seligman's research ties it to how well
people keep going after things go wrong.

The skill starts by asking you about six wins and six setbacks from your
past, and drills into how you explain each one. Then it scores every
explanation on three dimensions:

1. **Permanence:** whether the cause is over, or still running
2. **Pervasiveness:** whether it touches one corner of your life, or all of
   it
3. **Personalisation:** whether it was you, or the situation

An optimist explains good events as their own doing, lasting, and spread
across their life, and explains bad events the opposite way: the situation,
temporary, and contained to one place. A pessimist has it the other way
around.

Once it has your twelve, the teaching begins. Every question is built out of
one of your own events, and you answer in a sentence, in your own words. It
uses Seligman's method alongside principles from Peter Sage to help you see
the same explanations differently, nudging you closer to optimism. Sessions
are two or three questions, then it stops for the day.

To see whether you're actually moving, there's a minimal user interface: an
optimism map showing where you stand, which keeps updating as you go. Only
your six most recent setbacks and six most recent wins count, so the map
reads where you are now rather than your history.

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

The app is read only, and for now you interact with it through chat.
The page keeps itself up to date every few seconds.

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
