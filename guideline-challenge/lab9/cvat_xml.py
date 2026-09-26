"""Chuẩn hoá CVAT for images/video 1.1 thành object chung."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET
import re
import zipfile

from . import LabError

Point = Tuple[float, float]
# Mọi shape CVAT 2.x có thể nằm trong <image>/<track>; bỏ sót một loại sẽ biến object thật thành "none".
SHAPE_TAGS = {"box", "polyline", "polygon", "points", "mask", "ellipse", "cuboid", "skeleton"}


def _int_value(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        raise LabError(f"annotations.xml có {field_name} không phải số: {value!r}.") from error


def _float_value(value: str, field_name: str) -> float:
    try:
        return float(value)
    except ValueError as error:
        raise LabError(f"annotations.xml có {field_name} không phải số: {value!r}.") from error


@dataclass
class CvatObject:
    """Một shape/tag sau khi bỏ khác biệt giữa hai format CVAT."""

    sample: str
    frame: int
    label: str
    kind: str
    points: List[Point]
    attributes: Dict[str, str]
    track_id: Optional[str] = None


@dataclass
class CvatDocument:
    """Tài liệu CVAT đã chuẩn hoá."""

    objects: List[CvatObject] = field(default_factory=list)
    sizes: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    samples: List[str] = field(default_factory=list)
    has_tracks: bool = False


def xml_bytes(path: Path) -> bytes:
    """Lấy annotations.xml từ XML trực tiếp hoặc ZIP CVAT."""
    if not path.is_file():
        raise LabError(f"Không thấy file {path}.")
    try:
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                members = [name for name in archive.namelist() if Path(name).name == "annotations.xml"]
                if len(members) != 1:
                    raise LabError("ZIP phải chứa đúng một annotations.xml.")
                return archive.read(members[0])
        if path.suffix.lower() != ".xml":
            raise LabError("File export phải là .xml hoặc .zip của CVAT.")
        return path.read_bytes()
    except (OSError, zipfile.BadZipFile, KeyError) as error:
        raise LabError(f"Không đọc được export {path}: {error}") from error


def _attributes(node: ET.Element) -> Dict[str, str]:
    return {
        str(item.get("name", "")): item.text if item.text not in (None, "") else "__undefined__"
        for item in node.findall("attribute")
    }


def _points(text: str) -> List[Point]:
    result = []
    for pair in text.split(";"):
        if pair.strip():
            if "," not in pair:
                raise LabError(f"annotations.xml có point không hợp lệ: {pair!r}.")
            x, y = pair.split(",", 1)
            result.append((_float_value(x, "tọa độ x"), _float_value(y, "tọa độ y")))
    return result


def _shape_points(node: ET.Element) -> List[Point]:
    if node.tag in {"polyline", "polygon", "points"}:
        return _points(node.get("points", ""))
    if node.tag == "box":
        return [
            (_float_value(node.get("xtl", "0"), "xtl"), _float_value(node.get("ytl", "0"), "ytl")),
            (_float_value(node.get("xbr", "0"), "xbr"), _float_value(node.get("ybr", "0"), "ybr")),
        ]
    if node.tag == "mask":
        left, top = _float_value(node.get("left", "0"), "left"), _float_value(node.get("top", "0"), "top")
        width, height = _float_value(node.get("width", "0"), "width"), _float_value(node.get("height", "0"), "height")
        return [(left, top), (left + width, top + height)]
    if node.tag == "ellipse":
        cx, cy = _float_value(node.get("cx", "0"), "cx"), _float_value(node.get("cy", "0"), "cy")
        rx, ry = _float_value(node.get("rx", "0"), "rx"), _float_value(node.get("ry", "0"), "ry")
        return [(cx - rx, cy - ry), (cx + rx, cy + ry)]
    return []


def _meta_frame_names(root: ET.Element) -> Dict[int, str]:
    names: Dict[int, str] = {}
    for node in root.findall(".//meta//frames//image") + root.findall(".//meta//frames//frame"):
        raw_frame = node.get("frame", node.get("id", ""))
        name = node.get("name", node.text or "")
        if raw_frame.isdigit() and name:
            names[int(raw_frame)] = Path(name).stem
    return names


def _meta_frame_bounds(root: ET.Element) -> Optional[Tuple[int, int, int]]:
    """Đọc (start, stop, step) frame trong metadata CVAT video, export từ task hoặc từ job."""
    segment = root.find(".//meta/task")
    if segment is None:
        segment = root.find(".//meta/job")
    if segment is None:
        return None
    start_text = segment.findtext("start_frame")
    stop_text = segment.findtext("stop_frame")
    size_text = segment.findtext("size")
    step_match = re.search(r"step\s*=\s*(\d+)", segment.findtext("frame_filter") or "")
    step = max(int(step_match.group(1)), 1) if step_match else 1
    start = int(start_text) if start_text and start_text.isdigit() else 0
    if stop_text and stop_text.isdigit():
        return start, int(stop_text), step
    if size_text and size_text.isdigit() and int(size_text) > 0:
        return start, start + (int(size_text) - 1) * step, step
    return None


def parse_bytes(data: bytes, core_names: Iterable[str] = ()) -> CvatDocument:
    """Parse bytes XML; core_names ánh xạ frame video sang tên ảnh."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise LabError(f"annotations.xml không hợp lệ: {error}") from error
    if root.tag != "annotations":
        raise LabError("Root XML phải là <annotations>.")
    document = CvatDocument()
    images = root.findall("image")
    for image in images:
        sample = Path(image.get("name", "")).stem
        frame = _int_value(image.get("id", "0"), "image id")
        document.samples.append(sample)
        document.sizes[sample] = (
            _int_value(image.get("width", "1280"), "image width"),
            _int_value(image.get("height", "720"), "image height"),
        )
        for node in image:
            if node.tag not in SHAPE_TAGS | {"tag"}:
                continue
            document.objects.append(
                CvatObject(
                    sample=sample,
                    frame=frame,
                    label=node.get("label", ""),
                    kind=node.tag,
                    points=_shape_points(node),
                    attributes=_attributes(node),
                    track_id=node.get("track_id"),
                )
            )
    core = [Path(name).stem for name in core_names]
    meta_names = _meta_frame_names(root)
    bounds = _meta_frame_bounds(root)
    start, step = (bounds[0], bounds[2]) if bounds else (0, 1)

    def sample_for(frame: int) -> str:
        if frame in meta_names:
            return meta_names[frame]
        index, offset = divmod(frame - start, step)
        return core[index] if offset == 0 and 0 <= index < len(core) else f"frame-{frame}"

    tracks = root.findall("track")
    frame_tags = root.findall("tag")
    if not images and not tracks and not frame_tags:
        # Export video trống và export images mất hết <image> trông giống hệt nhau; không đoán thay nhóm.
        raise LabError(
            "Export không có <image>, <track> hay <tag> nào nên không biết ảnh nào có mặt."
            " Export lại bằng CVAT for images 1.1 — format này ghi đủ mọi ảnh, kể cả ảnh trống."
        )
    # CVAT for images ghi <image> cho mọi frame kể cả frame trống, nên ảnh vắng mặt là ảnh thiếu thật.
    # Chỉ CVAT for video mới cần dựng frame trống từ metadata.
    if not images:
        document.samples.extend(name for _, name in sorted(meta_names.items()) if name not in document.samples)
        if bounds and core:
            for frame in range(bounds[0], bounds[1] + 1, step):
                sample = sample_for(frame)
                if sample not in document.samples:
                    document.samples.append(sample)
    document.has_tracks = bool(tracks)
    for track in tracks:
        track_attrs = _attributes(track)
        track_id = track.get("id")
        for node in track:
            if node.tag not in SHAPE_TAGS:
                continue
            frame = _int_value(node.get("frame", "0"), "track frame")
            sample = sample_for(frame)
            if sample not in document.samples:
                document.samples.append(sample)
            if node.get("outside") == "1":
                continue
            attributes = dict(track_attrs)
            attributes.update(_attributes(node))
            document.objects.append(
                CvatObject(
                    sample=sample,
                    frame=frame,
                    label=track.get("label", node.get("label", "")),
                    kind=node.tag,
                    points=_shape_points(node),
                    attributes=attributes,
                    track_id=track_id,
                )
            )
    for node in frame_tags:
        frame = _int_value(node.get("frame", "0"), "tag frame")
        sample = sample_for(frame)
        if sample not in document.samples:
            document.samples.append(sample)
        document.objects.append(
            CvatObject(
                sample=sample,
                frame=frame,
                label=node.get("label", ""),
                kind="tag",
                points=[],
                attributes=_attributes(node),
            )
        )
    return document


def parse_file(path: Path, core_names: Iterable[str] = ()) -> CvatDocument:
    """Parse XML/ZIP CVAT từ đĩa."""
    return parse_bytes(xml_bytes(path), core_names)
