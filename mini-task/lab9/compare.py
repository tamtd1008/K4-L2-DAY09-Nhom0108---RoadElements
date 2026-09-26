"""So sánh annotation đã khoá với reference đã mở."""

from __future__ import annotations

import csv
import html
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from . import LabError
from .common import load_lab, load_manifest, read_json, require_intact_lock, require_task
from .cvat_xml import CvatDocument, CvatObject, parse_file
from .geometry import (
    box_center_distance,
    box_iou,
    mask_stats,
    polygon_mask,
    polyline_distance,
    union_masks,
)
from .provenance import display_tolerance, identical_shapes


@dataclass
class Difference:
    """Một khác biệt và loại taxonomy được gợi ý."""

    sample: str
    object_id: str
    text: str
    error_type: str
    unmatched: bool = False


@dataclass
class Comparison:
    """Nội dung trung gian cho Markdown, HTML và tóm tắt CLI."""

    task: str
    sections: Dict[str, List[str]] = field(default_factory=dict)
    differences: List[Difference] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    html_samples: Set[str] = field(default_factory=set)
    matched: int = 0
    only_learner: int = 0
    only_other: int = 0
    attribute_disagreements: int = 0

    def line(self, sample: str, text: str) -> None:
        self.sections.setdefault(sample, []).append(text)

    def difference(self, sample: str, object_id: str, text: str, error_type: str, unmatched: bool = False) -> None:
        self.line(sample, f"- {text} — gợi ý `{error_type}`")
        self.differences.append(Difference(sample, object_id, text, error_type, unmatched))
        self.html_samples.add(sample)


# Object chỉ có ở bài học viên: reference có thể không gán loại này (LISA bỏ đèn xa, GTSDB chỉ 43 class),
# hoặc học viên vẽ thừa. Taxonomy của slide không có loại "thừa", nên gợi ý guideline_gap để học viên tự xét.
EXTRA_TYPE = "guideline_gap"


def _by_sample(document: CvatDocument) -> Dict[str, List[CvatObject]]:
    grouped: Dict[str, List[CvatObject]] = {}
    for item in document.objects:
        grouped.setdefault(item.sample, []).append(item)
    return grouped


def _objects(items: Iterable[CvatObject], label: str, kind: Optional[str] = None) -> List[CvatObject]:
    return [item for item in items if item.label == label and (kind is None or item.kind == kind)]


def _names(items: Sequence[CvatObject], prefix: str, light: bool = False) -> Dict[int, str]:
    result = {}
    for index, item in enumerate(items, 1):
        result[id(item)] = f"{prefix}#{item.track_id}" if light and item.track_id is not None else f"{prefix}{index}"
    return result


def _display(value: str) -> str:
    """Hiển thị sentinel CVAT bằng từ dễ hiểu với học viên."""
    return "chưa chọn" if value in {"", "__undefined__"} else value


def _attribute_differences(
    report: Comparison,
    sample: str,
    reference: CvatObject,
    learner: CvatObject,
    object_id: str,
    attributes: Iterable[str],
    error_type: str = "attribute",
) -> None:
    for name in attributes:
        ref_value = reference.attributes.get(name, "__undefined__")
        own_value = learner.attributes.get(name, "__undefined__")
        if ref_value != own_value:
            report.attribute_disagreements += 1
            report.difference(
                sample,
                object_id,
                f"{object_id}: {name}: bạn {_display(own_value)}, reference {_display(ref_value)}",
                error_type,
            )


def _greedy_pairs(
    reference: Sequence[CvatObject],
    learner: Sequence[CvatObject],
    scores: Iterable[Tuple[float, int, int]],
    threshold: float,
    descending: bool,
) -> Tuple[List[Tuple[int, int, float]], Set[int], Set[int]]:
    pairs = []
    used_ref: Set[int] = set()
    used_own: Set[int] = set()
    for score, ref_index, own_index in sorted(scores, key=lambda value: value[0], reverse=descending):
        accepted = score >= threshold if descending else score <= threshold
        if not accepted or ref_index in used_ref or own_index in used_own:
            continue
        pairs.append((ref_index, own_index, score))
        used_ref.add(ref_index)
        used_own.add(own_index)
    return pairs, used_ref, used_own


def _compare_tags(
    report: Comparison,
    sample: str,
    reference: Sequence[CvatObject],
    learner: Sequence[CvatObject],
    tag_config: Dict[str, object],
) -> None:
    label = str(tag_config.get("label", ""))
    ref_tags = _objects(reference, label, "tag")
    own_tags = _objects(learner, label, "tag")
    if ref_tags and not own_tags:
        report.only_other += 1
        report.difference(sample, "B-tag", "thiếu tag image_context", "missing")
    elif own_tags and not ref_tags:
        report.only_learner += 1
        report.difference(sample, "B-tag", "tag image_context không có trong reference", "missing")
    elif ref_tags and own_tags:
        report.matched += 1
        _attribute_differences(
            report,
            sample,
            ref_tags[0],
            own_tags[0],
            "B-tag",
            tag_config.get("attributes", []),
        )


def compare_lane(
    report: Comparison,
    reference: CvatDocument,
    learner: CvatDocument,
    task_config: Dict[str, object],
    reference_kind: str,
) -> None:
    """So polyline lane và tag ngữ cảnh."""
    ref_group, own_group = _by_sample(reference), _by_sample(learner)
    settings = task_config["compare"]
    samples = list(dict.fromkeys(learner.samples))
    for sample in samples:
        ref_items, own_items = ref_group.get(sample, []), own_group.get(sample, [])
        _compare_tags(report, sample, ref_items, own_items, task_config.get("tag", {}))
        if reference_kind == "context_only":
            report.line(sample, "- Reference hiện chỉ có tag; không so polyline.")
            continue
        ref_lines = _objects(ref_items, str(settings["label"]), "polyline")
        own_lines = _objects(own_items, str(settings["label"]), "polyline")
        ref_names, own_names = _names(ref_lines, "R"), _names(own_lines, "B")
        scores = (
            (polyline_distance(ref.points, own.points, int(settings["samples_per_line"])), ri, oi)
            for ri, ref in enumerate(ref_lines)
            for oi, own in enumerate(own_lines)
        )
        pairs, used_ref, used_own = _greedy_pairs(
            ref_lines, own_lines, scores, float(settings["match_mean_px"]), False
        )
        report.matched += len(pairs)
        report.only_other += len(ref_lines) - len(used_ref)
        report.only_learner += len(own_lines) - len(used_own)
        for ri, oi, distance in pairs:
            pair_name = f"{ref_names[id(ref_lines[ri])]}/{own_names[id(own_lines[oi])]}"
            report.line(sample, f"- {pair_name}: khoảng cách {distance:.1f} px")
            _attribute_differences(
                report,
                sample,
                ref_lines[ri],
                own_lines[oi],
                pair_name,
                settings.get("attributes", []),
            )
        for index, item in enumerate(ref_lines):
            if index not in used_ref:
                name = ref_names[id(item)]
                report.difference(sample, name, f"{name}: bạn thiếu polyline reference", "missing", unmatched=True)
        for index, item in enumerate(own_lines):
            if index not in used_own:
                name = own_names[id(item)]
                report.difference(sample, name, f"{name}: polyline bạn vẽ không có trong reference", EXTRA_TYPE, unmatched=True)


def _union_of(masks: Sequence[bytearray], indices: Sequence[int], size: int) -> bytearray:
    return union_masks((masks[index] for index in indices), size)


def compare_drivable(
    report: Comparison,
    reference: CvatDocument,
    learner: CvatDocument,
    task_config: Dict[str, object],
) -> None:
    """So union polygon bằng raster scanline từng ảnh."""
    ref_group, own_group = _by_sample(reference), _by_sample(learner)
    settings = task_config["compare"]
    label = str(settings["label"])
    type_attribute = str(settings["type_attribute"])
    same_shape_iou = float(settings.get("same_shape_iou", 0.9))
    for sample in dict.fromkeys(learner.samples):
        ref_polygons = _objects(ref_group.get(sample, []), label, "polygon")
        own_polygons = _objects(own_group.get(sample, []), label, "polygon")
        width, height = learner.sizes.get(sample, reference.sizes.get(sample, (1280, 720)))
        size = width * height
        ref_types = [item.attributes.get(type_attribute, "__undefined__") for item in ref_polygons]
        own_types = [item.attributes.get(type_attribute, "__undefined__") for item in own_polygons]
        for index, own_type in enumerate(own_types, 1):
            if own_type == "__undefined__":
                report.attribute_disagreements += 1
                report.difference(sample, f"B{index}", f"B{index}: areaType chưa chọn", "attribute")
        ref_masks = [polygon_mask(item.points, width, height) for item in ref_polygons]
        own_masks = [polygon_mask(item.points, width, height) for item in own_polygons]
        scores = (
            (mask_stats(ref_masks[ri], own_masks[oi])[0], ri, oi)
            for ri in range(len(ref_masks))
            for oi in range(len(own_masks))
        )
        pairs, _, _ = _greedy_pairs(ref_polygons, own_polygons, scores, same_shape_iou, True)
        paired_ref = {ri for ri, _, _ in pairs}
        paired_own = {oi for _, oi, _ in pairs}
        report.matched += len(pairs)
        report.only_other += len(ref_polygons) - len(paired_ref)
        report.only_learner += len(own_polygons) - len(paired_own)
        # Polygon trùng hình reference mà khác areaType là lỗi attribute; geometry tính theo areaType reference.
        geometry_types = list(own_types)
        for ri, oi, score in pairs:
            if own_types[oi] == ref_types[ri]:
                continue
            geometry_types[oi] = ref_types[ri]
            if own_types[oi] != "__undefined__":
                report.attribute_disagreements += 1
                report.difference(
                    sample,
                    f"B{oi + 1}",
                    f"B{oi + 1}: hình khớp reference (IoU {score:.3f}), khác areaType: "
                    f"bạn {own_types[oi]}, reference {_display(ref_types[ri])}",
                    "attribute",
                )
        categories = list(settings.get("types", [])) + ["mọi vùng"]
        for category in categories:
            ref_indices = [i for i, kind in enumerate(ref_types) if category in ("mọi vùng", kind)]
            own_indices = [i for i, kind in enumerate(own_types) if category in ("mọi vùng", kind)]
            ref_mask = _union_of(ref_masks, ref_indices, size)
            iou, ref_only, own_only = mask_stats(ref_mask, _union_of(own_masks, own_indices, size))
            report.line(
                sample,
                f"- {category}: IoU {iou:.3f}; chỉ reference {ref_only} px; chỉ bạn {own_only} px",
            )
            geometry_indices = [i for i, kind in enumerate(geometry_types) if category in ("mọi vùng", kind)]
            if geometry_indices != own_indices:
                iou, ref_only, own_only = mask_stats(ref_mask, _union_of(own_masks, geometry_indices, size))
                report.line(
                    sample,
                    f"- {category} nếu sửa areaType: IoU {iou:.3f}; chỉ reference {ref_only} px; chỉ bạn {own_only} px",
                )
            if ref_only or own_only:
                report.difference(
                    sample,
                    str(category),
                    f"{category}: vùng hình học khác reference ({ref_only} px thiếu, {own_only} px thừa)",
                    "geometry",
                )


def compare_sign(
    report: Comparison,
    reference: CvatDocument,
    learner: CvatDocument,
    task_config: Dict[str, object],
    negative_samples: Set[str],
) -> None:
    """So box biển báo bằng IoU."""
    ref_group, own_group = _by_sample(reference), _by_sample(learner)
    settings = task_config["compare"]
    for sample in dict.fromkeys(learner.samples):
        ref_boxes = _objects(ref_group.get(sample, []), str(settings["label"]), "box")
        own_boxes = _objects(own_group.get(sample, []), str(settings["label"]), "box")
        ref_names, own_names = _names(ref_boxes, "R"), _names(own_boxes, "B")
        scores = (
            (box_iou(ref.points, own.points), ri, oi)
            for ri, ref in enumerate(ref_boxes)
            for oi, own in enumerate(own_boxes)
        )
        pairs, used_ref, used_own = _greedy_pairs(
            ref_boxes, own_boxes, scores, float(settings["match_iou"]), True
        )
        report.matched += len(pairs)
        report.only_other += len(ref_boxes) - len(used_ref)
        report.only_learner += len(own_boxes) - len(used_own)
        for ri, oi, score in pairs:
            pair_name = f"{ref_names[id(ref_boxes[ri])]}/{own_names[id(own_boxes[oi])]}"
            report.line(sample, f"- {pair_name}: IoU {score:.3f}")
            _attribute_differences(
                report,
                sample,
                ref_boxes[ri],
                own_boxes[oi],
                pair_name,
                settings.get("attributes", []),
                "class",
            )
        not_in_reference = [str(name) for name in settings.get("not_in_reference", [])]
        if own_boxes and not_in_reference:
            report.line(
                sample,
                f"- {', '.join(not_in_reference)}: GT không có, không so — tự đối chiếu bằng decision log",
            )
        for index, item in enumerate(ref_boxes):
            if index not in used_ref:
                name = ref_names[id(item)]
                report.difference(sample, name, f"{name}: bạn thiếu biển có trong reference", "missing", unmatched=True)
        for index, item in enumerate(own_boxes):
            if index not in used_own:
                name = own_names[id(item)]
                note = "box trên ảnh âm" if sample in negative_samples else "box bạn vẽ không có trong reference"
                report.difference(sample, name, f"{name}: {note}", EXTRA_TYPE, unmatched=True)


def _ranges(frames: Sequence[int]) -> str:
    if not frames:
        return "không có"
    groups: List[Tuple[int, int]] = []
    start = previous = frames[0]
    for frame in frames[1:]:
        if frame != previous + 1:
            groups.append((start, previous))
            start = frame
        previous = frame
    groups.append((start, previous))
    return ", ".join(str(start) if start == end else f"{start}–{end}" for start, end in groups)


def _change_frames(items: Sequence[CvatObject], attribute: str) -> List[int]:
    changes = []
    previous: Optional[str] = None
    for item in sorted(items, key=lambda value: value.frame):
        value = item.attributes.get(attribute, "__undefined__")
        if previous is not None and value != previous:
            changes.append(item.frame)
        previous = value
    return changes


def compare_light(
    report: Comparison,
    reference: CvatDocument,
    learner: CvatDocument,
    task_config: Dict[str, object],
) -> None:
    """Ghép box từng frame, sau đó liên kết track theo số lần ghép."""
    settings = task_config["compare"]
    ref_items = _objects(reference.objects, str(settings["label"]), "box")
    own_items = _objects(learner.objects, str(settings["label"]), "box")
    ref_frames: Dict[int, List[CvatObject]] = {}
    own_frames: Dict[int, List[CvatObject]] = {}
    for item in ref_items:
        ref_frames.setdefault(item.frame, []).append(item)
    for item in own_items:
        own_frames.setdefault(item.frame, []).append(item)
    matched_by_frame: Dict[int, List[Tuple[CvatObject, CvatObject]]] = {}
    counts: Dict[Tuple[str, str], int] = {}
    for frame in sorted(set(ref_frames) | set(own_frames)):
        refs, owns = ref_frames.get(frame, []), own_frames.get(frame, [])
        scores = []
        for ri, ref in enumerate(refs):
            ref_height = max(0.0, ref.points[1][1] - ref.points[0][1])
            distance = box_center_distance(ref.points, owns[0].points) if owns else float("inf")
            for oi, own in enumerate(owns):
                distance = box_center_distance(ref.points, own.points)
                if distance <= float(settings["match_center_ratio"]) * ref_height:
                    scores.append((distance, ri, oi))
        pairs, _, _ = _greedy_pairs(refs, owns, scores, float("inf"), False)
        for ri, oi, _ in pairs:
            ref, own = refs[ri], owns[oi]
            matched_by_frame.setdefault(frame, []).append((ref, own))
            key = (str(own.track_id), str(ref.track_id))
            counts[key] = counts.get(key, 0) + 1
    own_track_ids = sorted({str(item.track_id) for item in own_items})
    ref_track_ids = sorted({str(item.track_id) for item in ref_items})
    associations: Dict[str, str] = {}
    for own_id in own_track_ids:
        candidates = [(count, ref_id) for (candidate, ref_id), count in counts.items() if candidate == own_id]
        if candidates:
            associations[own_id] = max(candidates, key=lambda value: (value[0], value[1]))[1]
    report.matched += len(associations)
    report.only_other += len(set(ref_track_ids) - set(associations.values()))
    report.only_learner += len(set(own_track_ids) - set(associations))
    for own_id, ref_id in associations.items():
        own_track = sorted([item for item in own_items if str(item.track_id) == own_id], key=lambda value: value.frame)
        ref_track = sorted([item for item in ref_items if str(item.track_id) == ref_id], key=lambda value: value.frame)
        own_by_frame = {item.frame: item for item in own_track}
        ref_by_frame = {item.frame: item for item in ref_track}
        pair_name = f"R#{ref_id}/B#{own_id}"
        ref_changes = _change_frames(ref_track, "state")
        own_changes = _change_frames(own_track, "state")
        if ref_changes or own_changes:
            summary = f"frame đổi state reference {_ranges(ref_changes)}; bạn {_ranges(own_changes)}"
        else:
            summary = "cả reference và bạn đều không đổi state"
        report.line(own_track[0].sample if own_track else "traffic_light", f"- {pair_name}: {summary}")
        for attribute in settings.get("attributes", []):
            differing = []
            values: Dict[Tuple[str, str], List[int]] = {}
            for frame in sorted(set(ref_by_frame) & set(own_by_frame)):
                ref_value = ref_by_frame[frame].attributes.get(str(attribute), "__undefined__")
                own_value = own_by_frame[frame].attributes.get(str(attribute), "__undefined__")
                if ref_value != own_value:
                    differing.append(frame)
                    values.setdefault((own_value, ref_value), []).append(frame)
            for (own_value, ref_value), frames in values.items():
                sample = own_by_frame[frames[0]].sample
                report.attribute_disagreements += 1
                report.difference(
                    sample,
                    pair_name,
                    f"{pair_name} {attribute}, frame {_ranges(frames)}: bạn {_display(own_value)}, reference {_display(ref_value)}",
                    "temporal" if attribute == "state" else "attribute",
                )
            for frame in differing:
                report.html_samples.add(own_by_frame[frame].sample)
        extra_frames = sorted(set(own_by_frame) - set(ref_by_frame))
        if extra_frames:
            sample = own_by_frame[extra_frames[0]].sample
            report.difference(
                sample,
                pair_name,
                f"{pair_name}: frame {_ranges(extra_frames)} bạn còn box, reference không có — thiếu outside?",
                "temporal",
            )
            report.html_samples.add(sample)
        relevance = sorted({_display(item.attributes.get("relevance", "__undefined__")) for item in own_track})
        sample = own_track[0].sample if own_track else "traffic_light"
        report.line(sample, f"- B#{own_id}: relevance={', '.join(relevance)} (không so với GT)")
    own_ids_by_ref: Dict[str, List[str]] = {}
    for own_id, ref_id in associations.items():
        own_ids_by_ref.setdefault(ref_id, []).append(own_id)
    for ref_id, own_ids in own_ids_by_ref.items():
        ref_by_frame = {item.frame: item for item in ref_items if str(item.track_id) == ref_id}
        covered = {item.frame for item in own_items if str(item.track_id) in own_ids}
        names = ", ".join(f"B#{own_id}" for own_id in own_ids)
        first = ref_by_frame[min(ref_by_frame)].sample
        if len(own_ids) > 1:
            report.difference(
                first,
                f"R#{ref_id}",
                f"R#{ref_id}: một đèn nhưng bạn tách thành {len(own_ids)} track ({names})",
                "temporal",
            )
        missing_frames = sorted(set(ref_by_frame) - covered)
        if missing_frames:
            sample = ref_by_frame[missing_frames[0]].sample
            report.difference(
                sample,
                f"R#{ref_id}",
                f"R#{ref_id}: frame {_ranges(missing_frames)} reference còn thấy đèn, {names} không có box — outside sớm?",
                "temporal",
            )
            report.html_samples.add(sample)
    associated_refs = set(associations.values())
    for ref_id in ref_track_ids:
        if ref_id not in associated_refs:
            track = [item for item in ref_items if str(item.track_id) == ref_id]
            sample = track[0].sample if track else "traffic_light"
            report.difference(sample, f"R#{ref_id}", f"R#{ref_id}: bạn thiếu track reference", "missing", unmatched=True)
    for own_id in own_track_ids:
        if own_id not in associations:
            track = [item for item in own_items if str(item.track_id) == own_id]
            sample = track[0].sample if track else "traffic_light"
            report.difference(
                sample,
                f"B#{own_id}",
                f"B#{own_id}: không có trong reference (LISA không gán đèn xa) — ghi relevance và lý do vào light_log.md",
                EXTRA_TYPE,
                unmatched=True,
            )
            relevance = sorted({_display(item.attributes.get("relevance", "__undefined__")) for item in track})
            report.line(sample, f"- B#{own_id}: relevance={', '.join(relevance)} (không so với GT)")
    if ref_items:
        report.html_samples.add(min(ref_items, key=lambda item: item.frame).sample)
    for ref_id in ref_track_ids:
        track = [item for item in ref_items if str(item.track_id) == ref_id]
        for frame in _change_frames(track, "state"):
            item = next((candidate for candidate in track if candidate.frame == frame), None)
            if item:
                report.html_samples.add(item.sample)


def compare_documents(
    task: str,
    config: Dict[str, object],
    manifest_task: Dict[str, object],
    reference: CvatDocument,
    learner: CvatDocument,
    reference_kind: str = "dataset_gt",
) -> Comparison:
    """Chọn phép so đúng task và thêm cảnh báo core bị thiếu."""
    report = Comparison(task)
    core = list(manifest_task.get("core", []))
    for sample in core:
        # Export dạng video không liệt kê frame trống, nên chỉ kiểm tra khi có thẻ <image>.
        if learner.sizes and sample not in learner.sizes:
            warning = f"! Core {sample} không có trong export của bạn."
            report.warnings.append(warning)
            report.line(sample, warning)
            report.html_samples.add(sample)
        if task != "traffic_light":
            report.html_samples.add(sample)
    task_config = config["tasks"][task]
    if task == "lane":
        compare_lane(report, reference, learner, task_config, reference_kind)
    elif task == "drivable":
        compare_drivable(report, reference, learner, task_config)
    elif task == "traffic_sign":
        compare_sign(report, reference, learner, task_config, set(manifest_task.get("core_negatives", [])))
    else:
        compare_light(report, reference, learner, task_config)
    return report


def _candidate_csv(report: Comparison, config: Dict[str, object]) -> str:
    columns = config["logs"]["comparison_log.csv"]["columns"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for item in report.differences:
        writer.writerow(
            {
                "task": report.task,
                "sample": item.sample,
                "object": item.object_id,
                "difference": item.text,
                "error_type": item.error_type,
                "who_is_right": "",
                "action": "",
                "note": "",
            }
        )
    return stream.getvalue().rstrip("\n")


def markdown_report(
    report: Comparison,
    config: Dict[str, object],
    reference_note: str,
    identical: Optional[Tuple[int, int, float]] = None,
) -> str:
    """Dựng report Markdown không có điểm hay kết luận đạt/trượt."""
    lines = [
        f"# So sánh {report.task}",
        "",
        "> Các số dưới đây là số của công cụ so sánh, không phải ngưỡng chấm.",
        "",
        reference_note,
        "",
    ]
    if identical is not None:
        count, total, tolerance = identical
        lines.extend(
            [
                f"Trùng từng đỉnh với reference: {count}/{total} shape (<= {display_tolerance(tolerance)} px).",
                "",
            ]
        )
    lines.extend(report.warnings)
    if report.warnings:
        lines.append("")
    if not report.differences:
        lines.extend(["✓ Không có khác biệt trên các mẫu đã so.", ""])
    for sample, section in report.sections.items():
        lines.extend([f"## {sample}", "", *section, ""])
    lines.extend(
        [
            "## Dòng gợi ý cho comparison_log.csv",
            "",
            "```csv",
            _candidate_csv(report, config),
            "```",
            "",
            "Hãy điền `who_is_right`, `action`, `note`; loại lỗi chỉ là gợi ý.",
            "",
        ]
    )
    return "\n".join(lines)


def _svg_object(item: CvatObject, css_class: str, object_id: str, unmatched: bool) -> str:
    if item.kind == "box" and len(item.points) == 2:
        (x1, y1), (x2, y2) = item.points
        shape = f'<rect x="{x1}" y="{y1}" width="{x2 - x1}" height="{y2 - y1}" />'
        label_x, label_y = x1, y1
    elif item.kind in {"polygon", "polyline", "points"} and item.points:
        points = " ".join(f"{x},{y}" for x, y in item.points)
        tag = "polygon" if item.kind == "polygon" else "polyline"
        shape = f'<{tag} points="{points}" />'
        label_x, label_y = item.points[0]
    else:
        return ""
    classes = f"shape {css_class}" + (" unmatched" if unmatched else "")
    return f'<g class="{classes}">{shape}<text x="{label_x}" y="{label_y}">{html.escape(object_id)}</text></g>'


def html_report(
    report: Comparison,
    manifest_task: Dict[str, object],
    reference: CvatDocument,
    learner: CvatDocument,
    other_label: str = "Reference",
) -> str:
    """Dựng HTML tự chứa, overlay ảnh bằng SVG."""
    ref_group, own_group = _by_sample(reference), _by_sample(learner)
    core, stretch = set(manifest_task.get("core", [])), set(manifest_task.get("stretch", []))
    sizes = manifest_task.get("media_sizes", {})
    sections = []
    for sample in sorted(report.html_samples):
        width, height = sizes.get(sample, learner.sizes.get(sample, reference.sizes.get(sample, (1280, 720))))
        lane = "core" if sample in core else "stretch" if sample in stretch else "core"
        href = f"../../data/{report.task}/{lane}/{sample}"
        ref_items = [item for item in ref_group.get(sample, []) if item.kind != "tag"]
        own_items = [item for item in own_group.get(sample, []) if item.kind != "tag"]
        drawings = []
        for index, item in enumerate(ref_items, 1):
            name = f"R#{item.track_id}" if item.track_id is not None else f"R{index}"
            unmatched = any(
                difference.sample == sample and difference.unmatched and difference.object_id == name
                for difference in report.differences
            )
            drawings.append(_svg_object(item, "other", name, unmatched))
        for index, item in enumerate(own_items, 1):
            name = f"B#{item.track_id}" if item.track_id is not None else f"B{index}"
            unmatched = any(
                difference.sample == sample and difference.unmatched and difference.object_id == name
                for difference in report.differences
            )
            drawings.append(_svg_object(item, "learner", name, unmatched))
        sections.append(
            f'<section><h2>{html.escape(sample)}</h2><svg viewBox="0 0 {width} {height}">'
            f'<image href="{html.escape(href)}" width="{width}" height="{height}" />'
            + "".join(drawings)
            + "</svg></section>"
        )
    return """<!doctype html><html lang="vi"><meta charset="utf-8"><title>So sánh lab9</title>
<style>body{font:16px system-ui;margin:2rem;background:#fafafa;color:#222}.legend span{margin-right:1rem}.other-label{color:#159447}.own{color:#d81b90}section{margin:2rem 0}svg{max-width:100%;height:auto;background:#ddd}.shape{fill:none;stroke-width:3}.shape.other{stroke:#159447;stroke-dasharray:8 5}.shape.learner{stroke:#d81b90}.shape.unmatched{stroke-width:6}.shape text{fill:currentColor;stroke:none;font-weight:bold;font-size:18px}.shape.other text{fill:#159447}.shape.learner text{fill:#d81b90}</style>
<h1>Overlay so sánh</h1><p class="legend"><span class="other-label">""" + html.escape(other_label) + ": xanh lá, nét đứt</span><span class=\"own\">Bạn: hồng, nét liền</span></p>" + "".join(sections) + "</html>\n"


def _relabel_other(report: Comparison, label: str) -> None:
    """Đổi từ ngữ GT/reference thành tên phía còn lại cho report peer."""
    def replace(text: str) -> str:
        return text.replace("Reference", label).replace("reference", label).replace("GT", label)

    report.sections = {sample: [replace(line) for line in lines] for sample, lines in report.sections.items()}
    report.warnings = [replace(line) for line in report.warnings]
    for difference in report.differences:
        difference.text = replace(difference.text)


def compare_locked_with(
    base: Path,
    task: str,
    other_xml: Path,
    other_label: str = "reference",
) -> Tuple[Comparison, Dict[str, object], Dict[str, object], CvatDocument, CvatDocument]:
    """So bài đã khoá với một XML khác mà không quyết định đường dẫn output."""
    config = load_lab(base)
    require_task(task, config)
    manifest = load_manifest(base)
    manifest_task = manifest.get("tasks", {}).get(task)
    if not isinstance(manifest_task, dict):
        raise LabError(f"data/manifest.json thiếu task {task}.")
    locked_xml, _, _ = require_intact_lock(
        base,
        task,
        f"Chưa khoá {task} — chạy lock trước.",
        "file đã đổi sau khi khoá — chạy lại make lock với đúng file export đã khoá để khôi phục "
        "(sửa tay XML không được tính).",
    )
    core = manifest_task.get("core", [])
    learner = parse_file(locked_xml, core)
    other = parse_file(other_xml, core)
    report = compare_documents(task, config, manifest_task, other, learner)
    if other_label != "reference":
        _relabel_other(report, other_label)
    return report, config, manifest_task, other, learner


def write_html_comparison(
    destination: Path,
    report: Comparison,
    manifest_task: Dict[str, object],
    other: CvatDocument,
    learner: CvatDocument,
    other_label: str = "Reference",
) -> None:
    """Ghi HTML compare vào đường dẫn do caller chọn."""
    destination.write_text(html_report(report, manifest_task, other, learner, other_label), encoding="utf-8")


def run_compare(base: Path, task: str) -> List[str]:
    """Kiểm tra lock, chạy compare và ghi hai report."""
    submission = base / "submission" / task
    config = load_lab(base)
    require_task(task, config)
    require_intact_lock(
        base,
        task,
        f"Chưa khoá {task} — chạy lock trước.",
        "file đã đổi sau khi khoá — chạy lại make lock với đúng file export đã khoá để khôi phục "
        "(sửa tay XML không được tính).",
    )
    gt_xml = base / "gt" / task / "annotations.xml"
    if not gt_xml.is_file():
        raise LabError(
            f"Chưa cài reference {task}. Chạy make reference TASK={task} rồi thử lại."
        )
    report, config, manifest_task, reference, learner = compare_locked_with(base, task, gt_xml)
    meta_path = base / "gt" / task / "meta.json"
    meta = read_json(meta_path) if meta_path.is_file() else {"kind": "dataset_gt", "note": ""}
    kind = str(meta.get("kind", "dataset_gt"))
    note = str(meta.get("note", "")) or str(config.get("reference_notes", {}).get(task, {}).get(kind, ""))
    if task == "lane" and kind == "context_only":
        report = compare_documents(task, config, manifest_task, reference, learner, kind)
    tolerance = float(config.get("identical_vertex_px", 0.5))
    identical, total = identical_shapes(learner, reference, tolerance)
    submission.mkdir(parents=True, exist_ok=True)
    md_path = submission / "compare.md"
    html_path = submission / "compare.html"
    md_path.write_text(markdown_report(report, config, note, (identical, total, tolerance)), encoding="utf-8")
    write_html_comparison(html_path, report, manifest_task, reference, learner)
    lines = [f"✓ Đã so {task}: {len(report.differences)} khác biệt gợi ý."]
    if report.warnings:
        lines.append(f"! {len(report.warnings)} mẫu core không có trong export.")
    if identical:
        lines.append(
            f"! {identical}/{total} shape trùng từng đỉnh (<= {display_tolerance(tolerance)} px) với reference — "
            "nếu bạn đã import reference vào CVAT, ghi rõ trong decision_log.csv."
        )
    lines += [
        f"✓ Report: {md_path.relative_to(base)} và {html_path.relative_to(base)}",
        "! Hãy tự quyết định ai đúng và ghi vào comparison_log.csv.",
    ]
    return lines
