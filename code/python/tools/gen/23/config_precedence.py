"""Chapter 23 -- configuration comes from four places, and one of them wins.

One setting table with defaults, a config file, the environment and a
command-line flag all naming values. The count is of keys defined in more than
one place, which is where the surprises live.
"""

DEFAULTS = {"db": "sqlite:///tasks.db", "log": "info", "workers": "1",
            "timeout": "30"}
FROM_FILE = {"log": "debug", "workers": "4"}
FROM_ENV = {"workers": "8", "timeout": "60"}
FROM_FLAGS = {"workers": "16"}

SOURCES = [
    ("default", DEFAULTS),
    ("file", FROM_FILE),
    ("environment", FROM_ENV),
    ("flag", FROM_FLAGS),
]

KEYS = sorted(DEFAULTS)


def resolve(key):
    winner = "default"
    value = DEFAULTS[key]
    for label, source in SOURCES[1:]:
        if key in source:
            winner = label
            value = source[key]
    return value, winner


def places(key):
    return sum(1 for _, source in SOURCES if key in source)


rows = [(key, resolve(key)[0], resolve(key)[1], places(key)) for key in KEYS]

print(f"{len(KEYS)} settings, read from {len(SOURCES)} places in a fixed order")
print()
print(f"{'key':<10}{'resolved value':<24}{'came from':>14}{'set in':>8}")
print("-" * 56)
for key, value, source, count in rows:
    print(f"{key:<10}{value:<24}{source:>14}{count:>8}")

print()
print(f"{'what is counted':<40}{'count':>8}")
print("-" * 52)
print(f"{'settings resolved':<40}{len(rows):>8}")
print(f"{'settings defined in more than one place':<40}"
      f"{sum(1 for r in rows if r[3] > 1):>8}")
print(f"{'settings whose winner was not the default':<40}"
      f"{sum(1 for r in rows if r[2] != 'default'):>8}")
print(f"{'settings whose winner was the last source':<40}"
      f"{sum(1 for r in rows if r[2] == SOURCES[-1][0]):>8}")

print()
print("The order is the whole design, and it is fixed: default, then file, then")
print("environment, then flag. Each source that names a key replaces the one")
print("before it, so the thing typed on this command line always wins -- which")
print("is what makes a flag useful for the one run that is different.")
print()
print("The 'set in' column is where it goes wrong.")
print(f"{sum(1 for r in rows if r[3] > 1)} of these {len(rows)} keys are named in more than one place, and the")
print(f"busiest of them is named in {max(r[3] for r in rows)}. A key that appears four times has four")
print("candidate answers, and nothing about the key itself says which one won.")
print("You have to know the precedence order -- and the precedence order is not")
print("written in the config file the reader is looking at.")
print()
print("So make the resolved configuration printable, and print it at startup")
print("in the log. The question 'which value is it actually using' should be")
print("answerable from the log of the run, not from reading four files and")
print("knowing the precedence order by heart. And keep the number of sources")
print("small: every place a setting can come from is a place a bug can hide,")
print("and a settings system with five sources is a settings system nobody can")
print("debug at 3am.")
