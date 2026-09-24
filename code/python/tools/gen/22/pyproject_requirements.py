"""Chapter 22 -- what a pyproject.toml actually declares.

One manifest with a required list and three optional extras. The count is of
distributions a plain install pulls, against the same manifest with extras asked
for, and of the requirements that carry an upper bound.
"""

import tomllib

MANIFEST = """
[project]
name = "taskforge"
version = "0.4.1"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27,<1",
    "click>=8.1",
    "pydantic>=2.6,<3",
]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.5"]
docs = ["mkdocs>=1.6", "mkdocs-material>=9"]
postgres = ["psycopg[binary]>=3.1"]
"""

project = tomllib.loads(MANIFEST)["project"]
required = project["dependencies"]
extras = project["optional-dependencies"]

STOPS = "[<>=!~ "


def name_of(requirement):
    """The distribution name, with any extras and any version specifier removed."""
    for stop in STOPS:
        position = requirement.find(stop)
        if position != -1:
            requirement = requirement[:position]
    return requirement


def install_size(wanted):
    total = len(required)
    for extra in wanted:
        total += len(extras[extra])
    return total


every = sorted(extras)

print(f"one manifest, {len(required)} required and {len(extras)} extras")
print()
print(f"{'extra':<14}{'distributions':>15}   {'names'}")
print("-" * 60)
for extra in every:
    names = ", ".join(name_of(item) for item in extras[extra])
    print(f"{extra:<14}{len(extras[extra]):>15}   {names}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'required distributions':<46}{len(required):>8}")
print(f"{'extras declared':<46}{len(extras):>8}")
print(f"{'optional distributions in total':<46}"
      f"{sum(len(v) for v in extras.values()):>8}")
print(f"{'install with no extras':<46}{install_size([]):>8}")
print(f"{'install with dev':<46}{install_size(['dev']):>8}")
print(f"{'install with dev and docs':<46}{install_size(['dev', 'docs']):>8}")
print(f"{'install with every extra':<46}{install_size(every):>8}")

all_requirements = list(required) + [item for extra in every for item in extras[extra]]
bounded = [item for item in all_requirements if "<" in item]

print()
print(f"{'requirements declared in all':<46}{len(all_requirements):>8}")
print(f"{'requirements with an upper bound':<46}{len(bounded):>8}")
print(f"{'requirements with only a lower bound':<46}"
      f"{len(all_requirements) - len(bounded):>8}")

print()
print("The install counts are the reason extras exist. A plain install pulls")
print(f"{install_size([])} distributions and nothing else, so a user who only wants the library")
print(f"does not get a test runner. Asking for dev takes it to {install_size(['dev'])},")
print(f"and asking for everything takes it to {install_size(every)} -- more than twice the")
print("required set, all of it declared, none of it guessed. The alternative")
print("is a requirements.txt with everything in it and a README that says")
print("'ignore the ones you do not need', which is a list nobody can check.")
print()
print("The last two rows are the judgement call, and the answer differs by what")
print("you are writing. A library should carry an upper bound only where it")
print("knows it will break -- which is why two of these do, on the two")
print("packages whose next major version is a rewrite. An application should")
print("pin everything, because an application is deployed once and read by")
print("nobody; a library that pins everything is a library nobody can upgrade.")
print()
print("The mechanism is one file. `requires-python` says which interpreters are")
print("supported, `dependencies` says what is always needed, and each extra is")
print("a named group the user opts into. That is the whole contract, and it is")
print("declarative -- the installer reads it, so it cannot drift from what the")
print("README claims.")
