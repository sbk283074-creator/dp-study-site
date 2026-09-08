from __future__ import annotations

from typer.testing import CliRunner

from taskforge.cli import app

runner = CliRunner()


def test_add_then_list_shows_the_task(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TASKFORGE_DB", f"sqlite:///{tmp_path / 'cli.db'}")
    monkeypatch.setenv("TASKFORGE_LOG", str(tmp_path / "cli.log"))

    added = runner.invoke(
        app, ["add", "Write the report", "--project", "work", "--priority", "high"]
    )
    assert added.exit_code == 0, added.output
    assert "Write the report" in added.output

    listed = runner.invoke(app, ["list", "--project", "work"])
    assert listed.exit_code == 0, listed.output
    assert "Write the report" in listed.output


def test_unknown_task_exits_non_zero(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TASKFORGE_DB", f"sqlite:///{tmp_path / 'cli.db'}")
    monkeypatch.setenv("TASKFORGE_LOG", str(tmp_path / "cli.log"))

    result = runner.invoke(app, ["done", "999"])

    assert result.exit_code == 1
    assert "no task with id #999" in result.output
