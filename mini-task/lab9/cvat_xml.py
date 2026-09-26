"""Chuẩn hoá CVAT for images/video 1.1 thành object chung."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET
import zipfile

from . import LabError

Point = Tuple[float, float]


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
            x, y = pair.split(",", 1)
            result.append((float(x), float(y)))
    return result


def _shape_points(node: ET.Element) -> List[Point]:
    if node.tag in {"polyline", "polygon", "points"}:
        return _points(node.get("points", ""))
    if node.tag == "box":
        return [
            (float(node.get("xtl", "0")), float(node.get("ytl", "0"))),
            (float(node.get("xbr", "0")), float(node.get("ybr", "0"))),
        ]
    return []


def _meta_frame_names(root: ET.Element) -> Dict[int, str]:
    names: Dict[int, str] = {}
    for node in root.findall(".//meta//frames//image") + root.findall(".//meta//frames//frame"):
        raw_frame = node.get("frame", node.get("id", ""))
        name = node.get("name", node.text or "")
        if raw_frame.isdigit() and name:
            names[int(raw_frame)] = Path(name).name
    return names


def parse_bytes(data: bytes, core_names: Iterable[str] = ()) -> CvatDocument:
    """Parse bytes XML; core_names ánh xạ frame video sang tên ảnh."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise LabError(f"annotations.xml không hợp lệ: {error}") from error
    if root.tag != "annotations":
        raise LabError("Root XML phải là <annotations>.")
    document = CvatDocument()
    for image in root.findall("image"):
        sample = Path(image.get("name", "")).name
        frame = int(image.get("id", "0"))
        document.samples.append(sample)
        document.sizes[sample] = (int(image.get("width", "1280")), int(image.get("height", "720")))
        for node in image:
            if node.tag not in {"box", "polyline", "polygon", "points", "tag"}:
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
    core = list(core_names)
    meta_names = _meta_frame_names(root)
    tracks = root.findall("track")
    document.has_tracks = bool(tracks)
    for track in tracks:
        track_attrs = _attributes(track)
        track_id = track.get("id")
        for node in track:
            if node.tag not in {"box", "polyline", "polygon", "points"} or node.get("outside") == "1":
                continue
            frame = int(node.get("frame", "0"))
            sample = meta_names.get(frame, core[frame] if 0 <= frame < len(core) else f"frame-{frame}")
            if sample not in document.samples:
                document.samples.append(sample)
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
    return document


def parse_file(path: Path, core_names: Iterable[str] = ()) -> CvatDocument:
    """Parse XML/ZIP CVAT từ đĩa."""
    return parse_bytes(xml_bytes(path), core_names)

