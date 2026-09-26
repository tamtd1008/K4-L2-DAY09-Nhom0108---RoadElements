"""Freeze gold, xác minh và tạo blind handoff không lộ đáp án."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import subprocess
from typing import Dict, List, Optional, Sequence, Tuple
import zipfile

from . import LabError
from .catalog import load_catalog, media_path, validate_sample_pack
from .common import challenge_config, is_filled, parse_key_values, read_csv, read_json, require_columns, sha256_text, sha256_text_file

GOLD_COLUMNS = ["sample_id", "decision_id", "expected", "severity", "rationale"]
FREEZE_FILES = {
    "sha256_gold_decisions": "project/04_edge_cases/gold_decisions.csv",
    "sha256_sample_pack": "project/sample_pack.csv",
    "sha256_guideline": "project/02_guideline.md",
    "sha256_cvat_labels": "project/03_cvat_labels.json",
}
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def guideline_version(base: Path) -> int:
    """Đọc version vN từ guideline."""
    path = base / "project" / "02_guideline.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise LabError(f"Không đọc được {path}: {error}") from error
    match = re.search(r"(?im)^\W*version\W*:\W*v(\d+)", text)
    return int(match.group(1)) if match else 0


def valid_labels(base: Path) -> bool:
    """CVAT Raw labels phải là list có ít nhất một name không rỗng."""
    try:
        labels = read_json(base / "project" / "03_cvat_labels.json")
    except LabError:
        return False
    return isinstance(labels, list) and any(
        isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip()
        for item in labels
    )


def load_gold(base: Path) -> List[Dict[str, str]]:
    """Đọc gold decisions đúng schema."""
    path = base / "project" / "04_edge_cases" / "gold_decisions.csv"
    header, rows = read_csv(path)
    require_columns(path, header, GOLD_COLUMNS)
    return rows


def _freeze_validation(base: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[str], List[str]]:
    """Trả sample/gold cùng lỗi và cảnh báo, chưa ghi gì."""
    config = challenge_config(base)
    pack_rows, pack_errors = validate_sample_pack(base)
    _, catalog = load_catalog(base)
    errors = list(pack_errors)
    warnings: List[str] = []
    version = guideline_version(base)
    if version < 2:
        errors.append("guideline phải có version >= v2")
    if not valid_labels(base):
        errors.append("03_cvat_labels.json phải có ít nhất một label name")
    if not is_filled(base / "project" / "05_qa_plan.md"):
        warnings.append("05_qa_plan.md còn TODO — QA plan làm cùng lúc freeze (140–160'), gate G6 sẽ kiểm.")
    by_split = {}
    for split in ("example", "calibration", "blind"):
        unique = {}
        for row in pack_rows:
            if row["split"] == split:
                unique.setdefault(row["sample_id"], row)
        by_split[split] = list(unique.values())
    if not by_split["example"]:
        errors.append("sample_pack cần ít nhất 1 example")
    if not by_split["calibration"]:
        errors.append("sample_pack cần ít nhất 1 calibration")
    if len(by_split["blind"]) < 4:
        errors.append("sample_pack cần ít nhất 4 blind sample")
    blind_tags = [{item for item in row["tags"].split(";") if item} for row in by_split["blind"]]
    for tag, minimum in (("normal", 1), ("edge", 2), ("critical", 1)):
        if sum(tag in tags for tags in blind_tags) < minimum:
            errors.append(f"blind split cần ít nhất {minimum} sample có tag {tag}")
    if len(by_split["blind"]) >= 5 and not any("ambiguity" in tags for tags in blind_tags):
        errors.append("blind split từ 5 sample cần ít nhất 1 tag ambiguity")
    if by_split["example"] and not 3 <= len(by_split["example"]) <= 5:
        warnings.append("Số example nên trong khoảng 3–5.")
    if by_split["calibration"] and not 5 <= len(by_split["calibration"]) <= 8:
        warnings.append("Số calibration nên trong khoảng 5–8.")
    if len(by_split["blind"]) > 5:
        warnings.append("Blind split có hơn 5 sample.")
    nonblind_frames = []
    for row in by_split["example"] + by_split["calibration"]:
        info = catalog.get(row["sample_id"], {})
        match = re.search(r"\bframe\s+(\d+)\b", info.get("sequence", ""))
        if info.get("source") == "lisa" and match:
            nonblind_frames.append((int(match.group(1)), row["sample_id"]))
    leaked = []
    for row in by_split["blind"]:
        info = catalog.get(row["sample_id"], {})
        match = re.search(r"\bframe\s+(\d+)\b", info.get("sequence", ""))
        if info.get("source") == "lisa" and match:
            near = [sample for value, sample in nonblind_frames if abs(int(match.group(1)) - value) <= 2]
            if near:
                leaked.append(f"{row['sample_id']} (sát {', '.join(near)})")
    if leaked:
        warnings.append(
            "Nguy cơ temporal leakage — frame blind cách frame example/calibration ≤ 2 frame, peer gần như đã thấy ảnh: "
            + "; ".join(leaked)
            + ". Nên đổi sang frame xa hơn."
        )

    try:
        gold_rows = load_gold(base)
    except LabError as error:
        errors.append(str(error))
        gold_rows = []
    severities = {str(value).lower() for value in config["enums"]["severity"]}
    blind_ids = {row["sample_id"] for row in by_split["blind"]}
    keys = set()
    counts = {sample_id: 0 for sample_id in blind_ids}
    critical = 0
    geometry = 0
    for number, row in enumerate(gold_rows, 2):
        missing = [name for name in GOLD_COLUMNS if not row.get(name, "").strip()]
        if missing:
            errors.append(f"gold dòng {number} thiếu: {', '.join(missing)}")
        severity = row.get("severity", "").lower()
        if severity and severity not in severities:
            errors.append(f"gold dòng {number} có severity không hợp lệ: {severity}")
        key = (row.get("sample_id", ""), row.get("decision_id", ""))
        if key in keys:
            errors.append(f"gold trùng key {key[0]}/{key[1]}")
        keys.add(key)
        if key[0] not in blind_ids:
            errors.append(f"gold sample {key[0] or '(rỗng)'} không thuộc blind split")
        else:
            counts[key[0]] += 1
        critical += severity == "critical"
        geometry += row.get("expected", "").lower().startswith("geometry:")
    for sample_id, count in counts.items():
        if count == 0:
            errors.append(f"blind sample {sample_id} chưa có gold decision")
    if len(gold_rows) < 10:
        errors.append("gold cần ít nhất 10 decisions")
    if critical < 2:
        errors.append("gold cần ít nhất 2 critical decisions")
    if geometry == 0:
        errors.append("gold cần ít nhất 1 geometry decision")
    if gold_rows and geometry == len(gold_rows):
        errors.append("gold cần ít nhất 1 decision không phải geometry (D chiếm 60% GTS, không có thì không tính được)")
    return pack_rows, gold_rows, errors, warnings


def _git(base: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(base), *args], check=False, capture_output=True, text=True
    )


def _tagged_blob(base: Path, relative: str) -> Optional[bytes]:
    """Byte của file ở tag gold-freeze như lưu trong repo, chưa qua filter checkout của clone này."""
    result = subprocess.run(
        ["git", "-C", str(base), "cat-file", "blob", f"gold-freeze:./{relative}"], check=False, capture_output=True
    )
    return None if result.returncode else result.stdout


FREEZE_PATHS = [*FREEZE_FILES.values(), "project/FREEZE.txt"]
# Refreeze đẩy đè tag trên GitHub; fetch --tags thường từ chối ghi đè tag cũ đã có trong clone.
SYNC_TAG = "git pull && git fetch --tags --force"
RESTORE_RECEIPT = "git restore --source=gold-freeze -- project/FREEZE.txt"


def _freeze_message(version: int) -> str:
    return f"gold: freeze blind decisions (guideline v{version})"


def _push_command(move_tag: bool) -> str:
    # Tag đã có trên GitHub thì --follow-tags từ chối cập nhật, phải đẩy đè tag.
    return "git push && git push -f origin gold-freeze" if move_tag else "git push --follow-tags"


def _git_detail(result: subprocess.CompletedProcess[str]) -> str:
    detail = result.stderr.strip().splitlines()
    return f" ({detail[-1]})" if detail else ""


def _require_git_clone(base: Path) -> None:
    """Tag gold-freeze là bằng chứng G4, nên freeze/verify/handoff/score chỉ chạy trong clone repo nhóm."""
    if shutil.which("git") is None:
        raise LabError(
            "Máy chưa có git trên PATH nên không commit/gắn tag gold-freeze được. Cài git, hoặc làm bước này trên"
            " máy bạn cùng nhóm, trong clone của repo nhóm."
        )
    # Trong thư mục .git hay repo bare, rev-parse vẫn exit 0 nhưng in "false".
    inside = _git(base, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode or inside.stdout.strip() != "true":
        raise LabError(
            "Thư mục này không phải git clone (có thể tải ZIP hoặc chép thư mục ra ngoài) nên không có tag"
            " gold-freeze làm bằng chứng. Mở lab trong clone của repo nhóm (git clone), chép project/ vào đó rồi"
            " chạy lại lệnh."
        )


class _GitFreezeNotCommitted(LabError):
    """Git chưa tạo được commit freeze; freeze_project hoàn tác FREEZE.txt."""


def _commit_freeze(base: Path, version: int, move_tag: bool) -> List[str]:
    """Commit đúng các file freeze rồi gắn annotated tag gold-freeze."""
    message = _freeze_message(version)
    push = _push_command(move_tag)
    add = _git(base, ["add", "--", *FREEZE_PATHS])
    step = add if add.returncode else _git(base, ["commit", "-m", message, "--", *FREEZE_PATHS])
    if step.returncode:
        _git(base, ["reset", "-q", "--", *FREEZE_PATHS])
        raise _GitFreezeNotCommitted(
            f"Git chưa commit được{_git_detail(step)}, nên chưa freeze. Thường do git chưa có tên/email:"
            ' git config user.name "Tên bạn" và git config user.email "email@...", rồi chạy lại lệnh freeze.'
        )
    # Annotated tag: `git push --follow-tags` chỉ đẩy annotated tag, lightweight tag nằm lại trên máy.
    tag_args = ["tag", "-a", "-f", "-m", message, "gold-freeze"]
    tag = _git(base, tag_args)
    if tag.returncode:
        raise LabError(
            f"Đã commit freeze nhưng chưa gắn được tag{_git_detail(tag)}. Chạy:"
            f' git tag -a -f -m "{message}" gold-freeze && {push}'
        )
    return ["✓ Đã commit và gắn tag gold-freeze.", f"  Push ngay để Lab Coach thấy tag trên GitHub: {push}"]


def freeze_project(base: Path, refreeze: bool = False) -> List[str]:
    """Validate toàn bộ rồi ghi FREEZE.txt, commit và gắn tag; git lỗi thì không để lại freeze dở."""
    freeze_path = base / "project" / "FREEZE.txt"
    peer_output = base / "project" / "07_blind_handoff" / "peer_output"
    if freeze_path.exists() and not refreeze:
        raise LabError("FREEZE.txt đã tồn tại; chỉ refreeze khi chủ động dùng REFREEZE=1.")
    if refreeze and any(path.suffix.lower() in {".zip", ".xml"} for path in peer_output.glob("*")):
        raise LabError(
            "Không được refreeze sau khi đã có peer export. Giữ gold đã freeze; lỗi gold ghi `gold sai:` trong note của"
            " transfer_score.csv và sửa ở guideline v3 + revision log."
        )
    pack_rows, gold_rows, errors, warnings = _freeze_validation(base)
    if errors:
        raise LabError("Không thể freeze:\n- " + "\n- ".join(errors))
    _require_git_clone(base)
    if not refreeze and _has_freeze_tag(base):
        # Hai người cùng freeze sẽ ra hai tag khác nhau và GitHub chỉ giữ tag push trước.
        raise LabError(
            "Clone này đã có tag gold-freeze nhưng thiếu project/FREEZE.txt — có thể bạn cùng nhóm đã freeze: chạy"
            f" git pull. Vẫn thiếu (lỡ xoá FREEZE.txt): {RESTORE_RECEIPT}. Nếu nhóm cần freeze lại và chưa nhận"
            " export của peer: make freeze REFREEZE=1."
        )
    previous_receipt = freeze_path.read_bytes() if freeze_path.exists() else None
    previous_count = 0
    if previous_receipt is not None:
        try:
            previous_count = int(parse_key_values(freeze_path).get("refreeze_count", "0"))
        except ValueError:
            previous_count = 0
    values = {
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "guideline_version": str(guideline_version(base)),
        **{key: sha256_text_file(base / relative) for key, relative in FREEZE_FILES.items()},
        "decisions": str(len(gold_rows)),
        "critical": str(sum(row["severity"].lower() == "critical" for row in gold_rows)),
        "blind_samples": str(len({row["sample_id"] for row in pack_rows if row["split"] == "blind"})),
    }
    if refreeze:
        values["refreeze_count"] = str(previous_count + 1)
    freeze_path.write_text("".join(f"{key}={value}\n" for key, value in values.items()), encoding="utf-8")
    try:
        git_lines = _commit_freeze(base, int(values["guideline_version"]), move_tag=refreeze)
    except _GitFreezeNotCommitted:
        if previous_receipt is None:
            freeze_path.unlink()
        else:
            freeze_path.write_bytes(previous_receipt)
        raise
    lines = [f"! {warning}" for warning in warnings]
    lines.append(f"✓ Đã freeze {len(gold_rows)} decisions cho guideline v{values['guideline_version']}.")
    lines.extend(git_lines)
    return lines


def _receipt_changes(base: Path, keys: Sequence[str]) -> Tuple[Dict[str, str], List[str]]:
    """Đọc FREEZE.txt và trả các file có hash khác receipt."""
    path = base / "project" / "FREEZE.txt"
    if not path.is_file():
        if shutil.which("git") and _has_freeze_tag(base):
            raise LabError(f"Thiếu project/FREEZE.txt dù clone đã có tag gold-freeze — chạy {SYNC_TAG}; vẫn thiếu thì {RESTORE_RECEIPT}.")
        raise LabError("Chưa có project/FREEZE.txt — chạy make freeze trước.")
    values = parse_key_values(path)
    changed = [FREEZE_FILES[key] for key in keys if values.get(key) != sha256_text_file(base / FREEZE_FILES[key])]
    return values, changed


def _has_freeze_tag(base: Path) -> bool:
    return not _git(base, ["rev-parse", "-q", "--verify", "gold-freeze^{commit}"]).returncode


def _tag_changes(base: Path, relatives: Sequence[str]) -> List[str]:
    """Các file có nội dung khác bản ở tag gold-freeze."""
    differs = []
    for relative in relatives:
        tagged = _tagged_blob(base, relative)
        # So nội dung đã quy CRLF về LF, không so blob id: blob ở tag phụ thuộc autocrlf của máy đã commit,
        # không phải của clone đang kiểm tra.
        try:
            current = sha256_text_file(base / relative)
        except LabError:
            current = None
        if tagged is None or current != sha256_text(tagged):
            differs.append(relative)
    return differs


def _tagged_receipt_problem(base: Path, tagged: Dict[str, str]) -> Optional[str]:
    """FREEZE.txt ở tag phải có và khớp các file trong chính commit đó, nếu không tag chưa chứng minh được freeze."""
    if not tagged:
        return "Commit ở tag gold-freeze không có project/FREEZE.txt — tag không trỏ vào commit do make freeze tạo."
    if _parse_utc(tagged.get("frozen_at", "")) is None:
        return "FREEZE.txt ở tag gold-freeze thiếu frozen_at hợp lệ."
    for key, relative in FREEZE_FILES.items():
        blob = _tagged_blob(base, relative)
        if blob is None or tagged.get(key) != sha256_text(blob):
            return f"FREEZE.txt ở tag gold-freeze không khớp {relative} trong chính commit đó."
    return None


def _require_freeze_tag(base: Path) -> None:
    _require_git_clone(base)
    if not _has_freeze_tag(base):
        raise LabError(
            "Chưa có tag gold-freeze trong clone này. Nếu nhóm đã freeze ở máy khác và push tag lên GitHub, chạy"
            f" {SYNC_TAG}; chưa freeze thì chạy make freeze."
        )
    problem = _tagged_receipt_problem(base, _tagged_receipt(base))
    if problem:
        raise LabError(f"{problem} Nhóm vừa refreeze ở máy khác thì chạy {SYNC_TAG}; nếu không, hỏi Lab Coach.")


def freeze_integrity(base: Path, include_guideline: bool = False, include_labels: bool = False) -> Tuple[Dict[str, str], List[str]]:
    """Trả các file đã đổi sau freeze, so với cả FREEZE.txt lẫn bản ở tag gold-freeze."""
    keys = ["sha256_gold_decisions", "sha256_sample_pack"]
    if include_guideline:
        keys.append("sha256_guideline")
    if include_labels:
        keys.append("sha256_cvat_labels")
    values, changed = _receipt_changes(base, keys)
    # FREEZE.txt sửa tay được; tag mới là mốc so sánh. So chính các file freeze với tag, không so FREEZE.txt:
    # hai lần freeze cùng nội dung chỉ khác frozen_at.
    _require_freeze_tag(base)
    changed.extend(relative for relative in _tag_changes(base, [FREEZE_FILES[key] for key in keys]) if relative not in changed)
    return values, changed


def _parse_utc(value: str) -> Optional[datetime]:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _tagged_receipt(base: Path) -> Dict[str, str]:
    blob = _tagged_blob(base, "project/FREEZE.txt")
    if blob is None:
        return {}
    text = blob.decode("utf-8", errors="replace")
    return dict(
        (key.strip(), value.strip())
        for key, value in (line.split("=", 1) for line in text.splitlines() if "=" in line and not line.startswith("#"))
    )


def _git_freeze_lines(base: Path) -> Tuple[List[str], bool, Dict[str, str], List[str]]:
    """Đối chiếu working tree với tag gold-freeze: sửa cả gold lẫn FREEZE.txt vẫn lộ ở đây."""
    try:
        _require_git_clone(base)
    except LabError as error:
        return [f"✗ {error}"], False, {}, []
    if not _has_freeze_tag(base):
        # Tag là bằng chứng G4; thiếu tag thì FREEZE.txt (sửa tay được) không đủ để xác minh.
        return ["✗ Không có tag gold-freeze — nhóm chưa push tag (git push origin gold-freeze) hoặc clone chưa fetch tag."], False, {}, []
    tag = _git(base, ["rev-parse", "-q", "--verify", "gold-freeze^{commit}"])
    lines = [f"✓ Tag gold-freeze: {tag.stdout.strip()}"]
    tagged = _tagged_receipt(base)
    problem = _tagged_receipt_problem(base, tagged)
    if problem:
        lines.append(f"✗ {problem}")
        tagged = {}
    differs = _tag_changes(base, [FREEZE_FILES["sha256_gold_decisions"], FREEZE_FILES["sha256_sample_pack"]])
    peer_dir = "project/07_blind_handoff/peer_output/"
    # -z: tên file tiếng Việt không bị git quote nên đuôi .xml/.zip vẫn nhận ra.
    tagged_peer = [
        Path(name).name
        for name in _git(base, ["ls-tree", "-r", "-z", "--name-only", "gold-freeze", "--", peer_dir]).stdout.split("\0")
        if Path(name).suffix.lower() in {".zip", ".xml"}
    ]
    if differs:
        lines.append("✗ Khác bản đã commit ở tag gold-freeze: " + ", ".join(differs))
        lines.append(f"  Nhóm vừa refreeze ở máy khác thì lấy tag mới: {SYNC_TAG}")
    else:
        lines.append("✓ Gold và sample pack khớp tag gold-freeze.")
    if tagged_peer:
        lines.append("✗ Commit gold-freeze đã chứa peer export (" + ", ".join(tagged_peer) + ") — gold được freeze sau khi thấy output peer.")
    return lines, not problem and not differs and not tagged_peer, tagged, tagged_peer


def verify_freeze(base: Path) -> Tuple[List[str], bool]:
    """Tóm tắt freeze, hash, đối chiếu tag git và thời điểm peer export."""
    # Receipt và tag báo riêng từng dòng để Lab Coach thấy lệch ở đâu.
    values, changed = _receipt_changes(base, ["sha256_gold_decisions", "sha256_sample_pack"])
    git_lines, git_ok, tagged, tagged_peer = _git_freeze_lines(base)
    # Thời điểm freeze lấy từ tag khi có: FREEZE.txt ở working tree sửa tay được.
    frozen_value = tagged.get("frozen_at") or values.get("frozen_at", "")
    lines = [
        f"✓ Freeze lúc: {frozen_value or '(không rõ)'}",
        f"✓ Guideline version: v{tagged.get('guideline_version') or values.get('guideline_version', '?')}",
        ("✗ Gold decisions đã đổi sau freeze." if "project/04_edge_cases/gold_decisions.csv" in changed else "✓ Gold decisions còn nguyên."),
        ("✗ Sample pack đã đổi sau freeze." if "project/sample_pack.csv" in changed else "✓ Sample pack còn nguyên."),
    ]
    lines.extend(git_lines)
    if tagged.get("frozen_at") and values.get("frozen_at") != tagged["frozen_at"]:
        lines.append(
            f"! frozen_at trong FREEZE.txt ({values.get('frozen_at', '?')}) khác bản ở tag — có lần freeze khác chưa"
            " lên tag; dùng thời điểm ở tag."
        )
    peer_output = base / "project" / "07_blind_handoff" / "peer_output"
    frozen_at = _parse_utc(frozen_value)
    if frozen_at is None:
        lines.append("! frozen_at trong FREEZE.txt không đọc được — bỏ qua so sánh thời điểm peer export.")
    else:
        # Peer export bình thường đến SAU freeze; file có mtime trước freeze mới đáng hỏi lại nhóm.
        # File đã nằm trong commit gold-freeze bị báo ✗ ở trên, không so mtime nữa.
        exports = [
            path
            for path in peer_output.glob("*")
            if path.is_file() and path.suffix.lower() in {".zip", ".xml"} and path.name not in tagged_peer
        ]
        older = sorted(path.name for path in exports if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < frozen_at)
        newer = sorted(path.name for path in exports if path.name not in older)
        if newer:
            lines.append("✓ Peer export sau freeze: " + ", ".join(newer))
        if older:
            lines.append("! Peer export có thời điểm sửa trước freeze, hỏi lại nhóm: " + ", ".join(older))
        elif not tagged_peer:
            lines.append("✓ Không có peer export nào cũ hơn thời điểm freeze.")
    return lines, not changed and git_ok


def _zip_entry(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def _peer_readme() -> str:
    return """# Blind handoff

Bạn có 15 phút để đọc guideline và gắn nhãn các ảnh trong `images/`.

1. Tạo CVAT task từ `images/`, dùng raw labels trong `cvat_labels.json`, đặt guideline vào Guide.
2. Không hỏi owner về domain rule; hãy ghi mọi câu hỏi vào clarification log của owner.
3. Export `CVAT for images 1.1`; nếu task dùng track, export `CVAT for video 1.1`.
4. Gửi lại ZIP export cùng câu trả lời cho 5 câu hỏi:
   - Rule nào rõ nhất / giúp quyết định nhanh nhất?
   - Rule nào mơ hồ hoặc phải tự suy diễn?
   - Sample nào khiến guideline “vỡ”?
   - Attribute/default nào trong CVAT dễ gây thao tác sai?
   - Một thay đổi cụ thể giúp annotator mới ít hỏi hơn?
"""


def create_handoff(base: Path) -> List[str]:
    """Dựng ZIP deterministic chỉ gồm guideline, labels và blind images."""
    _, changed = freeze_integrity(base, include_guideline=True, include_labels=True)
    if changed:
        raise LabError(
            "Không thể handoff vì file đã đổi sau freeze: "
            + ", ".join(changed)
            + ". Hoàn tác (git checkout gold-freeze -- <file>) hoặc, nếu chưa gửi gói cho peer, chạy make freeze REFREEZE=1."
        )
    pack_rows, errors = validate_sample_pack(base)
    if errors:
        raise LabError("sample_pack.csv chưa hợp lệ:\n- " + "\n- ".join(errors))
    _, catalog = load_catalog(base)
    entries = {
        "guideline.md": (base / "project" / "02_guideline.md").read_bytes(),
        "cvat_labels.json": (base / "project" / "03_cvat_labels.json").read_bytes(),
        "PEER_README.md": _peer_readme().encode("utf-8"),
    }
    for row in pack_rows:
        if row["split"] != "blind":
            continue
        source = media_path(base, catalog[row["sample_id"]])
        entries[f"images/{source.name}"] = source.read_bytes()
    output = base / "handoff" / "blind-pack.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        for name in sorted(entries):
            _zip_entry(archive, name, entries[name])
    return [f"✓ Đã ghi handoff/blind-pack.zip với {sum(name.startswith('images/') for name in entries)} ảnh blind."]
