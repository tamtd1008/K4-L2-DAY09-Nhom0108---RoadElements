# Card 3 — Traffic sign · phút 120–160

**Câu hỏi của task:** vẽ box thì dễ. Khó là chọn đúng `sign_family` → `sign_class` và biết khi nào **không** đủ
bằng chứng để chọn class.

## Nhịp 40 phút

| Phút | Việc |
|---|---|
| 120–123 | Tạo task `sign-<tên bạn>`, label từ `data/traffic_sign/schema.json`, upload 7 ảnh `data/traffic_sign/core/` |
| 123–133 | **Lượt 1 — geometry:** chỉ vẽ box, chưa chọn attribute |
| 133–141 | **Lượt 2 — attribute:** chuyển sang Attribute Annotation Mode (GUIDE mục 3.2), gán từng box + self-QC theo checklist bên dưới |
| 141–143 | Export `CVAT for images 1.1` → `make lock TASK=traffic_sign FILE=…` (ghi mã khoá in ra vào bài) |
| 143–148 | Nhóm: đổi mã khoá + file `submission/traffic_sign/annotations.xml` với ít nhất 1 bạn, `make peer TASK=traffic_sign FILE=<file nhận được> CODE=<mã nhận được> NAME=<tên bạn ấy>`, bàn khác biệt (≤ 5 phút; chưa kịp thì làm sau ở phút 205–225). Cá nhân: ghi log trước |
| 148–154 | `make reference TASK=traffic_sign` → `make compare TASK=traffic_sign` → ghi log |
| 154–157 | Viết `sign_tree.md` |
| 157–160 | Debrief (mục cuối card) |

## 7 ảnh core

`00026`, `00054`, `00073`, `00088`, `00108`, `00206`, `00223` (ảnh GTSDB, Đức, 1360×800). Có ảnh nhiều biển nhỏ
20–30 px, có cụm biển xếp chồng, và `00108` không có biển nào — khi đó không vẽ gì là đúng.

## Quy tắc (quy ước lớp học)

1. **Box sát mặt biển**, không lấy cột. Biển xếp chồng có nghĩa khác nhau → mỗi panel một box.
2. **Hai cấp:** `sign_family` (prohibitory / mandatory / danger / other) rồi `sign_class` (43 class GTSDB).
3. **Không zoom rồi suy diễn.** Biển quá nhỏ để đọc class: chọn family nếu thấy rõ hình/màu, `sign_class = unknown`,
   `readable = uncertain` hoặc `no`.
4. `readable`, `truncated`, `relevant_to_ego` là quy ước lớp học. GT GTSDB không có — tool không so, bạn tự ghi lý do.
5. `relevant_to_ego = yes` cần bằng chứng làn/nhánh. Không có → `unknown`.

## Self-QC trước khi export

- [ ] Quét lại từng ảnh tìm biển nhỏ ở mép và phía xa.
- [ ] Mỗi panel một box; không box nào ôm hai biển.
- [ ] Không box nào còn `__undefined__` ở `sign_family` / `sign_class`.
- [ ] Hai biển giống nhau thì cùng class (không drift giữa các ảnh).

## Sau `make compare`

Tool ghép box theo IoU ≥ 0.6 rồi so family và class. Box trên ảnh không có biển được báo là thừa.

- `comparison_log.csv`: ≥ 2 dòng `task = traffic_sign`.
- `decision_log.csv`: ≥ 1 rule (gợi ý: biển nhỏ đọc không ra class; biển xếp chồng).
- `sign_tree.md`: cây family → class cho biển bạn đã vẽ, và 2 quyết định merge/split.
- `scale_100k.md` mục Traffic sign.

## Debrief (3 phút)

Ghi ngắn vào `scale_100k.md` mục Traffic sign: `sign_class` nào bạn phải để `unknown`, vì sao? Nếu lỗi đọc nhầm
biển nhỏ lặp lại trên 100k ảnh, model sẽ học sai điều gì?

**Stretch:** task `sign-stretch` với ảnh trong `data/traffic_sign/stretch/` (có biển nhỏ nhất 20×19 px).
