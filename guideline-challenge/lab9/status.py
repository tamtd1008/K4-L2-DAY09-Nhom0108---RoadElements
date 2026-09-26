"""Bảng gate G1–G6 của Guideline Design Challenge."""

from __future__ import annotations

from pathlib import Path
import re
from typing import List, Tuple

from . import LabError
from .catalog import validate_sample_pack
from .common import challenge_config, is_filled, read_csv
from .freeze import freeze_integrity, guideline_version, valid_labels
from .scoring import calculate_gts

CALIBRATION_COLUMNS = ["sample_id", "item", "values_by_annotator", "diagnosis", "action", "rule_change"]


def _safe_version(base: Path) -> int:
    try:
        return guideline_version(base)
    except Exception:
        return 0


def _sample_pack_gate(base: Path) -> Tuple[bool, str]:
    try:
        rows, errors = validate_sample_pack(base)
    except Exception:
        return False, "sample_pack.csv chưa đọc được"
    if errors:
        return False, errors[0]
    if not any(row["split"] == "example" for row in rows):
        return False, "sample_pack.csv chưa có example"
    if not any(row["split"] == "calibration" for row in rows):
        return False, "sample_pack.csv chưa có calibration"
    return True, ""


def _calibration_gate(base: Path) -> Tuple[bool, str]:
    path = base / "project" / "06_calibration_report.csv"
    try:
        header, rows = read_csv(path)
        enums = challenge_config(base)["enums"]
    except Exception:
        return False, "06_calibration_report.csv chưa đọc được"
    if any(name not in header for name in CALIBRATION_COLUMNS):
        return False, "06_calibration_report.csv thiếu cột bắt buộc"
    try:
        pack_rows, pack_errors = validate_sample_pack(base)
    except Exception:
        return False, "sample_pack.csv chưa đọc được"
    if pack_errors:
        return False, "sample_pack.csv chưa hợp lệ nên chưa đối chiếu được sample calibration"
    calibration_ids = {row["sample_id"] for row in pack_rows if row["split"] == "calibration"}
    valid = [
        row
        for row in rows
        if all(row.get(name, "") for name in CALIBRATION_COLUMNS[:-1])
        and row["sample_id"] in calibration_ids
        and row["diagnosis"].lower() in enums["diagnosis"]
        and row["action"].lower() in enums["action"]
    ]
    if len(valid) < 3:
        return False, "06_calibration_report.csv cần ít nhất 3 dòng hợp lệ (sample_id thuộc split calibration, đủ cột, enum đúng)"
    if not any(row.get("rule_change", "") for row in valid):
        return False, "calibration report chưa có rule_change"
    return True, ""


def _freeze_gate(base: Path) -> Tuple[bool, str]:
    try:
        _, changed = freeze_integrity(base)
    except LabError as error:
        return False, str(error)
    except Exception:
        return False, "FREEZE.txt chưa có hoặc chưa đọc được"
    if changed:
        return False, f"freeze không còn nguyên: {changed[0]}"
    return True, ""


def _edge_case_count(base: Path) -> int:
    path = base / "project" / "04_edge_cases" / "edge_case_cards.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return 0
    return sum(
        match.group(1) != "TODO"
        for match in re.finditer(r"(?im)^\W*case id\W*:\W*(\S+)", text)
    )


def _revision_versions(base: Path) -> Tuple[bool, bool]:
    path = base / "project" / "08_revision_log.md"
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if "|" in line]
    except OSError:
        return False, False
    separators = {
        index
        for index, line in enumerate(lines)
        if all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in line.strip("|").split("|"))
    }
    header_indexes = {index - 1 for index in separators if index > 0}
    rows = [line for index, line in enumerate(lines) if index not in separators | header_indexes]
    v2_rows = {index for index, line in enumerate(rows) if re.search(r"(?i)\bv2\b", line)}
    v3_rows = {index for index, line in enumerate(rows) if re.search(r"(?i)\bv3\b", line)}
    distinct = any(left != right for left in v2_rows for right in v3_rows)
    return bool(v2_rows), bool(v3_rows) and distinct


def _gts_current(base: Path) -> bool:
    path = base / "project" / "07_blind_handoff" / "gts_summary.md"
    try:
        expected, _ = calculate_gts(base)
        return path.read_text(encoding="utf-8") == expected
    except Exception:
        return False


def gate_status(base: Path) -> List[Tuple[str, bool, str]]:
    """Trả trạng thái và đúng một thiếu sót đầu tiên cho mỗi gate."""
    project = base / "project"
    version = _safe_version(base)
    pack_ok, pack_missing = _sample_pack_gate(base)
    calibration_ok, calibration_missing = _calibration_gate(base)
    freeze_ok, freeze_missing = _freeze_gate(base)

    g1_checks = [
        (is_filled(project / "00_team.md"), "00_team.md còn TODO hoặc bị thiếu"),
        (is_filled(project / "01_problem_statement.md"), "01_problem_statement.md còn TODO hoặc bị thiếu"),
    ]
    g2_checks = [
        (version >= 1, "02_guideline.md cần version >= v1"),
        (valid_labels(base), "03_cvat_labels.json chưa có label hợp lệ"),
        (is_filled(project / "03_ontology_and_cvat_setup.md"), "03_ontology_and_cvat_setup.md còn TODO hoặc bị thiếu"),
        (pack_ok, pack_missing),
    ]
    g3_checks = [
        (calibration_ok, calibration_missing),
        (version >= 2, "02_guideline.md cần version >= v2"),
    ]
    peer_output = project / "07_blind_handoff" / "peer_output"
    peer_exports = peer_output.is_dir() and any(path.suffix.lower() in {".zip", ".xml"} for path in peer_output.iterdir())
    g5_checks = [
        (peer_exports, "peer_output chưa có export .zip/.xml"),
        ((project / "07_blind_handoff" / "transfer_score.csv").is_file(), "chưa có transfer_score.csv"),
        ((project / "07_blind_handoff" / "clarification_log.csv").is_file(), "chưa có clarification_log.csv"),
        (is_filled(project / "07_blind_handoff" / "peer_feedback.md"), "peer_feedback.md còn TODO hoặc bị thiếu"),
    ]
    has_v2, has_v3 = _revision_versions(base)
    g6_checks = [
        (version >= 3, "02_guideline.md cần version >= v3"),
        (_edge_case_count(base) >= 8, "edge_case_cards.md cần ít nhất 8 CASE ID"),
        (is_filled(project / "05_qa_plan.md"), "05_qa_plan.md còn TODO hoặc bị thiếu"),
        (_gts_current(base), "gts_summary.md bị thiếu hoặc không còn khớp transfer_score.csv"),
        (has_v2, "08_revision_log.md chưa có dòng bảng v2"),
        (has_v3, "08_revision_log.md chưa có dòng bảng v3"),
        (is_filled(project / "09_cvat_export_or_task_reference.txt"), "09_cvat_export_or_task_reference.txt còn TODO hoặc bị thiếu"),
        (freeze_ok, freeze_missing),
    ]
    groups = [g1_checks, g2_checks, g3_checks, [(freeze_ok, freeze_missing)], g5_checks, g6_checks]
    labels = ["Topic lock", "CVAT ready", "Calibration done", "Gold frozen", "Handoff complete", "Final handoff"]
    result = []
    for index, (label, checks) in enumerate(zip(labels, groups), 1):
        missing = next((message for passed, message in checks if not passed), "")
        result.append((f"G{index} · {label}", not missing, missing))
    return result


def status_lines(base: Path) -> Tuple[List[str], bool]:
    """Render gate board."""
    gates = gate_status(base)
    lines = [f"✓ {name}" if done else f"… {name}: {missing}" for name, done, missing in gates]
    return lines, all(done for _, done, _ in gates)
