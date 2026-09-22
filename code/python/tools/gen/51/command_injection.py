#!/usr/bin/env python3
"""Chapter 51 demo, part 3 -- which of these five call sites is dangerous?

The received wisdom is "do not use a string with the shell". That is half of
it, and the half that is easy to state is not the half that matters: a list of
arguments is not safe if the shell is still in the pipeline, and a string is
safe if it never reaches one.

So this script measures it instead of asserting it. Every payload is harmless
-- they run `echo` -- and the test is whether a line of output is *exactly* the
marker, which is the difference between a command that ran and a command that
was echoed as text.

Five call sites, eight payloads.
"""
import shlex
import subprocess

MARKER = "INJECTED"

PAYLOADS = [
    "notes.txt",
    "notes.txt; echo INJECTED",
    "notes.txt && echo INJECTED",
    "notes.txt | echo INJECTED",
    "$(echo INJECTED)",
    "`echo INJECTED`",
    "notes.txt\necho INJECTED",
    "notes'.txt",
]


def ran_marker(result):
    """Did a *command* run, or was the marker just echoed as text?"""
    return MARKER in (result.stdout or "").splitlines()


def shell_fstring(name):
    return subprocess.run(f"echo {name}", shell=True,
                          capture_output=True, text=True)


def list_no_shell(name):
    return subprocess.run(["echo", name], shell=False,
                          capture_output=True, text=True)


def shell_quoted(name):
    return subprocess.run(f"echo {shlex.quote(name)}", shell=True,
                          capture_output=True, text=True)


def list_with_shell(name):
    return subprocess.run(["echo", name], shell=True,
                          capture_output=True, text=True)


def list_first_arg(name):
    """shell=True with a sequence: argv[0] is the command string."""
    return subprocess.run([f"echo {name}"], shell=True,
                          capture_output=True, text=True)


def explicit_sh(name):
    return subprocess.run(["sh", "-c", f"echo {name}"], shell=False,
                          capture_output=True, text=True)


SITES = [
    ("f-string, shell=True", shell_fstring),
    ("list, shell=False", list_no_shell),
    ("shlex.quote, shell=True", shell_quoted),
    ("list, shell=True, payload in argv[1]", list_with_shell),
    ("list, shell=True, payload in argv[0]", list_first_arg),
    ("['sh','-c', f-string], shell=False", explicit_sh),
]


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  the test is whether a line equals  {MARKER!r}")
    print()
    print(f"    {'call site':<42}{'payloads that ran':>18}{'safe?':>8}")
    for label, fn in SITES:
        hits = 0
        for p in PAYLOADS:
            try:
                if ran_marker(fn(p)):
                    hits += 1
            except OSError:
                pass
        safe = hits == 0
        print(f"    {label:<42}{hits:>18}{('yes' if safe else 'NO'):>8}")

    print()
    print(f"  of {len(PAYLOADS)} payloads, a call site that never reaches a shell")
    print("  runs 0 of them, whichever way the arguments were written.")
    print()
    print("  the two shell=True rows differ only in which argument the payload")
    print("  occupies, and they differ by every payload in the set.")


if __name__ == "__main__":
    main()
