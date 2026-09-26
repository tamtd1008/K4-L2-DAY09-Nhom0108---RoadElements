# Card 1 — Lane marking · phút 15–70

**Câu hỏi của task:** vạch này bảo xe được làm gì? Polyline chỉ có nghĩa khi `laneTypes`, `laneStyle`,
`laneDirection` đúng và nhất quán.

## Nhịp 55 phút

| Phút | Việc |
|---|---|
| 15–20 | Tạo task `lane-<tên bạn>` (GUIDE mục 2), label dán từ `data/lane/schema.json`, upload 6 ảnh `data/lane/core/` |
| 20–27 | Ảnh mẫu: mở `examples/lane-bb890202-d9d48310.png`, đọc 4 quyết định bên dưới, rồi tự vẽ lại đúng ảnh `bb890202` |
| 27–53 | Vẽ 5 ảnh còn lại + tag `image_context` cho cả 6 ảnh + self-QC theo checklist bên dưới |
| 53–55 | Export `CVAT for images 1.1` → `make lock TASK=lane FILE=…` (ghi mã khoá in ra vào bài) |
| 55–60 | Nhóm: đổi mã khoá + file `submission/lane/annotations.xml` với ít nhất 1 bạn cùng nhóm, `make peer TASK=lane FILE=<file nhận được> CODE=<mã nhận được> NAME=<tên bạn ấy>`, mở `submission/lane/peer-<tên>.html` bàn khác biệt (≤ 5 phút; bạn ấy chưa khoá kịp trong 3 phút thì bỏ qua, làm peer sau ở phút 205–225). Cá nhân: dùng phút này ghi log trước |
| 60–67 | `make reference TASK=lane` → `make compare TASK=lane` → ghi log (mục cuối card) |
| 67–70 | Debrief (mục cuối card) |

## Ảnh mẫu bb890202 — 4 quyết định

Reference lane trên `bb890202` là bản người thiết kế lab vẽ theo đúng quy tắc bên dưới. Đọc 4 quyết định sau trên
overlay trước khi tự vẽ lại ảnh này — đây là ảnh duy nhất bạn được so ngay với cách áp quy tắc, 5 ảnh còn lại thì
không có mẫu:

1. Vạch tim làn bên trái ngay trước xe: polyline dừng đúng tại góc sau xe SUV phía trước, không nối tiếp qua xe dù
   mặt đường vẫn thấy được ở phía xa hơn — bị che thì dừng, không đoán tiếp (quy tắc 3).
2. Vạch ranh giới làn xa hơn về bên trái: polyline dừng giữa mặt đường trống, không bị xe nào che — điểm dừng vì vạch
   nhạt dần khó chắc, không phải vì bị che (quy tắc 2, khác lý do với mục 1 dù cùng hành động "dừng line").
3. Vạch ở làn kế bên (gần xe màu bạc phía xa): polyline dừng đúng tại đuôi xe đó — cùng logic bị che như mục 1,
   áp cho một xe khác.
4. Vạch bên phải: điểm bắt đầu (gần xe mình) không ở sát mép dưới ảnh mà ở đúng chỗ vạch đứt bắt đầu hiện rõ (không
   kéo xuống chỗ chưa có sơn), rồi polyline đi tiếp qua khu vực nhiều vạch sơn chéo (làn tách/nhập) mà không rẽ theo
   từng nét sơn phụ — chỉ bám một ranh giới làn nhất quán.

## 6 ảnh core (thứ tự CVAT hiển thị)

| Ảnh | Để ý |
|---|---|
| `b75f355e` | Khu dân cư, vạch mờ |
| `bb890202` | Cao tốc, vạch đứt — ảnh mẫu |
| `c0f739d8` | Đường rộng, vạch liền tách ra làn rẽ |
| `c1589305` | Ngã tư: vạch qua đường, vạch dừng, xe che một phần |
| `c3cd6c82` | Cao tốc cong (ảnh này quay lại ở task drivable) |
| `c95fecc3` | Kính lóa, vạch xa mờ |

## Quy tắc (quy ước lớp học)

1. **Một polyline = một đoạn marking nhìn thấy, cùng một nghĩa.** Vạch đứt vẫn là một polyline duy nhất theo tim các
   đoạn đứt — không tách mỗi đoạn dash thành một polyline riêng. Không vẽ tâm làn khi task chỉ hỏi marking.
2. **Điểm đầu/cuối:** bắt đầu nơi marking đủ rõ; dừng khi nó biến mất, quá mờ, ra khỏi ảnh, hoặc bị che.
3. **Bị che:** không nối xuyên qua xe. Nếu bạn muốn nối, đó là một rule — ghi decision log và áp dụng cho mọi ảnh.
4. **Mật độ điểm:** đoạn thẳng ít điểm; đoạn cong thêm điểm nơi độ cong đổi. Không rải điểm theo vết nhựa đường.
5. **Attribute theo bằng chứng nhìn thấy.** Lóa, mờ, đêm làm bạn không chắc → chọn giá trị bạn thấy rõ nhất và bật
   `needs_review`, không đoán cho đủ.
6. **`crosswalk` và `road curb` là category riêng**, không gộp vào "lane line". Crosswalk thường là
   `laneDirection = vertical`.
7. `visibility` và `needs_review` là quy ước lớp học để QC, BDD100K không có — reference không so hai trường này.

## Self-QC trước khi export

- [ ] Mỗi polyline bám marking, không zig-zag; điểm cuối theo cùng một rule ở mọi ảnh.
- [ ] Không bỏ sót marking gần xe và ở ngã tư.
- [ ] Không polyline nào còn attribute `__undefined__`.
- [ ] Type/style không đổi chỉ vì ánh sáng đổi (so hai ảnh cùng loại vạch).
- [ ] 6 ảnh đều có tag `image_context` (weather, timeofday).

## Sau `make compare`

Reference lane do người thiết kế lab vẽ theo card này trên 6 ảnh core, **không phải GT chính thức BDD100K** (đọc
`gt/lane/README.md`). Khác reference chưa chắc là bạn sai — ghi `who_is_right` và lý do.

- `comparison_log.csv`: ≥ 2 dòng `task = lane`. Mở `submission/lane/compare.html` để nhìn trước khi kết luận.
- `decision_log.csv`: ≥ 1 rule cho một ca mơ hồ bạn gặp (gợi ý: endpoint khi vạch mờ dần, crosswalk, vạch tách làn rẽ).
- `scale_100k.md` mục Lane.

## Debrief (3 phút)

Ghi ngắn vào `scale_100k.md` mục Lane: lỗi geometry hay attribute nào bạn lặp lại ở nhiều ảnh nhất? Nếu phải viết
một rule cho lane marking để người khác theo đúng, rule đó là gì?

**Stretch** (xong sớm): tạo task `lane-stretch` với 10 ảnh `data/lane/stretch/`, áp rule vừa ghi. Không khoá, không nộp.
