"""Typer front end: parse arguments, call a service, print the result."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from taskforge import __version__
from taskforge.config import Settings
from taskforge.dates import parse_due
from taskforge.db import create_engine_from_settings, init_db, make_session_factory, session_scope
from taskforge.logging_setup import configure_logging
from taskforge.models import Priority, Status
from taskforge.repository import TaskRepository
from taskforge.services import TaskForgeError, TaskService, is_overdue

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="TaskForge - a task manager for your terminal.",
)
project_app = typer.Typer(no_args_is_help=True, help="Create and manage projects.")
app.add_typer(project_app, name="project")

console = Console(width=120)
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"taskforge {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Log debug detail to stderr and the log file."
    ),
    version: bool | None = typer.Option(
        None, "--version", callback=_version_callback, is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """TaskForge: projects, tasks, tags, due dates and reports."""
    settings = Settings.from_env()
    configure_logging(settings.log_path, verbose=verbose)
    engine = create_engine_from_settings(settings)
    init_db(engine)
    ctx.obj = {"session_factory": make_session_factory(engine), "settings": settings}


@contextmanager
def task_service(ctx: typer.Context) -> Iterator[TaskService]:
    """Open a transaction, hand over a service, and translate errors to exit codes."""
    with session_scope(ctx.obj["session_factory"]) as session:
        try:
            yield TaskService(TaskRepository(session))
        except TaskForgeError as exc:
            err_console.print(f"[bold red]error:[/bold red] {exc}")
            raise typer.Exit(code=1) from exc


@app.command()
def add(
    ctx: typer.Context,
    title: str = typer.Argument(..., help="What needs doing."),
    project: str = typer.Option("inbox", "--project", "-p", help="Project (created if new)."),
    priority: Priority = typer.Option(Priority.MEDIUM, "--priority", help="low|medium|high|urgent"),
    due: str | None = typer.Option(None, "--due", "-d", help="today, tomorrow, +3d or YYYY-MM-DD."),
    tag: list[str] | None = typer.Option(None, "--tag", "-t", help="Repeatable."),
    notes: str = typer.Option("", "--notes", "-n", help="Free-text detail."),
) -> None:
    """Create a task."""
    due_at = parse_due(due) if due else None
    with task_service(ctx) as service:
        task = service.create_task(
            project_name=project,
            title=title,
            notes=notes,
            priority=priority,
            due_at=due_at,
            tags=tag or (),
        )
        console.print(
            f"[green]added[/green] #{task.id} {task.title} "
            f"in [bold]{task.project.name}[/bold]"
        )


@app.command("list")
def list_tasks(
    ctx: typer.Context,
    project: str | None = typer.Option(None, "--project", "-p"),
    status: Status | None = typer.Option(None, "--status", "-s"),
    priority: Priority | None = typer.Option(None, "--priority"),
    tag: str | None = typer.Option(None, "--tag", "-t"),
    search: str | None = typer.Option(None, "--search", "-q", help="Match title or notes."),
    overdue: bool = typer.Option(False, "--overdue", help="Only tasks past their due date."),
    show_done: bool = typer.Option(False, "--done", help="Include completed tasks."),
) -> None:
    """List tasks, most urgent first."""
    with task_service(ctx) as service:
        tasks = service.find(
            project_name=project,
            status=status,
            priority=priority,
            tag=tag,
            search=search,
            overdue_only=overdue,
            include_done=show_done,
        )
        table = Table(title=f"{len(tasks)} task(s)")
        table.add_column("ID", style="dim", justify="right")
        table.add_column("Title")
        table.add_column("Project")
        table.add_column("Pri")
        table.add_column("Due")
        table.add_column("Tags")
        for task in tasks:
            due = task.due_at.date().isoformat() if task.due_at else ""
            if task.due_at and is_overdue(task):
                due = f"[red]{due}[/red]"
            table.add_row(
                str(task.id),
                task.title,
                task.project.name,
                task.priority.value,
                due,
                ", ".join(sorted(t.name for t in task.tags)),
            )
    console.print(table)


@app.command()
def done(ctx: typer.Context, task_id: int = typer.Argument(..., help="Task id from `list`.")) -> None:
    """Mark a task complete."""
    with task_service(ctx) as service:
        task = service.complete_task(task_id)
    console.print(f"[green]done[/green] #{task.id} {task.title}")


@app.command()
def reopen(ctx: typer.Context, task_id: int = typer.Argument(...)) -> None:
    """Undo a completion."""
    with task_service(ctx) as service:
        task = service.reopen_task(task_id)
    console.print(f"[cyan]reopened[/cyan] #{task.id} {task.title}")


@app.command()
def rm(ctx: typer.Context, task_id: int = typer.Argument(...)) -> None:
    """Delete a task."""
    with task_service(ctx) as service:
        task = service.delete_task(task_id)
    console.print(f"[yellow]removed[/yellow] #{task.id} {task.title}")


@app.command()
def tag(
    ctx: typer.Context,
    task_id: int = typer.Argument(...),
    names: list[str] = typer.Argument(..., help="One or more tag names."),
) -> None:
    """Add tags to a task."""
    with task_service(ctx) as service:
        task = service.tag_task(task_id, *names)
    console.print(f"[green]tagged[/green] #{task.id}: {', '.join(t.name for t in task.tags)}")


@app.command()
def report(
    ctx: typer.Context,
    days: int = typer.Option(7, "--days", min=1, max=90),
    week: bool = typer.Option(False, "--week", help="Shorthand for --days 7."),
) -> None:
    """Summarise the last N days."""
    if week:
        days = 7
    with task_service(ctx) as service:
        result = service.weekly_report(days=days)
        table = Table(title=f"Last {days} days")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        table.add_row("Created", str(result.created))
        table.add_row("Completed", str(result.completed))
        table.add_row("Overdue now", str(len(result.overdue)))
        for priority, count in sorted(result.by_priority.items()):
            table.add_row(f"Open ({priority.value})", str(count))
    console.print(table)


@app.command()
def export(ctx: typer.Context, path: Path = typer.Argument(..., help="Destination .json file.")) -> None:
    """Write the whole database to JSON."""
    with task_service(ctx) as service:
        payload = service.export_data()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"[green]exported[/green] {len(payload['projects'])} project(s) to {path}")


@app.command("import")
def import_data(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Source .json file."),
    merge: bool = typer.Option(True, "--merge/--replace", help="Skip tasks that already exist."),
) -> None:
    """Load tasks from a TaskForge JSON export."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    with task_service(ctx) as service:
        result = service.import_data(payload, merge=merge)
    console.print(
        f"[green]imported[/green] {result.projects} project(s), "
        f"{result.tasks} task(s), {result.skipped} skipped"
    )


@project_app.command("add")
def project_add(
    ctx: typer.Context,
    name: str = typer.Argument(...),
    description: str = typer.Option("", "--description", "-d"),
) -> None:
    """Create a project."""
    with task_service(ctx) as service:
        project = service.create_project(name, description)
    console.print(f"[green]created[/green] project [bold]{project.name}[/bold]")


@project_app.command("list")
def project_list(
    ctx: typer.Context,
    show_archived: bool = typer.Option(False, "--all", "-a", help="Include archived projects."),
) -> None:
    """List projects with task counts."""
    with task_service(ctx) as service:
        projects = service.list_projects(include_archived=show_archived)
        table = Table(title="Projects")
        table.add_column("Name")
        table.add_column("Open", justify="right")
        table.add_column("Archived")
        for project in projects:
            open_count = sum(1 for t in project.tasks if t.status is Status.TODO)
            table.add_row(project.name, str(open_count), "yes" if project.archived else "")
    console.print(table)


@project_app.command("archive")
def project_archive(ctx: typer.Context, name: str = typer.Argument(...)) -> None:
    """Archive a project; its tasks become read-only."""
    with task_service(ctx) as service:
        project = service.archive_project(name)
    console.print(f"[yellow]archived[/yellow] [bold]{project.name}[/bold]")


@project_app.command("rm")
def project_rm(
    ctx: typer.Context,
    name: str = typer.Argument(...),
    force: bool = typer.Option(False, "--force", "-f", help="Do not ask for confirmation."),
) -> None:
    """Delete a project and all of its tasks."""
    if not force:
        typer.confirm(f"Delete project {name!r} and all its tasks?", abort=True)
    with task_service(ctx) as service:
        service.delete_project(name)
    console.print(f"[yellow]deleted[/yellow] project {name}")


if __name__ == "__main__":
    app()
