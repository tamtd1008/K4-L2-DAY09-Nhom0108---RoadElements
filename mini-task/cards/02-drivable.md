# Card 2 — Drivable area · phút 70–110

**Câu hỏi của task:** ego được đi vào đâu? Polygon là vùng chức năng theo luật, không phải "tô hết nhựa đường".

## Nhịp 40 phút

| Phút | Việc |
|---|---|
| 70–73 | Tạo task `drivable-<tên bạn>`, label từ `data/drivable/schema.json`, upload 5 ảnh `data/drivable/core/` |
| 73–90 | Vẽ `direct` trước, `alternative` sau, tag `image_context` cho cả 5 ảnh + self-QC theo checklist bên dưới |
| 90–92 | Export `CVAT for images 1.1` → `make lock TASK=drivable FILE=…` (ghi mã khoá in ra vào bài) |
| 92–97 | Nhóm: đổi mã khoá + file `submission/drivable/annotations.xml` với ít nhất 1 bạn, `make peer TASK=drivable FILE=<file nhận được> CODE=<mã nhận được> NAME=<tên bạn ấy>`, bàn khác biệt (≤ 5 phút; chưa kịp thì làm sau ở phút 205–225). Cá nhân: ghi log trước |
| 97–107 | `make reference TASK=drivable` → `make compare TASK=drivable` → ghi log |
| 107–110 | Debrief (mục cuối card) |

## 5 ảnh core

| Ảnh | Để ý |
|---|---|
| `bb5cc516` | Mưa, giá gắn kính che góc ảnh |
| `be860305` | Đêm, có crosswalk |
| `c068a67b` | Phố, xe đỗ hai bên |
| `c3cd6c82` | Cao tốc cong — cùng ảnh với task lane, dùng vạch bạn đã vẽ để tách làn |
| `c723ad21` | Hầm chui, tối |

## Quy tắc

1. **`direct`** = làn ego đang đi, có quyền ưu tiên. **`alternative`** = làn ego chưa đi nhưng tới được bằng cách
   chuyển làn (định nghĩa của BDD100K). Nền (background) không vẽ.
2. **Vùng chức năng, không phải màu:** xét curb, đảo, vỉa hè, hướng giao thông, vật cản.
3. **Tách region:** mỗi vùng `alternative` rời nhau là một polygon riêng. Không gộp cho polygon "đẹp".
4. **Không kéo polygon vào chỗ không nhìn thấy** (tối, xa, bị che) trừ khi decision log cho phép.
5. **Không tự cắt chéo polygon.** Vùng rời nhau → nhiều polygon.
6. Giảm opacity để thấy vạch và curb bên dưới khi chỉnh biên.

Ca bạn phải tự quyết và ghi decision log: vùng sau xe đỗ có tính không; crosswalk thuộc vùng nào; biên ở hầm tối.

## Self-QC trước khi export

- [ ] Không lấn vỉa hè, đảo, làn ngược chiều bị ngăn bởi vạch/đảo.
- [ ] Không bỏ sót làn `alternative` hay làn rẽ.
- [ ] Không polygon nào còn `areaType = __undefined__`.
- [ ] Không có polygon kéo quá vùng nhìn thấy.

## Sau `make compare`

Tool in IoU **từng ảnh**, tách `direct` / `alternative` / mọi vùng. Không có số trung bình cả tập, và IoU không phải
điểm. Dòng "hình khớp reference …, khác areaType" nghĩa là polygon của bạn trùng hình một polygon reference nhưng gán khác
loại — phần sai loại được báo riêng là `attribute`; nếu biên vẫn còn lệch thì phần lệch đó vẫn là `geometry`. Ranh giới `direct` / `alternative` đặt lệch thì vẫn là `geometry`. Reference là polygon BDD100K, không có `needs_review`.

- `comparison_log.csv`: ≥ 2 dòng `task = drivable`.
- `decision_log.csv`: ≥ 1 rule.
- `scale_100k.md` mục Drivable area.

## Debrief (3 phút)

Ghi ngắn vào `scale_100k.md` mục Drivable area: bạn từng gán sai `direct`/`alternative` ở đâu, vì sao? Vùng nào
(sau xe đỗ, hầm tối, crosswalk) bạn thấy cần thêm rule rõ hơn cho người khác?

**Stretch:** task `drivable-stretch` với 9 ảnh `data/drivable/stretch/` (có tuyết che vạch, làn ngược chiều).
