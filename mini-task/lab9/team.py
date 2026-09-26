"""Cấu hình chế độ cá nhân hoặc nhóm cho lab."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import List, Optional

from . import LabError
from .common import read_json


def load_team(base: Path) -> List[str]:
    """Đọc team.json; không có file nghĩa là chế độ cá nhân."""
    path = base / "team.json"
    if not path.is_file():
        return []
    payload = read_json(path)
    members = payload.get("members")
    if not isinstance(members, list) or not all(isinstance(name, str) and name.strip() for name in members):
        raise LabError("team.json không hợp lệ — chạy lại make team MEMBERS=\"An, Bình\".")
    normalized = [name.strip() for name in members]
    if not 2 <= len(normalized) <= 4 or len({name.casefold() for name in normalized}) != len(normalized):
        raise LabError("team.json phải có 2–4 tên khác nhau — chạy lại make team MEMBERS=\"An, Bình\".")
    return normalized


def mode_line(base: Path) -> str:
    """Mô tả chế độ hiện tại bằng một dòng."""
    members = load_team(base)
    return f"Chế độ: nhóm ({', '.join(members)})" if members else "Chế độ: cá nhân"


def configure_team(base: Path, raw_members: Optional[str]) -> List[str]:
    """Ghi team.json hoặc chỉ in chế độ hiện tại."""
    if raw_members is None:
        return [mode_line(base)]
    members = [name.strip() for name in raw_members.split(",")]
    if not 2 <= len(members) <= 4 or any(not name for name in members):
        raise LabError("Nhóm phải có 2–4 tên không rỗng, ngăn cách bằng dấu phẩy.")
    if len({name.casefold() for name in members}) != len(members):
        raise LabError("Tên thành viên trong nhóm phải khác nhau.")
    payload = {
        "members": members,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    (base / "team.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [mode_line(base)]
