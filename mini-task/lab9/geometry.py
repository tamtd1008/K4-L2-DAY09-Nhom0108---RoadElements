"""Các phép hình học thuần Python dùng bởi compare."""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

Point = Tuple[float, float]


def resample_polyline(points: Sequence[Point], count: int) -> List[Point]:
    """Lấy mẫu đều theo độ dài cung, gồm hai đầu mút."""
    if count <= 0 or not points:
        return []
    if len(points) == 1 or count == 1:
        return [points[0]] * count
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    if total == 0:
        return [points[0]] * count
    result: List[Point] = []
    segment = 0
    walked = 0.0
    for index in range(count):
        target = total * index / (count - 1)
        while segment < len(lengths) - 1 and walked + lengths[segment] < target:
            walked += lengths[segment]
            segment += 1
        length = lengths[segment]
        ratio = 0.0 if length == 0 else (target - walked) / length
        a, b = points[segment], points[segment + 1]
        result.append((a[0] + ratio * (b[0] - a[0]), a[1] + ratio * (b[1] - a[1])))
    return result


def point_segment_distance(point: Point, start: Point, end: Point) -> float:
    """Khoảng cách Euclid từ điểm tới đoạn thẳng."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    if dx == 0 and dy == 0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    ratio = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy)
    ratio = max(0.0, min(1.0, ratio))
    nearest = (start[0] + ratio * dx, start[1] + ratio * dy)
    return math.hypot(point[0] - nearest[0], point[1] - nearest[1])


def directed_polyline_distance(left: Sequence[Point], right: Sequence[Point], samples: int) -> float:
    """Trung bình khoảng cách từ mẫu trên left tới các đoạn của right."""
    sampled = resample_polyline(left, samples)
    segments = list(zip(right, right[1:]))
    if not sampled or not segments:
        return math.inf
    return sum(min(point_segment_distance(point, a, b) for a, b in segments) for point in sampled) / len(sampled)


def polyline_distance(left: Sequence[Point], right: Sequence[Point], samples: int) -> float:
    """Khoảng cách đối xứng giữa hai polyline."""
    return (directed_polyline_distance(left, right, samples) + directed_polyline_distance(right, left, samples)) / 2


def box_iou(left: Sequence[Point], right: Sequence[Point]) -> float:
    """IoU của hai box biểu diễn bằng hai góc."""
    lx1, ly1 = left[0]
    lx2, ly2 = left[1]
    rx1, ry1 = right[0]
    rx2, ry2 = right[1]
    intersection = max(0.0, min(lx2, rx2) - max(lx1, rx1)) * max(0.0, min(ly2, ry2) - max(ly1, ry1))
    left_area = max(0.0, lx2 - lx1) * max(0.0, ly2 - ly1)
    right_area = max(0.0, rx2 - rx1) * max(0.0, ry2 - ry1)
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def box_center_distance(left: Sequence[Point], right: Sequence[Point]) -> float:
    """Khoảng cách giữa tâm hai box."""
    lc = ((left[0][0] + left[1][0]) / 2, (left[0][1] + left[1][1]) / 2)
    rc = ((right[0][0] + right[1][0]) / 2, (right[0][1] + right[1][1]) / 2)
    return math.hypot(lc[0] - rc[0], lc[1] - rc[1])


def polygon_mask(points: Sequence[Point], width: int, height: int) -> bytearray:
    """Raster polygon bằng scanline even-odd tại tâm pixel."""
    mask = bytearray(width * height)
    if len(points) < 3 or width <= 0 or height <= 0:
        return mask
    edges = list(zip(points, points[1:] + points[:1]))
    for y in range(height):
        scan_y = y + 0.5
        intersections = []
        for (x1, y1), (x2, y2) in edges:
            if (y1 <= scan_y < y2) or (y2 <= scan_y < y1):
                intersections.append(x1 + (scan_y - y1) * (x2 - x1) / (y2 - y1))
        intersections.sort()
        for left, right in zip(intersections[0::2], intersections[1::2]):
            start = max(0, int(math.ceil(left - 0.5)))
            stop = min(width, int(math.ceil(right - 0.5)))
            if stop > start:
                offset = y * width
                mask[offset + start : offset + stop] = b"\x01" * (stop - start)
    return mask


def union_masks(masks: Iterable[bytearray], size: int) -> bytearray:
    """Hợp nhiều mask cùng kích thước."""
    result = bytearray(size)
    for mask in masks:
        for index, value in enumerate(mask):
            if value:
                result[index] = 1
    return result


def mask_stats(reference: bytearray, learner: bytearray) -> Tuple[float, int, int]:
    """Trả IoU, số pixel chỉ reference, số pixel chỉ learner."""
    intersection = union = ref_only = learner_only = 0
    for ref, own in zip(reference, learner):
        if ref or own:
            union += 1
        if ref and own:
            intersection += 1
        elif ref:
            ref_only += 1
        elif own:
            learner_only += 1
    return (intersection / union if union else 1.0, ref_only, learner_only)
