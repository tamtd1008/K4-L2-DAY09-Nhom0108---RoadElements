"""Cài ZIP reference vào đúng gt/<task>/ sau khi đã khoá."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional
import zipfile

from . import LabError
from .common import load_lab, lock_values, require_intact_lock

ALLOWED_FILES = {"annotations.xml", "meta.json", "README.md"}


def _members(archive: zipfile.ZipFile, tasks: List[str]) -> Dict[str, Dict[str, zipfile.ZipInfo]]:
    found: Dict[str, Dict[str, zipfile.ZipInfo]] = {}
    for info in archive.infolist():
        if info.is_dir():
            continue
        parts = PurePosixPath(info.filename).parts
        if parts and parts[0] == "Day9-Lab":
            parts = parts[1:]
        if len(parts) != 3 or parts[0] != "gt" or parts[1] not in tasks or parts[2] not in ALLOWED_FILES:
            raise LabError(f"ZIP có file lạ ({info.filename}) — đây không phải ZIP reference của lab.")
        found.setdefault(parts[1], {})[parts[2]] = info
    return found


def _source_text(base: Path, source: Path) -> str:
    try:
        return str(source.relative_to(base))
    except ValueError:
        return str(source)


def _write_open_record(base: Path, task: str, source: Path, lock_sha256: str) -> None:
    path = base / "submission" / task / "reference.txt"
    previous = lock_values(path) if path.is_file() else {}
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    opened_at = previous.get("opened_at", now)
    lines = [f"task: {task}", f"opened_at: {opened_at}"]
    if previous:
        lines.append(f"reopened_at: {now}")
    lines.extend([f"lock_sha256: {lock_sha256}", f"source: {_source_text(base, source)}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_reference(base: Path, task: str, source: Optional[Path] = None) -> List[str]:
    """Giải nén reference của đúng một task, chỉ khi task đó đã khoá."""
    config = load_lab(base)
    if task not in config["task_order"]:
        raise LabError("Task không hợp lệ. Chọn: " + ", ".join(config["task_order"]))
    source = source or (base / "refs" / f"{task}.zip")
    if not source.is_file():
        if source == base / "refs" / f"{task}.zip":
            raise LabError(f"Không thấy refs/{task}.zip — khôi phục bằng git checkout -- refs/{task}.zip.")
        raise LabError(f"Không thấy {source} — kiểm tra đường dẫn ZIP reference.")
    _, _, lock = require_intact_lock(
        base,
        task,
        f"Chưa khoá {task} — chạy make lock TASK={task} FILE=… trước khi mở reference.",
        f"submission/{task}/annotations.xml đã đổi sau khi khoá — chạy lại make lock với đúng file "
        "export đã khoá để khôi phục (sửa tay XML không được tính).",
    )
    try:
        with zipfile.ZipFile(source) as archive:
            found = _members(archive, list(config["task_order"]))
            if len(found) != 1:
                raise LabError("ZIP reference phải chứa đúng một task.")
            archive_task, files = next(iter(found.items()))
            if archive_task != task:
                raise LabError(f"ZIP reference không khớp task {task}.")
            if "annotations.xml" not in files:
                raise LabError(f"ZIP reference {task} thiếu annotations.xml.")
            target = base / "gt" / task
            target.mkdir(parents=True, exist_ok=True)
            for name in ALLOWED_FILES - set(files):
                stale = target / name
                if stale.is_file():
                    stale.unlink()
            for name, info in files.items():
                (target / name).write_bytes(archive.read(info))
    except zipfile.BadZipFile as error:
        raise LabError(f"{source.name} không phải ZIP hợp lệ — lấy lại ZIP reference.") from error
    _write_open_record(base, task, source, lock.get("sha256", ""))
    return [
        f"✓ Đã cài reference {task} vào gt/{task}/",
        f"→ Chạy tiếp: make compare TASK={task}",
    ]
