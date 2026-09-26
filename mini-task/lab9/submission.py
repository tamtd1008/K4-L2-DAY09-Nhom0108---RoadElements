"""Kiểm tra submission đủ file và đúng cấu trúc tối thiểu."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from . import LabError
from .common import load_lab, lock_values, nonempty_csv_rows, read_json, sha256_file
from .cvat_xml import parse_bytes
from .provenance import display_tolerance, export_meta, identical_shapes, source_counts
from .team import load_team, mode_line


def _check_tasks(base: Path, config: Dict[str, object]) -> Tuple[List[str], bool]:
    lines: List[str] = []
    gaps = False
    for task in config["task_order"]:
        directory = base / "submission" / task
        xml_path, lock_path = directory / "annotations.xml", directory / "lock.txt"
        required = (xml_path, lock_path, directory / "reference.txt", directory / "compare.md")
        missing = [path.name for path in required if not path.is_file()]
        if missing:
            lines.append(f"✗ {task}: thiếu " + ", ".join(missing))
            gaps = True
            continue
        values = lock_values(lock_path)
        if values.get("sha256") != sha256_file(xml_path):
            lines.append(f"✗ {task}: annotations.xml không khớp SHA-256 trong lock.txt")
            gaps = True
        else:
            lines.append(f"✓ {task}: annotations.xml, lock.txt, reference.txt, compare.md đầy đủ và hash khớp")
    return lines, gaps


def _check_log(base: Path, name: str, config: Dict[str, object]) -> Tuple[List[str], bool, List[Dict[str, str]]]:
    path = base / "submission" / name
    spec = config["logs"][name]
    if not path.is_file():
        return [f"✗ {name}: thiếu file"], True, []
    try:
        header, rows = nonempty_csv_rows(path)
    except (OSError, csv.Error, UnicodeError) as error:
        return [f"✗ {name}: không đọc được CSV ({error})"], True, []
    lines: List[str] = []
    gaps = False
    if header != spec["columns"]:
        lines.append(f"✗ {name}: header phải đúng thứ tự trong lab.json")
        gaps = True
    tasks = list(config["task_order"])
    counts = {task: 0 for task in tasks}
    for number, row in enumerate(rows, 2):
        errors = []
        for field in spec.get("required", []):
            if not row.get(field, ""):
                errors.append(f"thiếu {field}")
        for field, allowed in spec.get("enums", {}).items():
            value = row.get(field, "")
            if value and value not in allowed:
                errors.append(f"{field}={value} không hợp lệ")
        task = row.get("task", "")
        if task not in tasks:
            errors.append(f"task={task or '(trống)'} không hợp lệ")
        else:
            counts[task] += 1
        if errors:
            lines.append(f"✗ {name} dòng {number}: " + "; ".join(errors))
            gaps = True
    minimum = int(spec.get("min_rows_per_task", 0))
    for task, count in counts.items():
        prefix = "✓" if count >= minimum else "✗"
        lines.append(f"{prefix} {name} {task}: {count} dòng (cần ít nhất {minimum})")
        if count < minimum:
            gaps = True
    total_minimum = int(spec.get("min_rows_total", 0))
    if total_minimum:
        prefix = "✓" if len(rows) >= total_minimum else "✗"
        lines.append(f"{prefix} {name}: {len(rows)} dòng tổng (cần ít nhất {total_minimum})")
        if len(rows) < total_minimum:
            gaps = True
    return lines, gaps, rows


def _check_documents(base: Path, config: Dict[str, object]) -> Tuple[List[str], bool]:
    lines: List[str] = []
    gaps = False
    marker = str(config.get("todo_marker", "TODO"))
    for name in config.get("documents", []):
        path = base / "submission" / str(name)
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            lines.append(f"✗ {name}: thiếu hoặc rỗng")
            gaps = True
            continue
        count = path.read_text(encoding="utf-8").count(marker)
        if count:
            lines.append(f"✗ {name}: còn {count} marker {marker}")
            gaps = True
        else:
            lines.append(f"✓ {name}: đã điền và không còn marker {marker}")
    return lines, gaps


def _source_summary(counts: Dict[str, int]) -> str:
    return ", ".join(f"{name}={count}" for name, count in sorted(counts.items())) or "(không có)"


def _provenance_lines(base: Path, config: Dict[str, object]) -> List[str]:
    """Tóm tắt dấu vết trực tiếp từ XML; mọi dòng chỉ là tín hiệu."""
    lines = [". Dấu vết provenance (đọc trực tiếp annotations.xml):"]
    owners: Dict[str, List[str]] = {}
    tolerance = float(config.get("identical_vertex_px", 0.5))
    manifest_tasks = {}
    manifest_path = base / "data" / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest_tasks = read_json(manifest_path).get("tasks", {})
        except LabError:
            manifest_tasks = {}
    for task in config["task_order"]:
        xml_path = base / "submission" / task / "annotations.xml"
        if not xml_path.is_file():
            lines.append(f". {task}: chưa có annotations.xml")
            continue
        try:
            data = xml_path.read_bytes()
            meta = export_meta(data)
            sources = source_counts(data)
            task_manifest = manifest_tasks.get(task, {})
            core = task_manifest.get("core", []) if isinstance(task_manifest, dict) else []
            learner = parse_bytes(data, core)
        except (OSError, LabError, ValueError) as error:
            lines.append(f"! {task}: không đọc được dấu vết ({error})")
            continue
        owner = meta["owner"] or "(không có)"
        created = meta["created"] or "(không có)"
        dumped = meta["dumped"] or "(không có)"
        non_manual = sum(count for name, count in sources.items() if name != "manual")
        lines.append(
            f"{'!' if non_manual else '.'} {task}: owner={owner}; {created} -> {dumped}; "
            f"shape_sources={_source_summary(sources)}"
        )
        if meta["owner"]:
            owners.setdefault(meta["owner"], []).append(task)
        if non_manual:
            lines.append(
                f"! {task}: {non_manual} shape có source khác manual — hỏi về nguồn import và decision_log.csv."
            )
        gt_path = base / "gt" / task / "annotations.xml"
        if gt_path.is_file():
            try:
                reference = parse_bytes(gt_path.read_bytes(), core)
                identical, total = identical_shapes(learner, reference, tolerance)
            except (OSError, LabError, ValueError) as error:
                lines.append(f"! {task}: không đọc được reference để kiểm shape trùng ({error})")
            else:
                if identical:
                    lines.append(
                        f"! {task}: {identical}/{total} shape trùng từng đỉnh "
                        f"(<= {display_tolerance(tolerance)} px) với reference."
                    )
    if len(owners) >= 2:
        detail = "; ".join(f"{owner}: {', '.join(tasks)}" for owner, tasks in owners.items())
        lines.append(f"! Các task dùng từ 2 CVAT owner khác nhau: {detail}")
    return lines


def check_submission(base: Path) -> Tuple[List[str], bool]:
    """Trả từng dòng kiểm tra và cờ có thiếu/sai."""
    config = load_lab(base)
    members = load_team(base)
    task_lines, gaps = _check_tasks(base, config)
    lines = [mode_line(base), *task_lines]
    for task in config["task_order"]:
        reference_path = base / "submission" / task / "reference.txt"
        if not reference_path.is_file():
            continue
        reference = lock_values(reference_path)
        lock_path = base / "submission" / task / "lock.txt"
        lock = lock_values(lock_path) if lock_path.is_file() else {}
        try:
            opened_at = datetime.fromisoformat(reference.get("opened_at", ""))
            locked_at = datetime.fromisoformat(lock.get("locked_at", ""))
            relocked_after_open = locked_at > opened_at
        except (TypeError, ValueError):
            continue
        if relocked_after_open:
            lines.append(f"! {task}: khoá lại sau khi mở reference — ghi lý do trong decision log")
    if members and not any((base / "submission").glob("*/peer-*.txt")):
        lines.append("✗ Chế độ nhóm: chưa có submission/*/peer-*.txt")
        gaps = True
    comparison_lines, comparison_gaps, _ = _check_log(base, "comparison_log.csv", config)
    decision_lines, decision_gaps, decision_rows = _check_log(base, "decision_log.csv", config)
    document_lines, document_gaps = _check_documents(base, config)
    lines.extend(comparison_lines)
    lines.extend(decision_lines)
    lines.extend(document_lines)
    gaps = gaps or comparison_gaps or decision_gaps or document_gaps
    ratified = sum(row.get("status") == "ratified" for row in decision_rows)
    if ratified:
        lines.append(f"✓ decision_log.csv: {ratified} dòng đã ratify")
    else:
        lines.append("! decision_log.csv: chưa có dòng nào ratified — ratify ở bước cuối (phút 225–235)")
    lines.extend(_provenance_lines(base, config))
    lines.append("Đây là kiểm tra đủ file, không phải điểm.")
    return lines, gaps
