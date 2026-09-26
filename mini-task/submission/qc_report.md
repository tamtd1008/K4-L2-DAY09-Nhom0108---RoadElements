# QC report

Họ tên: TODO · Chế độ: TODO (`cá nhân` hoặc `nhóm`) · Nếu nhóm — các thành viên: TODO
Guideline dùng: `GUIDE.md` + 4 card, bản phát ngày học.

Viết ở phút 205–225. Xoá mọi chữ `TODO` khi xong — `make check` đếm chữ này.

- **Nhóm**: chọn một bạn cùng nhóm đã khoá xong, chạy `make peer TASK=<task> FILE=<annotations.xml của họ>
  CODE=<mã khoá của họ> NAME=<tên họ>`. Lệnh tự viết `submission/<task>/peer-<tên>.html` và `.txt` — mở file
  `.html` bằng trình duyệt để xem overlay hai bài. Report này là bạn review **bài đã khoá của họ**, không phải
  bản của mình.
- **Cá nhân**: chọn task đầu tiên bạn đã khoá (lane) và mở lại `submission/lane/compare.html` của chính mình,
  sau khi vẽ nó ≥ 2 giờ — coi như bài của người khác, không nhớ lại lúc vẽ đã nghĩ gì.

## 1. Sample plan

Không đủ thời gian xem hết. Chọn **6 sample** và nói vì sao chọn. Lấy theo lát dễ lỗi (ngã tư, crosswalk, đêm/mưa,
lóa, biển nhỏ, điểm chuyển state), không lấy ngẫu nhiên.

| # | Task | Sample (ảnh / frame) | Lát (vì sao chọn) |
|---|---|---|---|
| 1 | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO |
| 4 | TODO | TODO | TODO |
| 5 | TODO | TODO | TODO |
| 6 | TODO | TODO | TODO |

## 2. Lỗi tìm thấy

Ít nhất 1 lỗi geometry, 1 lỗi attribute và 1 ca cần vào decision log. Nếu không tìm thấy loại nào, ghi rõ "đã xem,
không có".

- `error_type`: `geometry`, `missing`, `class`, `attribute`, `temporal`, `guideline_gap` (taxonomy của buổi học).
- `severity` (quy ước của lab, không phải thang của doanh nghiệp):
  `critical` = đổi quyết định của ego (state/relevance sai, drivable lấn sang làn ngược chiều, mất lane ngay trước xe);
  `major` = sai attribute hoặc geometry mà model sẽ học theo; `minor` = lệch nhỏ, không đổi nghĩa.
- `action`: `accept`, `rework`, `escalate`.

| Task | Sample | Object | Mô tả lỗi | error_type | severity | action | Downstream sai gì nếu bỏ qua |
|---|---|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

## 3. Kết luận cho batch

- Accept / rework / escalate cả batch, và lý do: TODO
- Note cho người label (1–2 câu, nói cách sửa — với cá nhân thì viết cho chính mình): TODO
- Known limitation phải ghi khi handoff (điều guideline chưa quyết): TODO
