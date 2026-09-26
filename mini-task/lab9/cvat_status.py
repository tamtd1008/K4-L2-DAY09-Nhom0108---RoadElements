"""Kiểm tra CVAT học viên đã cài từ ngày học trước."""

from __future__ import annotations

import json
import os
from typing import List
from urllib.error import URLError
from urllib.request import urlopen

from . import LabError


def check_cvat() -> List[str]:
    """Đọc phiên bản từ API CVAT mà không gọi Docker hoặc cài đặt gì."""
    url = (os.environ.get("CVAT_URL") or "http://localhost:8080").rstrip("/")
    try:
        with urlopen(f"{url}/api/server/about", timeout=5) as response:
            payload = json.load(response)
    except (URLError, OSError) as error:
        raise LabError(
            f"CVAT chưa chạy ở {url} — mở Docker Desktop, vào thư mục CVAT bạn đã cài "
            "(Day 2: cvat-day2, Day 8: cvat) rồi chạy docker compose start."
        ) from error
    return [f"✓ CVAT {payload['version']} tại {url}"]
