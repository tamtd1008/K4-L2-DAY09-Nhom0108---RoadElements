"""Chuẩn bị bảng chấm owner và tính Guideline Transferability Score."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import shutil
from typing import DefaultDict, Dict, List, Sequence, Tuple

from . import LabError
from .catalog import validate_sample_pack
from .common import challenge_config, read_csv, require_columns, write_csv
from .cvat_xml import CvatObject, parse_file
from .freeze import freeze_integrity, load_gold

SCORE_COLUMNS = [
    "sample_id",
    "decision_id",
    "expected",
    "severity",
    "kind",
    "peer_evidence",
    "correct",
    "note",
]
CLARIFICATION_COLUMNS = ["time", "asker", "question", "answered_how", "guideline_change"]


def _object_text(item: CvatObject) -> str:
    attributes = ";".join(f"{name}={value}" for name, value in sorted(item.attributes.items()))
    return item.label + (f" [{attributes}]" if attributes else "")


def _evidence(objects: Sequence[CvatObject]) -> str:
    if not objects:
        return "none"
    counts = Counter(_object_text(item) for item in objects)
    return " | ".join(f"{text}×{count}" if count > 1 else text for text, count in sorted(counts.items()))


def prepare_score(base: Path, peer_file: Path) -> List[str]:
    """Copy peer export và refresh transfer_score, không tự chấm correct."""
    _, changed = freeze_integrity(base)
    if changed:
        raise LabError("Gold hoặc sample_pack đã đổi sau freeze: " + ", ".join(changed) + ".")
    pack_rows, errors = validate_sample_pack(base)
    if errors:
        raise LabError("sample_pack.csv chưa hợp lệ:\n- " + "\n- ".join(errors))
    blind_ids = sorted({row["sample_id"] for row in pack_rows if row["split"] == "blind"})
    output_dir = base / "project" / "07_blind_handoff" / "peer_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / peer_file.name
    document = parse_file(peer_file, blind_ids)
    expected_samples = set(blind_ids)
    actual_samples = set(document.samples)
    if actual_samples != expected_samples:
        missing = sorted(expected_samples - actual_samples)
        extra = sorted(actual_samples - expected_samples)
        details = []
        if missing:
            details.append("thiếu " + ", ".join(missing))
        if extra:
            details.append("thừa " + ", ".join(extra))
        raise LabError("Peer export không khớp blind samples (" + "; ".join(details) + ").")
    temporary = output_dir / f".{peer_file.name}.tmp"
    try:
        if peer_file.resolve() != destination.resolve():
            shutil.copyfile(peer_file, temporary)
            temporary.replace(destination)
    except OSError as error:
        if temporary.exists():
            temporary.unlink()
        raise LabError(f"Không copy được peer export {peer_file}: {error}") from error
    grouped: DefaultDict[str, List[CvatObject]] = defaultdict(list)
    for item in document.objects:
        grouped[item.sample].append(item)
    score_path = base / "project" / "07_blind_handoff" / "transfer_score.csv"
    preserved: Dict[Tuple[str, str], Tuple[str, str]] = {}
    if score_path.is_file():
        header, rows = read_csv(score_path)
        if "sample_id" in header and "decision_id" in header:
            preserved = {
                (row.get("sample_id", ""), row.get("decision_id", "")): (
                    row.get("correct", ""),
                    row.get("note", ""),
                )
                for row in rows
            }
    output_rows = []
    for gold in load_gold(base):
        key = (gold["sample_id"], gold["decision_id"])
        correct, note = preserved.get(key, ("", ""))
        output_rows.append(
            {
                "sample_id": gold["sample_id"],
                "decision_id": gold["decision_id"],
                "expected": gold["expected"],
                "severity": gold["severity"],
                "kind": "geometry" if gold["expected"].lower().startswith("geometry:") else "decision",
                "peer_evidence": _evidence(grouped[gold["sample_id"]]),
                "correct": correct,
                "note": note,
            }
        )
    write_csv(score_path, SCORE_COLUMNS, output_rows)
    remaining = sum(not row["correct"] for row in output_rows)
    return [
        f"✓ Đã lưu peer export tại {destination.relative_to(base)}.",
        f"! Còn {remaining}/{len(output_rows)} dòng cần owner nhập correct (0 hoặc 1).",
    ]


def _validated_scores(base: Path) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
    values, changed = freeze_integrity(base)
    if changed:
        raise LabError("Gold hoặc sample_pack đã đổi sau freeze: " + ", ".join(changed) + ".")
    gold = load_gold(base)
    score_path = base / "project" / "07_blind_handoff" / "transfer_score.csv"
    header, rows = read_csv(score_path)
    require_columns(score_path, header, SCORE_COLUMNS)
    gold_map = {(row["sample_id"], row["decision_id"]): row for row in gold}
    score_map: Dict[Tuple[str, str], Dict[str, str]] = {}
    for row in rows:
        key = (row["sample_id"], row["decision_id"])
        if key in score_map:
            raise LabError(f"transfer_score.csv trùng key {key[0]}/{key[1]}.")
        score_map[key] = row
    if set(score_map) != set(gold_map):
        missing = sorted(set(gold_map) - set(score_map))
        extra = sorted(set(score_map) - set(gold_map))
        detail = []
        if missing:
            detail.append("thiếu " + ", ".join(f"{a}/{b}" for a, b in missing))
        if extra:
            detail.append("thừa " + ", ".join(f"{a}/{b}" for a, b in extra))
        raise LabError("transfer_score.csv không khớp frozen gold: " + "; ".join(detail) + ".")
    ordered = []
    for key, gold_row in gold_map.items():
        row = score_map[key]
        if row["expected"] != gold_row["expected"] or row["severity"] != gold_row["severity"]:
            raise LabError(f"transfer_score.csv đã đổi expected/severity của {key[0]}/{key[1]}.")
        expected_kind = "geometry" if gold_row["expected"].lower().startswith("geometry:") else "decision"
        if row["kind"] != expected_kind:
            raise LabError(f"transfer_score.csv có kind sai ở {key[0]}/{key[1]}.")
        if row["correct"] not in {"0", "1"}:
            raise LabError(f"correct của {key[0]}/{key[1]} phải là 0 hoặc 1.")
        ordered.append(row)
    return ordered, values


def calculate_gts(base: Path) -> Tuple[str, Dict[str, float]]:
    """Tính summary hiện tại mà không ghi file."""
    rows, freeze = _validated_scores(base)
    decision_rows = [row for row in rows if row["kind"] != "geometry"]
    geometry_rows = [row for row in rows if row["kind"] == "geometry"]
    critical_rows = [row for row in rows if row["severity"].lower() == "critical"]
    if not decision_rows:
        raise LabError("Không có non-geometry decision để tính D.")
    if not geometry_rows:
        raise LabError("Không có geometry decision để tính G.")
    if not critical_rows:
        raise LabError("Không có critical decision để tính C.")
    clarification_path = base / "project" / "07_blind_handoff" / "clarification_log.csv"
    header, questions = read_csv(clarification_path)
    require_columns(clarification_path, header, CLARIFICATION_COLUMNS)
    question_count = len(questions)
    independence = 100.0 if question_count == 0 else 70.0 if question_count <= 2 else 40.0 if question_count <= 4 else 0.0

    def score(items: Sequence[Dict[str, str]]) -> float:
        return 100.0 * sum(row["correct"] == "1" for row in items) / len(items)

    decision = score(decision_rows)
    critical = score(critical_rows)
    geometry = score(geometry_rows)
    weights = challenge_config(base).get("gts_weights", {})
    total = (
        float(weights.get("decision", 0.6)) * decision
        + float(weights.get("critical", 0.2)) * critical
        + float(weights.get("geometry", 0.1)) * geometry
        + float(weights.get("independence", 0.1)) * independence
    )
    escapes = sum(row["correct"] == "0" for row in critical_rows)
    gold_errors = [row for row in rows if row["correct"] == "0" and row["note"].strip().lower().startswith("gold sai:")]
    critical_gold_errors = sum(row["severity"].lower() == "critical" for row in gold_errors)
    metrics = {
        "D": decision,
        "C": critical,
        "G": geometry,
        "I": independence,
        "GTS": total,
        "critical_escapes": float(escapes),
        "questions": float(question_count),
        "gold_errors": float(len(gold_errors)),
    }
    gold_note = ""
    if gold_errors:
        gold_note = (
            f"\n- Owner ghi `gold sai:` ở {len(gold_errors)} dòng ({critical_gold_errors} critical): vẫn tính 0 theo gold"
            " đã freeze; debrief tách các dòng này khỏi lỗi guideline."
        )
    summary = f"""# Guideline Transferability Score

| Chỉ số | Điểm | Đúng / Tổng |
|---|---:|---:|
| D · Decision accuracy | {decision:.1f} | {sum(row['correct'] == '1' for row in decision_rows)} / {len(decision_rows)} |
| C · Critical decisions | {critical:.1f} | {sum(row['correct'] == '1' for row in critical_rows)} / {len(critical_rows)} |
| G · Geometry compliance | {geometry:.1f} | {sum(row['correct'] == '1' for row in geometry_rows)} / {len(geometry_rows)} |
| I · Independence | {independence:.1f} | {question_count} câu hỏi |
| **GTS** | **{total:.1f}** | 0.60D + 0.20C + 0.10G + 0.10I |

- Critical escapes: {escapes}{gold_note}
- Frozen at: {freeze.get('frozen_at', '(không rõ)')}
- GTS đo khả năng truyền đạt của specification, không đo kỹ năng tổng quát của peer annotator.
"""
    return summary, metrics


def write_gts(base: Path) -> List[str]:
    """Tính, ghi và in summary GTS."""
    summary, _ = calculate_gts(base)
    path = base / "project" / "07_blind_handoff" / "gts_summary.md"
    path.write_text(summary, encoding="utf-8")
    return summary.rstrip().splitlines()
