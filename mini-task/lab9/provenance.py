"""Đọc dấu vết CVAT và phát hiện shape trùng từng đỉnh."""

from __future__ import annotations

from collections import Counter
from math import hypot
from typing import Counter as CounterType, Dict, Tuple
from xml.etree import ElementTree as ET

from . import LabError
from .cvat_xml import CvatDocument


def _root(xml_data: bytes) -> ET.Element:
    try:
        return ET.fromstring(xml_data)
    except ET.ParseError as error:
        raise LabError(f"annotations.xml không hợp lệ: {error}") from error


def export_meta(xml_data: bytes) -> Dict[str, str]:
    """Lấy metadata task/job có ích từ một CVAT XML export."""
    root = _root(xml_data)
    node = root.find("./meta/task")
    kind = "task"
    if node is None:
        node = root.find("./meta/job")
        kind = "job"
    if node is None:
        return {name: "" for name in ("owner", "kind", "id", "name", "created", "dumped")}

    def text(path: str) -> str:
        value = node.findtext(path)
        return value.strip() if value else ""

    dumped = root.findtext("./meta/dumped")
    return {
        "owner": text("owner/username"),
        "kind": kind,
        "id": text("id"),
        "name": text("name") if kind == "task" else "",
        "created": text("created"),
        "dumped": dumped.strip() if dumped else "",
    }


def source_counts(xml_data: bytes) -> CounterType[str]:
    """Đếm source của object ảnh và track; thiếu source được tính unknown."""
    root = _root(xml_data)
    counts: CounterType[str] = Counter()
    shape_tags = {"box", "polygon", "polyline", "points", "ellipse", "cuboid", "skeleton", "mask", "tag"}
    for image in root.findall("image"):
        for node in image:
            if node.tag in shape_tags:
                counts[node.get("source") or "unknown"] += 1
    for track in root.findall("track"):
        counts[track.get("source") or "unknown"] += 1
    return counts


def identical_shapes(
    learner_doc: CvatDocument,
    other_doc: CvatDocument,
    tolerance: float,
) -> Tuple[int, int]:
    """Đếm shape bài mình trùng loại, mẫu, frame và từng đỉnh với phía kia."""
    def key(item, document: CvatDocument):
        # Với CVAT for images, tên file là định danh ổn định; image id thay đổi khi upload lại cùng tập core.
        frame = item.frame if document.has_tracks else 0
        return (document.has_tracks, item.sample, frame, item.label, item.kind, len(item.points))

    candidates = {}
    for item in other_doc.objects:
        if item.kind == "tag" or not item.points:
            continue
        candidates.setdefault(key(item, other_doc), []).append(item)

    identical = 0
    total = 0
    for item in learner_doc.objects:
        if item.kind == "tag" or not item.points:
            continue
        total += 1
        for other in candidates.get(key(item, learner_doc), []):
            if all(hypot(x1 - x2, y1 - y2) <= tolerance for (x1, y1), (x2, y2) in zip(item.points, other.points)):
                identical += 1
                break
    return identical, total


def display_tolerance(tolerance: float) -> str:
    """Hiển thị số thập phân theo cách viết tiếng Việt."""
    return f"{tolerance:g}".replace(".", ",")
