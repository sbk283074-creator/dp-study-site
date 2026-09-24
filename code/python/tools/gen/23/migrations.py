"""Chapter 23 -- a migration is applied once, and the record is what makes it so.

Three schema changes applied by a runner that remembers what it has done. The
count is of migrations run, and of the work a second run does when there is
nothing left to do.
"""

import sqlite3

MIGRATIONS = [
    ("001_create_tasks", "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT)"),
    ("002_add_done", "ALTER TABLE tasks ADD COLUMN done INTEGER DEFAULT 0"),
    ("003_add_project", "ALTER TABLE tasks ADD COLUMN project TEXT"),
]


def connect():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE schema_version (name TEXT PRIMARY KEY)")
    return connection


def applied(connection):
    return {row[0] for row in connection.execute("SELECT name FROM schema_version")}


def columns(connection):
    return [row[1] for row in connection.execute("PRAGMA table_info(tasks)")]


def migrate(connection):
    ran = 0
    done = applied(connection)
    for name, sql in MIGRATIONS:
        if name in done:
            continue
        connection.execute(sql)
        connection.execute("INSERT INTO schema_version VALUES (?)", (name,))
        connection.commit()
        ran += 1
    return ran


connection = connect()
first = migrate(connection)
after_first = list(columns(connection))
second = migrate(connection)
third = migrate(connection)
recorded = sorted(applied(connection))

print(f"{len(MIGRATIONS)} migrations, applied by a runner that keeps a record")
print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'migrations defined':<46}{len(MIGRATIONS):>8}")
print(f"{'migrations applied on the first run':<46}{first:>8}")
print(f"{'migrations applied on the second run':<46}{second:>8}")
print(f"{'migrations applied on the third run':<46}{third:>8}")
print(f"{'versions recorded in the schema table':<46}{len(recorded):>8}")
print(f"{'columns in tasks at the end':<46}{len(after_first):>8}")
print()
print(f"columns in tasks: {', '.join(after_first)}")
print(f"recorded versions: {', '.join(recorded)}")

print()
print("The second and third rows are the property that matters. Running the")
print("runner twice is the same as running it once, because each migration")
print("checks the record before it does anything. That is what makes it safe")
print("to call at startup, in a deploy script, and again by hand when somebody")
print("is not sure whether it ran -- which is the situation that actually")
print("happens.")
print()
print(f"The column count is the other half. Three migrations produced")
print(f"{len(after_first)} columns, because a migration adds to the schema rather than")
print("replacing it. The schema in production is the sum of every migration")
print("that has ever run, and the only description of it that is true is the")
print("list of files plus the record of which ones ran.")
print()
print("Which is why a migration that has already run must never be edited. The")
print("record says it is done, so the change never executes again, and the")
print("file on disk stops describing the database it created. Add a fourth")
print("migration instead: a wrong migration that has run is history, and")
print("history is corrected by what comes after it.")
