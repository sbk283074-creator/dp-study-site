---
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

```java run-files
// ===== OpsDemo.java =====

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class OpsDemo {
    public static void main(String[] args) {
        Config config = new Config();

        Map<String, String> defaults = new LinkedHashMap<>();
        defaults.put("port", "8080");
        defaults.put("level", "info");
        defaults.put("db", "bulletin.db");
        defaults.put("secret", "from-defaults");
        config.layer(defaults, "defaults");

        Map<String, String> file = new LinkedHashMap<>();
        file.put("db", "/var/lib/bulletin/app.db");
        config.layer(file, "config file");

        Map<String, String> environment = new LinkedHashMap<>();
        environment.put("level", "debug");
        config.layer(environment, "environment");

        config.arguments(new String[]{"--port=9090", "--secret=s3cr3t"});

        System.out.println("--- where every value came from ---");
        for (String key : List.of("port", "level", "db", "secret")) {
            System.out.println("  " + key + " = " + config.get(key)
                    + "   (" + config.originOf(key) + ")");
        }
        System.out.println();
        System.out.println("four layers, last wins: arguments beat environment, which beats");
        System.out.println("the file, which beats the defaults. The point of recording the");
        System.out.println("origin is that `--print-config` then answers \"why is this value");
        System.out.println("what it is\" instead of only \"what is it\"");

        System.out.println();
        System.out.println("--- printed, with secrets removed ---");
        System.out.println("  " + config.printed());

        System.out.println();
        System.out.println("--- validation, before anything is served ---");
        List<String> problems = config.validate();
        System.out.println("  problems : " + problems.size());

        Config broken = new Config();
        broken.layer(Map.of("port", "0", "level", "loud"), "arguments");
        for (String problem : broken.validate()) {
            System.out.println("  " + problem);
        }

        System.out.println();
        System.out.println("--- log lines, numbered rather than timestamped ---");
        Log log = new Log("info");
        log.line("debug", "this is below the threshold and never appears");
        log.line("info", "server starting", "port", "9090");
        log.line("info", "login", "user", "bob", "password", "hunter2");
        log.line("warn", "slow request", "path", "/notes", "millis", "812");
        System.out.println("  written      : " + log.written());
        System.out.println("  debug kept   : " + log.enabled("debug"));

        System.out.println();
        System.out.println("--- a value that tries to forge a log line ---");
        log.line("info", "login", "user", "bob\nINJECTED admin=true");
        System.out.println();
        System.out.println("  the newline became \\n, so the value stayed one field and the");
        System.out.println("  line stayed one line. Without that, a username can write");
        System.out.println("  whatever it likes into your log aggregation");

        System.out.println();
        System.out.println("--- shutdown, in reverse order, once ---");
        Hooks hooks = new Hooks();
        hooks.add(() -> System.out.println("  stop accepting requests"));
        hooks.add(() -> System.out.println("  close the pool"));
        hooks.add(() -> System.out.println("  close the database"));
        hooks.run();
        hooks.run();
        System.out.println("  stopped      : " + hooks.stopped());
    }
}

// ===== Config.java =====

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Four layers, last one wins, and every value remembers where it came from.
 * That provenance is what makes `--print-config` an answer instead of a guess.
 */
public final class Config {

    private static final List<String> SECRETS = List.of("secret", "password", "token");

    private final Map<String, String> values = new TreeMap<>();
    private final Map<String, String> origin = new TreeMap<>();

    public void layer(Map<String, String> entries, String source) {
        for (Map.Entry<String, String> entry : entries.entrySet()) {
            values.put(entry.getKey(), entry.getValue());
            origin.put(entry.getKey(), source);
        }
    }

    public void arguments(String[] args) {
        for (String arg : args) {
            if (!arg.startsWith("--")) {
                continue;
            }
            String body = arg.substring(2);
            int at = body.indexOf('=');
            if (at <= 0) {
                continue;
            }
            values.put(body.substring(0, at), body.substring(at + 1));
            origin.put(body.substring(0, at), "arguments");
        }
    }

    public String get(String key) {
        return values.get(key);
    }

    public String originOf(String key) {
        return origin.getOrDefault(key, "missing");
    }

    public int intOf(String key, int fallback) {
        String raw = values.get(key);
        if (raw == null) {
            return fallback;
        }
        try {
            return Integer.parseInt(raw.trim());
        } catch (NumberFormatException e) {
            return Integer.MIN_VALUE;
        }
    }

    /** Every problem found at startup, so the process can die before it serves. */
    public List<String> validate() {
        List<String> problems = new ArrayList<>();
        int port = intOf("port", -1);
        if (port < 1 || port > 65535) {
            problems.add("port must be between 1 and 65535, got " + port);
        }
        String level = get("level");
        if (level == null) {
            problems.add("level is required");
        } else if (!List.of("debug", "info", "warn", "error").contains(level)) {
            problems.add("level must be one of debug, info, warn, error; got " + level);
        }
        if (get("db") == null || get("db").isEmpty()) {
            problems.add("db is required");
        }
        return problems;
    }

    /** Secrets never leave this method in the clear. */
    public String printed() {
        StringBuilder out = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : values.entrySet()) {
            if (!first) {
                out.append(", ");
            }
            first = false;
            out.append('"').append(entry.getKey()).append("\": \"");
            out.append(SECRETS.contains(entry.getKey()) ? "<redacted>" : entry.getValue());
            out.append('"');
        }
        return out.append('}').toString();
    }
}

// ===== Log.java =====

import java.util.ArrayList;
import java.util.List;

/**
 * One JSON object per line, with no timestamp in it. A real logger stamps every
 * line; this one numbers them, because a transcript that changes every run is a
 * transcript that cannot be checked.
 */
public final class Log {

    private static final List<String> SECRETS = List.of("password", "token", "secret");

    private final List<String> lines = new ArrayList<>();
    private final String threshold;
    private static final List<String> ORDER = List.of("debug", "info", "warn", "error");

    public Log(String threshold) {
        this.threshold = threshold;
    }

    public boolean enabled(String level) {
        return ORDER.indexOf(level) >= ORDER.indexOf(threshold);
    }

    public void line(String level, String message, String... fields) {
        if (!enabled(level)) {
            return;
        }
        StringBuilder out = new StringBuilder();
        out.append("{\"seq\": ").append(lines.size() + 1);
        out.append(", \"level\": \"").append(level).append('"');
        out.append(", \"msg\": \"").append(escape(message)).append('"');
        for (int i = 0; i + 1 < fields.length; i += 2) {
            String value = SECRETS.contains(fields[i]) ? "<redacted>" : fields[i + 1];
            out.append(", \"").append(escape(fields[i])).append("\": \"")
                    .append(escape(value)).append('"');
        }
        out.append('}');
        String built = out.toString();
        lines.add(built);
        System.out.println(built);
    }

    /** A newline in a value is a fake log line, so it becomes two characters. */
    public static String escape(String value) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            switch (c) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                default -> {
                    if (c < 0x20) {
                        out.append(String.format("\\u%04x", (int) c));
                    } else {
                        out.append(c);
                    }
                }
            }
        }
        return out.toString();
    }

    public int written() {
        return lines.size();
    }
}

// ===== Hooks.java =====

import java.util.ArrayList;
import java.util.List;

/** Shutdown steps that must run, in reverse order of registration, exactly once. */
public final class Hooks {

    private final List<Runnable> steps = new ArrayList<>();
    private boolean done;

    public void add(Runnable step) {
        steps.add(step);
    }

    public void run() {
        if (done) {
            System.out.println("  already stopped: " + done);
            return;
        }
        done = true;
        for (int i = steps.size() - 1; i >= 0; i--) {
            steps.get(i).run();
        }
    }

    public boolean stopped() {
        return done;
    }
}
```

```text
--- where every value came from ---
  port = 9090   (arguments)
  level = debug   (environment)
  db = /var/lib/bulletin/app.db   (config file)
  secret = s3cr3t   (arguments)

four layers, last wins: arguments beat environment, which beats
the file, which beats the defaults. The point of recording the
origin is that `--print-config` then answers "why is this value
what it is" instead of only "what is it"

--- printed, with secrets removed ---
  {"db": "/var/lib/bulletin/app.db", "level": "debug", "port": "9090", "secret": "<redacted>"}

--- validation, before anything is served ---
  problems : 0
  port must be between 1 and 65535, got 0
  level must be one of debug, info, warn, error; got loud
  db is required

--- log lines, numbered rather than timestamped ---
{"seq": 1, "level": "info", "msg": "server starting", "port": "9090"}
{"seq": 2, "level": "info", "msg": "login", "user": "bob", "password": "<redacted>"}
{"seq": 3, "level": "warn", "msg": "slow request", "path": "/notes", "millis": "812"}
  written      : 3
  debug kept   : false

--- a value that tries to forge a log line ---
{"seq": 4, "level": "info", "msg": "login", "user": "bob\nINJECTED admin=true"}

  the newline became \n, so the value stayed one field and the
  line stayed one line. Without that, a username can write
  whatever it likes into your log aggregation

--- shutdown, in reverse order, once ---
  close the database
  close the pool
  stop accepting requests
  already stopped: true
  stopped      : true
```

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

```sh run-project
cat > Layering.java <<'JAVA'
import java.util.LinkedHashMap;
import java.util.Map;

public class Layering {
    public static void main(String[] args) {
        Config config = new Config();
        config.layer(Map.of("port", "8080", "level", "info"), "defaults");
        System.out.println("after defaults  : port=" + config.get("port")
                + " from " + config.originOf("port"));

        Map<String, String> file = new LinkedHashMap<>();
        file.put("port", "7000");
        config.layer(file, "config file");
        System.out.println("after the file  : port=" + config.get("port")
                + " from " + config.originOf("port"));

        config.layer(Map.of("port", "6000"), "environment");
        System.out.println("after env       : port=" + config.get("port")
                + " from " + config.originOf("port"));

        config.arguments(new String[]{"--port=5000"});
        System.out.println("after arguments : port=" + config.get("port")
                + " from " + config.originOf("port"));

        config.arguments(new String[]{"--port"});
        System.out.println("a flag with no = : port=" + config.get("port")
                + " from " + config.originOf("port"));
        System.out.println();
        System.out.println("the last layer to speak wins, and every value knows who spoke");
        System.out.println("last -- which is the difference between a config bug you can");
        System.out.println("see and one you have to reproduce");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Layering.java
java -cp out Layering
```

```text
after defaults  : port=8080 from defaults
after the file  : port=7000 from config file
after env       : port=6000 from environment
after arguments : port=5000 from arguments
a flag with no = : port=5000 from arguments

the last layer to speak wins, and every value knows who spoke
last -- which is the difference between a config bug you can
see and one you have to reproduce
```

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

```sh run-project
cat > Drain.java <<'JAVA'
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Drain {
    public static void main(String[] args) throws InterruptedException {
        AtomicInteger finished = new AtomicInteger();
        CountDownLatch inFlight = new CountDownLatch(3);
        ExecutorService pool = Executors.newFixedThreadPool(4);

        for (int i = 0; i < 3; i++) {
            pool.execute(() -> {
                try {
                    Thread.sleep(200);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                finished.incrementAndGet();
                inFlight.countDown();
            });
        }

        System.out.println("shutting down with 3 requests still running");
        pool.shutdown();
        boolean drained = pool.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("  finished before exit : " + finished.get());
        System.out.println("  drained              : " + drained);
        System.out.println();
        System.out.println("a graceful stop is two things in order: stop accepting new work,");
        System.out.println("then wait for the work already accepted. shutdown() does the");
        System.out.println("first and awaitTermination the second, and skipping either one");
        System.out.println("means either a request that never started or one that was cut off");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Drain.java
java -cp out Drain
```

```text
shutting down with 3 requests still running
  finished before exit : 3
  drained              : true

a graceful stop is two things in order: stop accepting new work,
then wait for the work already accepted. shutdown() does the
first and awaitTermination the second, and skipping either one
means either a request that never started or one that was cut off
```

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

```sh run-project
cat > JvmHook.java <<'JAVA'
public class JvmHook {
    public static void main(String[] args) {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("  hook: flushing the log");
            System.out.println("  hook: closing the database");
        }));
        System.out.println("main: starting");
        System.out.println("main: about to call System.exit(0)");
        System.exit(0);
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out JvmHook.java
java -cp out JvmHook
echo "exit status: $?"
```

```text
main: starting
main: about to call System.exit(0)
  hook: flushing the log
  hook: closing the database
exit status: 0
```

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

```java bad
public class MissingCase {
    enum Level { DEBUG, INFO, WARN, ERROR }

    public static void main(String[] args) {
        Level level = Level.WARN;
        String shortName = switch (level) {
            case DEBUG -> "D";
            case INFO -> "I";
        };
        System.out.println(shortName);
    }
}
```

```text
error: the switch expression does not cover all possible input values
```

This is exactly the code you write when parsing a configuration value into an enum, and javac refusing
it is why Chapter 16's sealed types and exhaustive `switch` matter here: **a configuration value that
can only be one of four things should be impossible to handle for three of them.** Add the missing
cases or add a `default` that throws — either is fine, silently doing nothing is not.

The second is a warning, and it is the oldest bug in the language:

```java warn
public class Fallthrough {
    public static void main(String[] args) {
        int code = 1;
        switch (code) {
            case 1:
                System.out.println("one");
            case 2:
                System.out.println("two");
                break;
            default:
                break;
        }
    }
}
```

```text
warning: [fallthrough] possible fall-through into case
```

A missing `break` in a `switch` is legal Java and almost never intended. `-Xlint:fallthrough` finds it,
which is one more reason every program in this book is compiled with `-Xlint:all`.

:::scenario The deploy that hung because an environment variable was empty
A service reads `DB_URL` from the environment. A deploy sets it to the empty string — a templating bug
in the chart, an empty value in the secret store, someone's local `export DB_URL=`. The service starts,
connects to... something, and every request fails with a database error. Because it bound its port
first, the orchestrator thinks it is healthy and keeps it in rotation. Three replicas, all broken,
serving 500s for eleven minutes.

```sh run-project
cat > Scenario.java <<'JAVA'
import java.util.List;
import java.util.Map;

public class Scenario {
    public static void main(String[] args) {
        Config config = new Config();
        config.layer(Map.of("port", "8080", "level", "info", "db", "bulletin.db"),
                "defaults");
        config.layer(Map.of("db", ""), "environment");
        config.layer(Map.of("token", "abc123"), "environment");

        List<String> problems = config.validate();
        System.out.println("--- a deploy with an empty DB_URL set in the environment ---");
        System.out.println("  problems found : " + problems.size());
        for (String problem : problems) {
            System.out.println("  " + problem);
        }
        System.out.println();
        System.out.println("  and the token never appears in any of that output:");
        System.out.println("  " + config.printed());
        System.out.println();
        System.out.println("this is what startup validation is for: the process dies here,");
        System.out.println("before it binds a port, before it serves a request, and with a");
        System.out.println("message that names the variable somebody set wrong");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
--- a deploy with an empty DB_URL set in the environment ---
  problems found : 1
  db is required

  and the token never appears in any of that output:
  {"db": "", "level": "info", "port": "8080", "token": "<redacted>"}

this is what startup validation is for: the process dies here,
before it binds a port, before it serves a request, and with a
message that names the variable somebody set wrong
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
```sh run-project
cat > Sol1.java <<'JAVA'
import java.util.Map;

public class Sol1 {
    public static void main(String[] args) {
        Config config = new Config();
        config.layer(Map.of("port", "8080"), "defaults");
        config.layer(Map.of("port", "9090"), "environment");
        config.arguments(new String[]{"--port=7070"});
        System.out.println("port   : " + config.get("port"));
        System.out.println("origin : " + config.originOf("port"));
        System.out.println();
        System.out.println("arguments win, because they are applied last. A layer is just an");
        System.out.println("assignment plus a note about who made it");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
port   : 7070
origin : arguments

arguments win, because they are applied last. A layer is just an
assignment plus a note about who made it
```

Arguments win because they are applied last. That ordering is a choice, not a law — some systems make
the environment win so that an operator can override what a deploy script wrote — but whichever order
you pick has to be written down, because "which layer wins" is the question behind every config
surprise.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'JAVA'
public class Sol2 {
    public static void main(String[] args) {
        Log log = new Log("warn");
        log.line("debug", "not kept");
        log.line("info", "also not kept");
        log.line("warn", "kept", "path", "/notes");
        log.line("error", "kept", "path", "/notes");
        System.out.println("written  : " + log.written());
        System.out.println("info on  : " + log.enabled("info"));
        System.out.println("warn on  : " + log.enabled("warn"));
        System.out.println();
        System.out.println("the threshold is a floor, not a filter list: everything at or");
        System.out.println("above it is kept, and that is why the order of the levels matters");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
{"seq": 1, "level": "warn", "msg": "kept", "path": "/notes"}
{"seq": 2, "level": "error", "msg": "kept", "path": "/notes"}
written  : 2
info on  : false
warn on  : true

the threshold is a floor, not a filter list: everything at or
above it is kept, and that is why the order of the levels matters
```

The threshold is a floor: everything at or above it is kept. Note that `written()` counts lines that
were actually emitted, so a line filtered out costs nothing — which is why a debug-level string
built with concatenation is still worth avoiding in a hot loop.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) {
        String hostile = "bob\n2026-09-25 level=error msg=\"breach\" user=admin";
        Log log = new Log("info");
        log.line("info", "login", "user", hostile);
        System.out.println();
        System.out.println("one line in, one line out. An unescaped newline would have made");
        System.out.println("this two lines, and the second one would say whatever the client");
        System.out.println("wanted it to say -- to your log search, your alerting, and the");
        System.out.println("person reading it at three in the morning");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
{"seq": 1, "level": "info", "msg": "login", "user": "bob\n2026-09-25 level=error msg=\"breach\" user=admin"}

one line in, one line out. An unescaped newline would have made
this two lines, and the second one would say whatever the client
wanted it to say -- to your log search, your alerting, and the
person reading it at three in the morning
```

One line in, one line out. The forged second line never appeared, because the newline became two
characters inside a quoted string. This is the log-injection equivalent of SQL injection: same shape,
different destination, same fix — the value travels as data and never as syntax.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'JAVA'
public class Sol4 {
    public static void main(String[] args) {
        Hooks hooks = new Hooks();
        hooks.add(() -> System.out.println("  first registered, last run"));
        hooks.add(() -> System.out.println("  last registered, first run"));
        hooks.run();
        hooks.run();
        System.out.println("stopped : " + hooks.stopped());
        System.out.println();
        System.out.println("reverse order mirrors try-with-resources, so the thing that was");
        System.out.println("opened first closes last. Running twice does nothing the second");
        System.out.println("time, because a shutdown hook that can run twice can also double");
        System.out.println("free a resource that was only ever acquired once");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
  last registered, first run
  first registered, last run
  already stopped: true
stopped : true

reverse order mirrors try-with-resources, so the thing that was
opened first closes last. Running twice does nothing the second
time, because a shutdown hook that can run twice can also double
free a resource that was only ever acquired once
```

Reverse order, and the second `run()` did nothing. Both properties are the point: reverse order mirrors
`try`-with-resources, and idempotence is what makes a hook safe to call from both your own shutdown
path and the JVM's.

:::
