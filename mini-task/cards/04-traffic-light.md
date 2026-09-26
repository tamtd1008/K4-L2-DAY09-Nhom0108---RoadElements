# Card 4 — Traffic light · phút 160–205

**Câu hỏi của task:** box quanh đèn không đủ để quyết định dừng hay đi. Cần `state` đúng ở **từng frame**, `relevance`
có bằng chứng, và cùng một đầu đèn giữ cùng một track qua chuỗi frame.

## Nhịp 45 phút

| Phút | Việc |
|---|---|
| 160–164 | Tạo task `light-<tên bạn>`, label từ `data/traffic_light/schema.json`, upload **cả 30 frame** `data/traffic_light/core/` |
| 164–177 | Vẽ **Rectangle → Track** cho từng đầu đèn (GUIDE mục 3.3). Kéo box ở frame nó lệch rõ |
| 177–184 | Attribute Annotation Mode: đi từng frame, kiểm `state` |
| 184–188 | Điền `light_log.md` mục 1–3 + self-QC theo checklist bên dưới |
| 188–190 | Export **`CVAT for video 1.1`** → `make lock TASK=traffic_light FILE=…` (ghi mã khoá in ra vào bài) |
| 190–195 | Nhóm: đổi mã khoá + file `submission/traffic_light/annotations.xml` với ít nhất 1 bạn, `make peer TASK=traffic_light FILE=<file nhận được> CODE=<mã nhận được> NAME=<tên bạn ấy>`, bàn khác biệt (≤ 5 phút; chưa kịp thì làm sau ở phút 205–225). Cá nhân: ghi log trước |
| 195–202 | `make reference TASK=traffic_light` → `make compare TASK=traffic_light` → ghi log + `light_log.md` mục 4 |
| 202–205 | Debrief (mục cuối card) |

30 frame liên tiếp, xe tiến tới một ngã tư (LISA Traffic Light Dataset). Frame đếm từ 0.

## Quy tắc

1. **Một box cho một đầu đèn**, sát vỏ đèn, không lấy cột hay giá treo.
2. **Track, không phải Shape:** cùng một đầu đèn vật lý giữ một track suốt chuỗi. CVAT nội suy vị trí box giữa hai
   keyframe; `state` thì giữ nguyên giá trị của keyframe trước cho tới khi bạn đổi. Đổi `state` ở frame nào, CVAT tự
   tạo keyframe ở frame đó — nhưng không tự kéo box, nên box lệch thì bạn phải kéo.
3. **Đèn ra khỏi khung hoặc bị che hẳn trước frame cuối → đặt `outside`** ở frame đó (GUIDE mục 3.3). Không đặt, export
   sẽ có box "ma" kéo dài tới frame 29.
4. `state` đổi được theo frame. `pictogram` và `relevance` cố định cho cả track.
5. **Relevance theo đường đi của ego:** xác định làn/hướng của ego → đèn thuộc nhóm làn nào (vị trí, giá treo,
   mũi tên) → loại đèn người đi bộ/đường cắt ngang. Không đủ bằng chứng → `unknown`, bật `needs_review`.
6. **Dùng frame trước/sau để lấy ngữ cảnh, không để bịa state** khi đèn bị che hoặc lóa. Không thấy → `unknown`.

## Self-QC trước khi export

- [ ] Không bỏ sót đầu đèn có mũi tên.
- [ ] Mỗi đầu đèn đúng một track, không đứt thành hai track.
- [ ] Track nào kết thúc trước frame 29 đã có `outside`.
- [ ] Không có frame nào state nhảy vô lý (đỏ → xanh → đỏ trong 2 frame).
- [ ] Mỗi track có `relevance` và bằng chứng trong `light_log.md`.

## Sau `make compare`

Tool ghép theo tâm box và so `state` / `pictogram` từng frame; in các khoảng frame lệch, frame reference đổi state,
khoảng frame chỉ một bên có box (kết thúc sớm hoặc thiếu `outside`) và đèn bị tách thành nhiều track.
Reference là LISA: **không có `relevance`** và **không gán đèn nhỏ ở ngã tư phía xa**. Track của bạn không khớp
reference chưa chắc là thừa — quyết định giữ/bỏ và ghi lý do vào `light_log.md`.

- `comparison_log.csv`: ≥ 2 dòng `task = traffic_light` (lỗi thời gian dùng `error_type = temporal`).
- `decision_log.csv`: ≥ 1 rule (gợi ý: state ở frame chuyển; đèn xa có vẽ không).
- `scale_100k.md` mục Traffic light.

## Debrief (3 phút)

Ghi ngắn vào `scale_100k.md` mục Traffic light: ở frame chuyển state bạn không chắc, bạn quyết định thế nào? Bỏ sót
`outside` hoặc gán sai `relevance` sẽ khiến model học sai gì về hành vi dừng/đi?

**Stretch:** vẽ các đầu đèn nhỏ ở ngã tư phía xa thành track riêng, đặt `relevance`, đọc state ở frame chuyển.
