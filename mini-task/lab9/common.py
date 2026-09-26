"""Đọc cấu hình và các file chung của lab."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from . import LabError, TASKS


def read_json(path: Path) -> Dict[str, Any]:
    """Đọc JSON UTF-8 và đổi lỗi thành hướng dẫn ngắn."""
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, ValueError) as error:
        raise LabError(f"Không đọc được {path}: {error}") from error


def nonempty_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    """Đọc CSV và bỏ các dòng hoàn toàn rỗng theo cùng một quy tắc."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames or []
        rows = []
        for row in reader:
            normalized = {
                str(key): (";".join(value) if isinstance(value, list) else (value or "")).strip()
                for key, value in row.items()
                if key is not None
            }
            if any(normalized.values()):
                rows.append(normalized)
        return header, rows


def load_lab(base: Path) -> Dict[str, Any]:
    """Đọc lab.json cạnh chương trình."""
    path = base / "lab.json"
    if not path.is_file():
        raise LabError("Thiếu lab.json — khôi phục bằng git checkout -- lab.json.")
    config = read_json(path)
    if tuple(config.get("task_order", ())) != TASKS:
        raise LabError("lab.json không đúng bộ task Day 9 — khôi phục bằng git checkout -- lab.json.")
    return config


def load_manifest(base: Path) -> Dict[str, Any]:
    """Đọc manifest media của repo học viên."""
    path = base / "data" / "manifest.json"
    if not path.is_file():
        raise LabError("Thiếu data/manifest.json — khôi phục bằng git checkout -- data/manifest.json.")
    return read_json(path)


def require_task(task: str, config: Dict[str, Any]) -> None:
    """Kiểm tra task từ dòng lệnh."""
    if task not in config.get("task_order", []):
        raise LabError("Task không hợp lệ. Chọn: " + ", ".join(config.get("task_order", TASKS)))


def sha256_file(path: Path) -> str:
    """Tính SHA-256 theo luồng để dùng được với export lớn."""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise LabError(f"Không đọc được {path}: {error}") from error
    return digest.hexdigest()


def lock_values(path: Path) -> Dict[str, str]:
    """Đọc các dòng key: value ở phần hiện tại của lock.txt."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise LabError(f"Không đọc được {path}: {error}") from error
    values: Dict[str, str] = {}
    for line in lines:
        if line == "history:":
            break
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def require_intact_lock(
    base: Path,
    task: str,
    missing_message: str,
    changed_message: str,
) -> Tuple[Path, Path, Dict[str, str]]:
    """Trả file XML/lock khi bài đã khoá còn nguyên vẹn."""
    submission = base / "submission" / task
    lock_path = submission / "lock.txt"
    locked_xml = submission / "annotations.xml"
    if not lock_path.is_file() or not locked_xml.is_file():
        raise LabError(missing_message)
    values = lock_values(lock_path)
    if values.get("sha256") != sha256_file(locked_xml):
        raise LabError(changed_message)
    return locked_xml, lock_path, values
