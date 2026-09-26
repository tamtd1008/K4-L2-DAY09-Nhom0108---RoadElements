"""Đọc catalog, kiểm tra sample pack và dựng thư mục upload CVAT."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import LabError
from .common import challenge_config, read_csv, require_columns

CATALOG_COLUMNS = [
    "sample_id",
    "file",
    "source",
    "original_name",
    "sequence",
    "width",
    "height",
    "weather",
    "timeofday",
    "scene",
]
PACK_COLUMNS = ["sample_id", "split", "tags", "reason"]


def load_catalog(base: Path) -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, str]]]:
    """Đọc catalog và lập chỉ mục sample_id duy nhất."""
    path = base / "data" / "catalog.csv"
    header, rows = read_csv(path)
    require_columns(path, header, CATALOG_COLUMNS)
    indexed: Dict[str, Dict[str, str]] = {}
    for row in rows:
        sample_id = row.get("sample_id", "")
        if not sample_id:
            raise LabError("data/catalog.csv có sample_id rỗng.")
        if sample_id in indexed:
            raise LabError(f"data/catalog.csv trùng sample_id {sample_id}.")
        relative = Path(row.get("file", ""))
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or len(relative.parts) < 3
            or relative.parts[0] != "data"
            or relative.stem != sample_id
            or relative.suffix.lower() not in {".jpg", ".jpeg", ".png", ".ppm"}
        ):
            raise LabError(f"data/catalog.csv có đường dẫn media không an toàn cho {sample_id}.")
        indexed[sample_id] = row
    return rows, indexed


def media_path(base: Path, row: Dict[str, str]) -> Path:
    """Resolve media và chặn symlink/path thoát khỏi data/."""
    candidate = base / row["file"]
    try:
        candidate.resolve().relative_to((base / "data").resolve())
    except (OSError, ValueError) as error:
        raise LabError(f"Đường dẫn media thoát khỏi data/ cho {row.get('sample_id', '(không rõ)')}.") from error
    if not candidate.is_file():
        raise LabError(f"Thiếu ảnh {row['file']} của {row.get('sample_id', '(không rõ)')}.")
    return candidate


def validate_sample_pack(base: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """Kiểm tra ID, split, tag và việc một ID không nằm ở hai split."""
    config = challenge_config(base)
    _, catalog = load_catalog(base)
    path = base / "project" / "sample_pack.csv"
    header, rows = read_csv(path)
    require_columns(path, header, PACK_COLUMNS)
    splits = {str(value).lower() for value in config["enums"]["split"]}
    tags = {str(value).lower() for value in config["enums"]["tags"]}
    seen: Dict[str, str] = {}
    errors: List[str] = []
    normalized: List[Dict[str, str]] = []
    for number, row in enumerate(rows, 2):
        sample_id = row.get("sample_id", "")
        split = row.get("split", "").lower()
        row_tags = [item.strip().lower() for item in row.get("tags", "").split(";") if item.strip()]
        if sample_id not in catalog:
            errors.append(f"dòng {number}: sample_id {sample_id or '(rỗng)'} không có trong catalog")
        if split not in splits:
            errors.append(f"dòng {number}: split {split or '(rỗng)'} không hợp lệ")
        invalid_tags = [item for item in row_tags if item not in tags]
        if invalid_tags:
            errors.append(f"dòng {number}: tag không hợp lệ: {', '.join(invalid_tags)}")
        if sample_id in seen and seen[sample_id] != split:
            errors.append(f"sample {sample_id} nằm ở cả split {seen[sample_id]} và {split}")
        elif sample_id:
            seen[sample_id] = split
        normalized.append({**row, "split": split, "tags": ";".join(row_tags)})
    return normalized, errors


def sample_lines(base: Path, source: Optional[str] = None) -> List[str]:
    """Tạo danh sách sample dễ đọc cho terminal."""
    rows, _ = load_catalog(base)
    if source:
        rows = [row for row in rows if row["source"] == source]
    lines = ["sample_id  source   bối cảnh"]
    for row in rows:
        context = row["sequence"] or "/".join(
            value for value in (row["weather"], row["timeofday"], row["scene"]) if value
        )
        lines.append(f"{row['sample_id']:<10} {row['source']:<8} {context or '-'}")
    return lines


def build_split(base: Path, split: str) -> List[str]:
    """Làm sạch rồi copy ảnh của một split vào build/<split>/."""
    config = challenge_config(base)
    valid_splits = {str(value).lower() for value in config["enums"]["split"]}
    split = split.lower()
    if split not in valid_splits:
        raise LabError("SPLIT không hợp lệ. Chọn: " + ", ".join(sorted(valid_splits)) + ".")
    rows, errors = validate_sample_pack(base)
    if errors:
        raise LabError("sample_pack.csv chưa hợp lệ:\n- " + "\n- ".join(errors))
    _, catalog = load_catalog(base)
    selected = [row["sample_id"] for row in rows if row["split"] == split]
    if not selected:
        raise LabError(f"sample_pack.csv chưa có sample cho split {split}.")
    destination = base / "build" / split
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for sample_id in selected:
        relative = Path(catalog[sample_id]["file"])
        source_path = media_path(base, catalog[sample_id])
        shutil.copyfile(source_path, destination / relative.name)
    return [f"✓ Đã dựng build/{split}/ với {len(selected)} ảnh."]
