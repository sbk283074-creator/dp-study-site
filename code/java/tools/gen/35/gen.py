#!/usr/bin/env python3
"""Generate chapters/35-configuration-logging-and-graceful-shutdown.md.

    python3 tools/gen/35/gen.py

The service now has a data layer and sessions. What it does not have is any way to
be operated: the port is hard-coded, the only output is `System.out`, and stopping
it means killing it. This chapter is the three things that make a process
operable, and all three are the kind of code that is invisible until it is missing.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "35-configuration-logging-and-graceful-shutdown.md")

BLOCKS = {
    "core": gen.run_files(["OpsDemo.java", "Config.java", "Log.java", "Hooks.java"]),
    "layers": gen.sh("config.sh", "run-project"),
    "drain": gen.sh("drain.sh", "run-project"),
    "hook": gen.sh("hook.sh", "run-project"),
    "exhaustive": gen.bad("MissingCase.java", "does not cover all possible input values"),
    "fallthrough": gen.warn("Fallthrough.java", "fall-through"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 35
part: 5
title: Configuration, Logging and Graceful Shutdown
summary: The three things that decide whether a service can be operated at all: four configuration layers where every value remembers its origin, validation that kills the process before it binds a port, structured log lines that survive a hostile value and never contain a secret, and a shutdown that stops accepting work and then waits for what it already accepted.
minutes: 80
tags: [configuration, logging, structured-logging, shutdown, validation, operations]
---

A service that works is not the same thing as a service that can be operated. Everything built so far
has a port in a literal, diagnostics on `System.out`, and no way to stop that does not involve killing
the process. Those three gaps are invisible while you are writing the code and total once it is on
someone else's machine — you cannot find out why it chose port 8080, you cannot find out what it did
at 3am, and you cannot restart it without dropping whatever it was doing.

The claim that organises this chapter is that **configuration, logging and shutdown are not features,
they are the interface a service presents to whoever runs it.** Get them wrong and every incident
starts with "we can't tell what it was doing".

## Four layers, and every value remembers where it came from

@@core@@

Four layers, applied in order, last one wins: **defaults → config file → environment → command-line
arguments**. Arguments beat the environment, which beats the file, which beats the defaults, which is
what makes a container deployment possible (`--db`), a staged environment possible (environment
variables), and a sane local default possible (no configuration at all).

The part that is worth more than the layering is the second column — `origin`. A config value that
knows only its value tells you `port=9090`; a config value that knows its *provenance* tells you
`port=9090 from arguments`, and that is the difference between an incident you can resolve from the
log and one you have to reproduce. Every config layer in this book records both, and `--print-config`
prints both.

The third block is `--print-config` with the secret removed. **A service must be able to print its own
configuration without leaking it**, because the first thing anyone asks during an incident is "what
configuration is it running with", and the answer cannot be "I can't show you, it has the database
password in it". Redaction belongs in the printer, not in the caller, so no future caller can forget
it.

### Validate before you bind

The fourth block is validation, and its position matters more than its content: it has to run **before
the process does anything observable**. A service that validates after it has bound its port and
started serving has already told the load balancer it is healthy, which means the orchestrator will
send it traffic and then watch it die — repeatedly, in a loop, during a deploy.

The rule is: collect every problem, print all of them, exit non-zero. Not the first problem, because
whoever set the environment wrong set more than one thing wrong.

@@layers@@

One subtlety is visible at the end of that transcript: `--port` with no `=` is ignored rather than
crashing. A flag parser that throws on a flag it does not understand is a parser that makes a typo into
an outage, and a parser that silently accepts everything is a parser that makes a typo into a
mystery. Ignoring an unknown flag and *recording that it was ignored* is the only version that is
neither.

## Log lines that survive a hostile value

Structured logging means one JSON object per line, and it exists so that a machine can read your logs
without parsing English. Two properties of the lines above are the ones that matter:

**Secrets are removed at the point of writing.** `password`, `token` and `secret` become `<redacted>`
no matter what the caller passed. Redaction in the caller is a redaction that one caller forgets, and
one is all it takes — logs are replicated to places with different access controls than the database
they came from.

**A newline in a value becomes `\n`.** The transcript shows a username containing a newline arriving as
one field on one line. Unescaped, that value would have produced *two* lines, and the second one would
say `admin=true` — written by an attacker, into your log search and your alerting. This is the same bug
as Chapter 29's HTML escaping with a different destination, which is the recurring lesson: escaping is
a property of the place the value lands.

:::pitfall Logging the thing you were told not to log
"Don't log passwords" is a rule everyone agrees with and nobody implements, because the leak is almost
never a line that says `password=hunter2`. It is a request body logged at debug level, a stack trace
whose message contains the connection URL, or a `Map` dumped wholesale because it was convenient. Two
habits that actually hold: **log keys, not values** for anything credential-shaped, and make the
logger itself redact, so the safe path is the default path rather than the one that requires
remembering.
:::

## Stopping

@@drain@@

A graceful stop is two steps in a fixed order:

1. **Stop accepting new work.** For an HTTP server that is closing the listener; for a pool that is
   `shutdown()`.
2. **Wait for the work already accepted.** `awaitTermination` with a bound.

Skipping the first means accepting requests you will never serve. Skipping the second means cutting
off requests that were halfway through — a payment that was sent but not recorded, a file that was
half written. The bound on the second step matters too: a drain with no timeout is a process that
never exits, and a deploy that hangs forever is its own outage. Choose the timeout deliberately —
thirty seconds is a common default — and log what was still in flight when it expired.

Shutdown steps run in **reverse order of registration**, exactly like `try`-with-resources, so the
thing opened first is closed last: stop the listener, drain the pool, close the database. And they run
**once** — a hook that can run twice can double-free a resource that was only acquired once.

### The JVM's own hook

@@hook@@

`Runtime.addShutdownHook` is what runs when the JVM exits normally — `System.exit`, the last
non-daemon thread finishing, or Ctrl-C. It is the right place for "flush the log" and "close the
database". Three honest caveats:

- **It does not run if the process is killed with `SIGKILL`**, or if the machine loses power. A
  shutdown hook is not durability; anything that must survive a crash needs to be written durable at
  the time it happens.
- **Hooks run concurrently with each other**, so ordering between two hooks is not guaranteed. If
  order matters, register one hook that runs a list in the order you want — which is what the `Hooks`
  type above is for.
- **A hook must be fast.** Kubernetes gives you a grace period, typically thirty seconds, and then
  `SIGKILL`. A hook that takes a minute is a hook that gets interrupted halfway.

`SIGTERM` is what a container runtime actually sends, and Java gives you no portable way to handle it
directly — the usual answer is a shutdown hook plus a readiness endpoint that starts failing the
moment shutdown begins, so the load balancer stops sending new work before the process goes away.

### Two mistakes javac catches

The first is a `switch` expression that does not cover every value it can be given:

@@exhaustive@@

This is exactly the code you write when parsing a configuration value into an enum, and javac refusing
it is why Chapter 16's sealed types and exhaustive `switch` matter here: **a configuration value that
can only be one of four things should be impossible to handle for three of them.** Add the missing
cases or add a `default` that throws — either is fine, silently doing nothing is not.

The second is a warning, and it is the oldest bug in the language:

@@fallthrough@@

A missing `break` in a `switch` is legal Java and almost never intended. `-Xlint:fallthrough` finds it,
which is one more reason every program in this book is compiled with `-Xlint:all`.

:::scenario The deploy that hung because an environment variable was empty
A service reads `DB_URL` from the environment. A deploy sets it to the empty string — a templating bug
in the chart, an empty value in the secret store, someone's local `export DB_URL=`. The service starts,
connects to... something, and every request fails with a database error. Because it bound its port
first, the orchestrator thinks it is healthy and keeps it in rotation. Three replicas, all broken,
serving 500s for eleven minutes.

```sh run-project
@@scenario@@
```

:::solution
Validate the whole configuration before binding anything, and make the failure loud:

1. **Collect every problem, not the first one.** The transcript prints both the empty `db` and
   whatever else is wrong, so one fix round is enough.
2. **Fail before the port is bound.** Build the config, validate it, and only then start the server.
   A process that dies at startup with exit code 1 and a clear message is a failed deploy that rolls
   back; a process that starts and then fails every request is an outage.
3. **Print the configuration you validated, with secrets removed.** `--print-config` on the way out
   gives you the answer to "what was it running with" in the log of the process that died, which is
   the log you still have.
4. **Treat an empty string as missing.** `db=""` is not a database path; it is an unset variable that
   happened to be set. The validator above rejects both, and that is deliberate — `getenv` returning
   `""` and returning `null` are the same bug wearing two hats.
5. **Add a readiness probe that checks the dependency.** Liveness says "restart me if I am dead";
   readiness says "do not send me traffic yet". A pod that is up but has no database is exactly the
   case readiness exists for.

:::

## Key takeaways

- Configuration has four layers — defaults, file, environment, arguments — and the last one wins.
- Record the *origin* of every value, so `--print-config` can explain why a value is what it is.
- Validate the whole configuration before binding a port, and print every problem found, not the first.
- Treat an empty environment variable as missing: `""` and `null` are the same bug.
- Structured logging is one JSON object per line, so a machine can read it without parsing English.
- Redact secrets in the logger, not in the caller, so the safe path is the default path.
- Escape newlines in every logged value, or a hostile value writes its own lines into your logs.
- A graceful stop is stop-accepting then wait-for-accepted, in that order, with a bound on the wait.
- Shutdown steps run in reverse registration order and exactly once.
- A JVM shutdown hook does not run on `SIGKILL`, runs concurrently with other hooks, and must be fast.

## Practice

- [ ] Layer the same key from defaults, environment and arguments, and print the winning value and its origin.
- [ ] Create a logger with a `warn` threshold, write one line at each level, and print how many were kept.
- [ ] Log a value containing a newline and show that the output is still one line.
- [ ] Register two shutdown steps, run the shutdown twice, and print the order and the stopped flag.

## Solutions

:::solution Exercise 1
@@sol1@@

Arguments win because they are applied last. That ordering is a choice, not a law — some systems make
the environment win so that an operator can override what a deploy script wrote — but whichever order
you pick has to be written down, because "which layer wins" is the question behind every config
surprise.

:::

:::solution Exercise 2
@@sol2@@

The threshold is a floor: everything at or above it is kept. Note that `written()` counts lines that
were actually emitted, so a line filtered out costs nothing — which is why a debug-level string
built with concatenation is still worth avoiding in a hot loop.

:::

:::solution Exercise 3
@@sol3@@

One line in, one line out. The forged second line never appeared, because the newline became two
characters inside a quoted string. This is the log-injection equivalent of SQL injection: same shape,
different destination, same fix — the value travels as data and never as syntax.

:::

:::solution Exercise 4
@@sol4@@

Reverse order, and the second `run()` did nothing. Both properties are the point: reverse order mirrors
`try`-with-resources, and idempotence is what makes a hook safe to call from both your own shutdown
path and the JVM's.

:::
"""

gen.write(TEMPLATE, BLOCKS)
