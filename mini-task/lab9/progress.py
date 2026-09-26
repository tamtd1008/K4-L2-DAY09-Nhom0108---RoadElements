"""Theo dõi vòng lock → reference → compare → log của từng task."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from . import LabError
from .common import lock_values, nonempty_csv_rows, sha256_file
from .team import mode_line


def task_state(base: Path, config: Dict[str, object], task: str) -> Dict[str, object]:
    """Trả trạng thái bốn bước bắt buộc của một task."""
    directory = base / "submission" / task
    xml_path = directory / "annotations.xml"
    lock_path = directory / "lock.txt"
    locked = False
    if xml_path.is_file() and lock_path.is_file():
        try:
            locked = lock_values(lock_path).get("sha256") == sha256_file(xml_path)
        except LabError:
            locked = False

    rows = 0
    log_path = base / "submission" / "comparison_log.csv"
    if log_path.is_file():
        try:
            _, values = nonempty_csv_rows(log_path)
            rows = sum(row.get("task") == task for row in values)
        except (OSError, csv.Error, UnicodeError):
            rows = 0
    minimum = int(config["logs"]["comparison_log.csv"].get("min_rows_per_task", 0))
    return {
        "lock": locked,
        "reference": (directory / "reference.txt").is_file(),
        "compare": (directory / "compare.md").is_file(),
        "comparison_log": rows >= minimum,
        "comparison_rows": rows,
        "comparison_minimum": minimum,
    }


def _gap_text(task: str, state: Dict[str, object]) -> str:
    missing = []
    if not state["lock"]:
        missing.append("thiếu lock còn nguyên hash")
    if not state["reference"]:
        missing.append("thiếu reference.txt")
    if not state["compare"]:
        missing.append("thiếu compare.md")
    if not state["comparison_log"]:
        missing.append(
            "comparison_log.csv mới có "
            f"{state['comparison_rows']}/{state['comparison_minimum']} dòng"
        )
    return f"{task}: " + ", ".join(missing)


def loop_gaps(base: Path, config: Dict[str, object], task: str) -> List[str]:
    """Liệt kê các vòng chưa xong đứng trước task được yêu cầu."""
    tasks = list(config["task_order"])
    gaps = []
    for earlier in tasks[: tasks.index(task)]:
        state = task_state(base, config, earlier)
        if not all(state[name] for name in ("lock", "reference", "compare", "comparison_log")):
            gaps.append(_gap_text(earlier, state))
    return gaps


def _document_ready(path: Path, marker: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(text.strip()) and marker not in text


def _decision_log_ratified(base: Path) -> bool:
    path = base / "submission" / "decision_log.csv"
    if not path.is_file():
        return False
    try:
        _, rows = nonempty_csv_rows(path)
    except (OSError, csv.Error, UnicodeError):
        return False
    return bool(rows) and all(row.get("status") in {"ratified", "escalated"} for row in rows)


def next_step(base: Path, config: Dict[str, object]) -> str:
    """Chọn đúng một bước tiếp theo từ trạng thái hiện tại."""
    for task in config["task_order"]:
        state = task_state(base, config, task)
        if not state["lock"]:
            return f"make lock TASK={task} FILE=<file export>.zip"
        if not state["reference"]:
            return f"make reference TASK={task}"
        if not state["compare"]:
            return f"make compare TASK={task}"
        if not state["comparison_log"]:
            return (
                f"ghi ít nhất {state['comparison_minimum']} dòng task={task} "
                "vào submission/comparison_log.csv"
            )

    marker = str(config.get("todo_marker", "TODO"))
    for name in ("qc_report.md", "scale_100k.md"):
        if not _document_ready(base / "submission" / name, marker):
            return f"hoàn thành submission/{name}"
    if not _decision_log_ratified(base):
        return "ratify submission/decision_log.csv (status=ratified hoặc escalated)"
    return "make check"


def status_lines(base: Path, config: Dict[str, object]) -> List[str]:
    """Dựng phần hiển thị ngắn cho lệnh status."""
    lines = [mode_line(base)]
    for task in config["task_order"]:
        state = task_state(base, config, task)
        complete = all(state[name] for name in ("lock", "reference", "compare", "comparison_log"))
        lines.append(
            f"{'✓' if complete else '·'} {task}: "
            f"lock {'✓' if state['lock'] else '✗'} · "
            f"reference {'✓' if state['reference'] else '✗'} · "
            f"compare {'✓' if state['compare'] else '✗'} · "
            f"comparison_log.csv {state['comparison_rows']}/{state['comparison_minimum']} "
            f"{'✓' if state['comparison_log'] else '✗'}"
        )
    lines.append(f"→ Bước tiếp theo: {next_step(base, config)}")
    return lines
