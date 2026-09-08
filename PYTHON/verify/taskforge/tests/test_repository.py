from datetime import datetime

from taskforge.models import Priority, Status
from taskforge.repository import TaskRepository


def test_project_names_are_unique_per_lookup(repo: TaskRepository) -> None:
    repo.add_project("work")
    assert repo.get_project("work") is not None
    assert repo.get_project("nope") is None


def test_list_tasks_filters_by_tag(repo: TaskRepository) -> None:
    work = repo.add_project("work")
    home = repo.add_project("home")
    report = repo.add_task(work, "Write report", priority=Priority.HIGH)
    repo.add_task(home, "Buy milk")
    report.tags.append(repo.get_or_create_tag("writing"))

    found = repo.list_tasks(project=work, tag="writing")

    assert [t.title for t in found] == ["Write report"]


def test_list_tasks_orders_by_due_date_with_missing_last(repo: TaskRepository) -> None:
    work = repo.add_project("work")
    later = repo.add_task(work, "Later", due_at=datetime(2026, 12, 1))
    sooner = repo.add_task(work, "Sooner", due_at=datetime(2026, 1, 1))
    never = repo.add_task(work, "No date")

    assert [t.id for t in repo.list_tasks(project=work)] == [sooner.id, later.id, never.id]


def test_search_matches_title_and_notes_case_insensitively(repo: TaskRepository) -> None:
    work = repo.add_project("work")
    repo.add_task(work, "Renew passport", notes="bring the old one")

    assert len(repo.list_tasks(project=work, search="PASSPORT")) == 1
    assert len(repo.list_tasks(project=work, search="old one")) == 1
    assert len(repo.list_tasks(project=work, search="visa")) == 0
