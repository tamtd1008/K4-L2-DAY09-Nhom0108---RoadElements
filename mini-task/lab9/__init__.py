"""Công cụ offline cho lab Day 9."""

from __future__ import annotations

TASKS = ("lane", "drivable", "traffic_sign", "traffic_light")


class LabError(RuntimeError):
    """Lỗi đầu vào có hướng dẫn để học viên tự sửa."""

