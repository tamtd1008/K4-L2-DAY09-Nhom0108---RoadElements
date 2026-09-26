"""Tiện ích file dùng chung cho Guideline Design Challenge."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from . import LabError


def read_json(path: Path) -> Any:
    """Đọc JSON UTF-8 và đổi lỗi thành thông báo ngắn."""
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, ValueError) as error:
        raise LabError(f"Không đọc được {path}: {error}") from error


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    """Đọc CSV, chuẩn hoá khoảng trắng và bỏ dòng hoàn toàn rỗng."""
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            header = list(reader.fieldnames or [])
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
    except OSError as error:
        raise LabError(f"Không đọc được {path}: {error}") from error


def require_columns(path: Path, header: Iterable[str], expected: Iterable[str]) -> None:
    """Báo lỗi khi CSV thiếu cột bắt buộc."""
    missing = [name for name in expected if name not in header]
    if missing:
        raise LabError(f"{path} thiếu cột: {', '.join(missing)}.")


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Dict[str, object]]) -> None:
    """Ghi CSV UTF-8 với CRLF ổn định."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_text(data: bytes) -> str:
    """SHA-256 của nội dung text với CRLF quy về LF.

    Git for Windows (autocrlf) lưu LF nhưng checkout CRLF, nên cùng một commit cho byte khác nhau trên Windows
    và macOS. Chuẩn hoá xuống dòng để FREEZE.txt ghi trên máy này vẫn khớp clone trên máy kia.
    """
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sha256_text_file(path: Path) -> str:
    """sha256_text của một file."""
    try:
        data = path.read_bytes()
    except OSError as error:
        raise LabError(f"Không đọc được {path}: {error}") from error
    return sha256_text(data)


def challenge_config(base: Path) -> Dict[str, Any]:
    """Đọc challenge.json ở gốc repo học viên."""
    path = base / "challenge.json"
    if not path.is_file():
        raise LabError("Thiếu challenge.json — khôi phục file từ repo gốc.")
    config = read_json(path)
    if not isinstance(config, dict) or not isinstance(config.get("enums"), dict):
        raise LabError("challenge.json không đúng định dạng.")
    return config


def project_path(base: Path, relative: str) -> Path:
    """Trả đường dẫn trong project/."""
    return base / "project" / relative


def is_filled(path: Path) -> bool:
    """Template được điền khi tồn tại và không còn token TODO."""
    try:
        return path.is_file() and "TODO" not in path.read_text(encoding="utf-8")
    except OSError:
        return False


def parse_key_values(path: Path) -> Dict[str, str]:
    """Đọc file key=value, bỏ dòng trống và comment."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise LabError(f"Không đọc được {path}: {error}") from error
    values: Dict[str, str] = {}
    for line in lines:
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values
