"""Đo bất đồng giữa các export CVAT độc lập."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from . import LabError
from .catalog import validate_sample_pack
from .common import write_csv
from .cvat_xml import CvatDocument, CvatObject, parse_file

MEASURE_COLUMNS = ["sample_id", "label", "measure"]


def _objects(document: CvatDocument, sample_id: str, label: str) -> List[CvatObject]:
    return [item for item in document.objects if item.sample == sample_id and item.label == label]


def _multiset(values: Iterable[str]) -> str:
    return "|".join(sorted(values))


def _value(document: CvatDocument, sample_id: str, label: str, measure: str) -> str:
    objects = _objects(document, sample_id, label)
    if measure == "tag":
        return "1" if any(item.kind == "tag" for item in objects) else "0"
    shapes = [item for item in objects if item.kind != "tag"]
    if measure == "count":
        return str(len(shapes))
    attribute = measure.split(":", 1)[1]
    return _multiset(item.attributes[attribute] for item in objects if attribute in item.attributes)


def _measure_keys(documents: Sequence[CvatDocument], sample_ids: Sequence[str]) -> List[Tuple[str, str, str]]:
    keys = set()
    everything = [item for document in documents for item in document.objects]
    # Label đã xuất hiện ở bất kỳ sample nào được đo trên mọi sample, để "cùng không vẽ gì" cũng tính là đồng thuận.
    shape_labels = {item.label for item in everything if item.kind != "tag"}
    tag_labels = {item.label for item in everything if item.kind == "tag"}
    for sample_id in sample_ids:
        keys.update((sample_id, label, "count") for label in shape_labels)
        keys.update((sample_id, label, "tag") for label in tag_labels)
        for item in everything:
            if item.sample == sample_id:
                keys.update((sample_id, item.label, f"attr:{name}") for name in item.attributes)
    order = {"count": 0, "tag": 1}
    return sorted(keys, key=lambda key: (sample_ids.index(key[0]), key[1], order.get(key[2], 2), key[2]))


def run_calibration(base: Path, files: Sequence[Path]) -> List[str]:
    """So ≥2 export, ghi bảng đo wide và trả tóm tắt."""
    if len(files) < 2:
        raise LabError("Cần ít nhất 2 export CVAT cho calibration.")
    annotators = [path.stem for path in files]
    if len(set(annotators)) != len(annotators):
        raise LabError("Tên file export phải có stem khác nhau để nhận diện annotator.")
    reserved = set(MEASURE_COLUMNS + ["agree"])
    collisions = sorted(set(annotators) & reserved)
    if collisions:
        raise LabError("Tên file export trùng cột hệ thống: " + ", ".join(collisions) + ".")
    pack_rows, errors = validate_sample_pack(base)
    if errors:
        raise LabError("sample_pack.csv chưa hợp lệ:\n- " + "\n- ".join(errors))
    sample_ids = sorted({row["sample_id"] for row in pack_rows if row["split"] == "calibration"})
    if not sample_ids:
        raise LabError("sample_pack.csv chưa có sample calibration.")
    documents = [parse_file(path, sample_ids) for path in files]
    expected = set(sample_ids)
    for path, document in zip(files, documents):
        actual = set(document.samples)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            details = []
            if missing:
                details.append("thiếu " + ", ".join(missing))
            if extra:
                details.append("thừa " + ", ".join(extra))
            raise LabError(f"Export {path.name} không có cùng bộ sample calibration ({'; '.join(details)}).")
    rows: List[Dict[str, object]] = []
    disagreements: List[Tuple[int, Dict[str, object]]] = []
    for sample_id, label, measure in _measure_keys(documents, sample_ids):
        values = [_value(document, sample_id, label, measure) for document in documents]
        row: Dict[str, object] = {"sample_id": sample_id, "label": label, "measure": measure}
        row.update(dict(zip(annotators, values)))
        row["agree"] = "1" if len(set(values)) == 1 else "0"
        rows.append(row)
        disagreements.append((len(set(values)), row))
    columns = MEASURE_COLUMNS + annotators + ["agree"]
    write_csv(base / "project" / "06_calibration_measure.csv", columns, rows)
    count_rows = [row for row in rows if row["measure"] == "count"]
    attribute_rows = [row for row in rows if str(row["measure"]).startswith("attr:") or row["measure"] == "tag"]

    def percent(items: Sequence[Dict[str, object]]) -> float:
        return 100.0 * sum(row["agree"] == "1" for row in items) / len(items) if items else 100.0

    lines = [
        f"✓ Đã so {len(sample_ids)} sample từ {len(files)} annotator.",
        f"✓ Đồng thuận count: {percent(count_rows):.1f}%.",
        f"✓ Đồng thuận attribute/tag: {percent(attribute_rows):.1f}%.",
    ]
    ranked = sorted(disagreements, key=lambda item: (-item[0], str(item[1]["sample_id"]), str(item[1]["label"]), str(item[1]["measure"])))
    for distinct, row in ranked[:5]:
        values = ", ".join(f"{name}={row[name]}" for name in annotators)
        lines.append(f"! {row['sample_id']} · {row['label']} · {row['measure']}: {distinct} giá trị ({values})")
    return lines
