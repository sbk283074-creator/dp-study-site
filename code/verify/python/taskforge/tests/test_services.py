from datetime import datetime, timedelta

import pytest

from taskforge.models import Priority, Status
from taskforge.services import (
    ProjectArchivedError,
    TaskService,
    ValidationError,
    is_overdue,
)


def test_create_task_makes_the_project_on_demand(service: TaskService) -> None:
    task = service.create_task("home", "Buy paint", priority=Priority.LOW)

    assert task.project.name == "home"
    assert task.priority is Priority.LOW
    assert task.status is Status.TODO


def test_blank_title_is_rejected(service: TaskService) -> None:
    with pytest.raises(ValidationError):
        service.create_task("home", "   ")


def test_completing_a_task_stamps_completed_at(service: TaskService) -> None:
    task = service.create_task("work", "Ship it")

    done = service.complete_task(task.id)

    assert done.status is Status.DONE
    assert done.completed_at is not None


def test_cannot_complete_a_task_in_an_archived_project(service: TaskService) -> None:
    task = service.create_task("work", "Old thing")
    service.archive_project("work")

    with pytest.raises(ProjectArchivedError):
        service.complete_task(task.id)


def test_overdue_uses_date_not_time(service: TaskService) -> None:
    today = service.create_task("work", "Today", due_at=datetime(2026, 9, 7))
    last_week = service.create_task("work", "Late", due_at=datetime(2026, 9, 1))
    now = datetime(2026, 9, 7, 23, 59)

    assert not is_overdue(today, now)  # due today is not overdue at 23:59
    assert is_overdue(last_week, now)


def test_find_sorts_urgent_first(service: TaskService) -> None:
    service.create_task("work", "Meh", priority=Priority.LOW)
    service.create_task("work", "Now", priority=Priority.URGENT)
    service.create_task("work", "Soon", priority=Priority.HIGH)

    titles = [t.title for t in service.find()]

    assert titles == ["Now", "Soon", "Meh"]


def test_weekly_report_counts_created_and_completed(service: TaskService) -> None:
    task = service.create_task("work", "Older")
    service.complete_task(task.id)
    service.create_task("work", "Fresh")

    result = service.weekly_report(days=7, now=datetime(2026, 9, 7, 12, 0))

    assert result.created == 2
    assert result.completed == 1


def test_reopen_clears_completed_at(service: TaskService) -> None:
    task = service.create_task("work", "Ship it")
    service.complete_task(task.id)

    reopened = service.reopen_task(task.id)

    assert reopened.status is Status.TODO
    assert reopened.completed_at is None


def test_export_then_import_round_trips(service: TaskService) -> None:
    service.create_task("work", "Write docs", tags=["writing"])

    payload = service.export_data()
    result = service.import_data(payload, merge=False)

    assert result.tasks == 1
    assert [t.title for t in service.find(include_done=True)] == [
        "Write docs",
        "Write docs",
    ]
