"""Điểm vào dòng lệnh cho các thao tác offline của lab."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List, Optional

from . import LabError
from .common import load_lab
from .compare import run_compare
from .cvat_status import check_cvat
from .locking import lock_export
from .peer import run_peer
from .progress import status_lines
from .reference import install_reference
from .submission import check_submission
from .team import configure_team


def parser() -> argparse.ArgumentParser:
    """Tạo parser với hướng dẫn tiếng Việt."""
    root = argparse.ArgumentParser(prog="lab9.py", description="Công cụ offline cho lab Day 9")
    commands = root.add_subparsers(dest="command", required=True)
    lock = commands.add_parser("lock", help="Khoá một export CVAT")
    lock.add_argument("task")
    lock.add_argument("file", type=Path)
    lock.add_argument("--relock", action="store_true", help="Khoá lại khi chủ động thay file")
    reference = commands.add_parser("reference", help="Mở reference (refs/<task>.zip) sau khi đã khoá")
    reference.add_argument("task")
    reference.add_argument("--file", type=Path, help="ZIP reference ngoài workspace")
    peer = commands.add_parser("peer", help="So với file đã khoá của bạn cùng nhóm")
    peer.add_argument("task")
    peer.add_argument("--file", type=Path, required=True)
    peer.add_argument("--code", required=True)
    peer.add_argument("--name", required=True)
    team = commands.add_parser("team", help="Xem hoặc đặt chế độ nhóm")
    team.add_argument("--members", help="2–4 tên, ngăn cách bằng dấu phẩy")
    compare = commands.add_parser("compare", help="So với reference đã mở")
    compare.add_argument("task")
    commands.add_parser("cvat", help="Kiểm CVAT đã cài ở Day 2/Day 8 đang chạy")
    commands.add_parser("check", help="Kiểm tra submission đủ file")
    commands.add_parser("status", help="Xem tiến độ và đúng một bước tiếp theo")
    return root


def main(argv: Optional[List[str]] = None, base: Optional[Path] = None) -> int:
    """Chạy lệnh; mọi đường dẫn nội bộ bám theo thư mục script."""
    args = parser().parse_args(argv)
    lab_root = (base or Path(__file__).resolve().parents[1]).resolve()
    try:
        if args.command == "lock":
            lines = lock_export(lab_root, args.task, args.file.resolve(), args.relock)
            code = 0
        elif args.command == "reference":
            source = args.file.resolve() if args.file else None
            lines = install_reference(lab_root, args.task, source)
            code = 0
        elif args.command == "peer":
            lines = run_peer(lab_root, args.task, args.file.resolve(), args.code, args.name)
            code = 0
        elif args.command == "team":
            lines = configure_team(lab_root, args.members)
            code = 0
        elif args.command == "compare":
            lines = run_compare(lab_root, args.task)
            code = 0
        elif args.command == "cvat":
            lines = check_cvat()
            code = 0
        elif args.command == "status":
            lines = status_lines(lab_root, load_lab(lab_root))
            code = 0
        else:
            lines, gaps = check_submission(lab_root)
            code = 1 if gaps else 0
    except LabError as error:
        print(f"✗ {error}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return code
