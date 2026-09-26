"""Điểm vào dòng lệnh cho Guideline Design Challenge."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List, Optional

from . import LabError
from .calibration import run_calibration
from .catalog import build_split, sample_lines
from .cvat_status import check_cvat
from .freeze import create_handoff, freeze_project, verify_freeze
from .scoring import prepare_score, write_gts
from .status import status_lines


def parser() -> argparse.ArgumentParser:
    """Tạo parser với hướng dẫn tiếng Việt."""
    root = argparse.ArgumentParser(prog="lab9.py", description="Công cụ offline Guideline Design Challenge")
    commands = root.add_subparsers(dest="command", required=True)
    samples = commands.add_parser("samples", help="Liệt kê catalog sample")
    samples.add_argument("--source", choices=("bdd100k", "gtsdb", "lisa"))
    pack = commands.add_parser("pack", help="Dựng thư mục ảnh để upload CVAT")
    pack.add_argument("split", choices=("example", "calibration", "blind"))
    calib = commands.add_parser("calib", help="Đo bất đồng giữa các export calibration")
    calib.add_argument("files", nargs="+", type=Path)
    freeze = commands.add_parser("freeze", help="Kiểm tra và freeze blind gold")
    freeze.add_argument("--refreeze", action="store_true")
    commands.add_parser("verify", help="Xác minh freeze chưa bị sửa")
    commands.add_parser("handoff", help="Tạo blind-pack.zip")
    score = commands.add_parser("score", help="Chuẩn bị transfer_score.csv từ peer export")
    score.add_argument("file", type=Path)
    commands.add_parser("gts", help="Tính Guideline Transferability Score")
    commands.add_parser("status", help="Xem bảng gate G1–G6")
    commands.add_parser("check", help="Kiểm tra đủ cả sáu gate")
    commands.add_parser("cvat", help="Kiểm CVAT đã cài ở Day 2/Day 8 đang chạy")
    return root


def main(argv: Optional[List[str]] = None, base: Optional[Path] = None) -> int:
    """Chạy lệnh; mọi đường dẫn nội bộ bám theo thư mục script."""
    args = parser().parse_args(argv)
    lab_root = (base or Path(__file__).resolve().parents[1]).resolve()
    try:
        if args.command == "samples":
            lines = sample_lines(lab_root, args.source)
            code = 0
        elif args.command == "pack":
            lines = build_split(lab_root, args.split)
            code = 0
        elif args.command == "calib":
            lines = run_calibration(lab_root, [path.resolve() for path in args.files])
            code = 0
        elif args.command == "freeze":
            lines = freeze_project(lab_root, args.refreeze)
            code = 0
        elif args.command == "verify":
            lines, intact = verify_freeze(lab_root)
            code = 0 if intact else 1
        elif args.command == "handoff":
            lines = create_handoff(lab_root)
            code = 0
        elif args.command == "score":
            lines = prepare_score(lab_root, args.file.resolve())
            code = 0
        elif args.command == "gts":
            lines = write_gts(lab_root)
            code = 0
        elif args.command in {"status", "check"}:
            lines, complete = status_lines(lab_root)
            code = 0 if args.command == "status" or complete else 1
        else:
            lines = check_cvat()
            code = 0
    except LabError as error:
        print(f"✗ {error}", file=sys.stderr)
        return 2 if args.command == "cvat" else 1
    for line in lines:
        print(line)
    return code
