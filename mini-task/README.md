# Day 9 Lab — Road Elements trên CVAT · 240 phút

Bạn gắn nhãn 4 loại phần tử đường (lane marking, drivable area, traffic sign, traffic light) trên CVAT, rồi tự đối
chiếu bài của mình với reference có sẵn trong repo. Mục tiêu của buổi không phải vẽ nhiều, mà là **làm đúng rule, thấy
được chỗ mình khác reference, và quyết định ai đúng bằng bằng chứng**.

Lab Coach có mặt trong lớp suốt buổi để theo dõi tiến độ và hỗ trợ khi bạn kẹt. Nhưng luồng bài không chờ ai: bạn
tự khoá, tự mở reference, tự so sánh, tự ghi log. Mọi hướng dẫn nằm trong file này, `GUIDE.md` và 4 card; mọi thứ bạn
nộp nằm trong `submission/`. Khi nào gọi Lab Coach: xem mục [Khi bị kẹt](#khi-bị-kẹt).

## Làm một mình hay theo nhóm

Chọn một trong hai, làm suốt buổi:

Mỗi người tạo **repo riêng từ template bằng tài khoản GitHub của mình**. Không dùng chung repo, không fork repo của
trưởng nhóm; bài nộp được tính theo từng repo.

- **Cá nhân**: không chạy `make team`. Mỗi mini-task bạn tự vẽ, tự khoá, tự so với reference, không có bước đổi bài
  với ai. Thời gian đáng lẽ dùng để so bài nhóm thì dùng cho stretch hoặc ghi log kỹ hơn.
- **Nhóm 2–4 người**: chạy `make team MEMBERS="An, Bình"` (liệt kê đủ tên, cách nhau bằng dấu phẩy) trước phút 15.
  Mỗi người trong nhóm **vẫn tự vẽ toàn bộ ảnh core của mình** — nhóm không chia nhau vẽ. Trước khi khoá, chỉ hỏi
  nhau thao tác công cụ; đừng chốt chung cách xử lý ca mơ hồ — để dành cho lúc so peer, không thì hai bài không còn
  độc lập để so. Sau khi khoá, đổi mã khoá và file `annotations.xml` với ít nhất một bạn cùng nhóm, chạy `make peer`
  để so hai bài, rồi thảo luận (mục "Vòng lặp" bên dưới).

`make team` không có `MEMBERS=` sẽ in chế độ hiện tại (`Chế độ: cá nhân` hoặc `Chế độ: nhóm (An, Bình)`). Không có
file `team.json` = cá nhân; file này nằm ở gốc thư mục `mini-task/`, không nằm trong `submission/`, nên header của `qc_report.md`
vẫn cần bạn tự ghi tên các thành viên.

## Chuẩn bị (trước phút 0)

1. Trên trang repo mẫu, chọn **Use this template → Create a new repository** để tạo repo bài làm của bạn, rồi clone
   repo đó về một thư mục **không có dấu tiếng Việt và khoảng trắng** trong đường dẫn.
2. Mở terminal trong thư mục `mini-task/` của repo vừa clone (`cd mini-task`), chạy `make help`. Bài này chỉ dùng
   thư mục `mini-task/`; thư mục `guideline-challenge/` là bài khác, để nguyên. Không có `make` (thường gặp trên Windows) thì dùng
   lệnh `python lab9.py …` ở cột phải bảng dưới — hai cách cho cùng kết quả. Máy báo không có `python` thì gõ
   `python3` (macOS/Linux) hoặc `py` (Windows) thay cho `python`.
3. Bật CVAT bạn **đã cài từ Day 2** — không cài lại: mở Docker Desktop, vào thư mục CVAT (`cvat-day2`, hoặc `cvat`
   nếu bạn đã cài bản mới ở Day 8), chạy `docker compose start`. Quay về thư mục `mini-task/` rồi chạy `make cvat-status`.
   Đăng nhập bằng tài khoản CVAT của bạn. Chi tiết: [GUIDE mục 1](GUIDE.md); cách tạo task: [GUIDE mục 2](GUIDE.md).
4. Làm nhóm: chạy `make team MEMBERS="…"` (xem mục trên).

## Lệnh dùng trong buổi

Tên task trong lệnh: `lane`, `drivable`, `traffic_sign`, `traffic_light`. Tool chỉ cần Python 3 có sẵn, không cài
thêm gì.

| Việc | Có `make` | Không có `make` |
|---|---|---|
| Kiểm CVAT đang chạy | `make cvat-status` | `python lab9.py cvat` |
| Khoá một export | `make lock TASK=lane FILE=<file export>.zip [RELOCK=1]` | `python lab9.py lock lane <file export>.zip [--relock]` |
| Xem/đặt chế độ nhóm | `make team [MEMBERS="An, Bình"]` | `python lab9.py team [--members "An, Bình"]` |
| So bài với bạn cùng nhóm (nhóm) | `make peer TASK=lane FILE=<annotations.xml của bạn cùng nhóm> CODE=<mã khoá của họ> NAME=<tên họ>` | `python lab9.py peer lane --file … --code … --name …` |
| Mở reference (sau khi đã khoá) | `make reference TASK=lane [FILE=<zip reference ngoài>]` | `python lab9.py reference lane [--file …]` |
| So với reference | `make compare TASK=lane` | `python lab9.py compare lane` |
| Xem tiến độ và bước tiếp theo | `make status` | `python lab9.py status` |
| Kiểm đủ file nộp | `make check` | `python lab9.py check` |

## Trong thư mục

| Đường dẫn | Là gì |
|---|---|
| `cards/01-lane.md` … `04-traffic-light.md` | Một card cho mỗi mini-task: nhịp phút, ảnh core, rule, self-QC, việc sau khi so |
| `GUIDE.md` | Chọn CVAT, thao tác CVAT: tạo task, vẽ, Track, Attribute Annotation Mode, export |
| `RUBRIC.md` | Người chấm nhìn gì khi đọc bài của bạn |
| `data/<task>/schema.json` | Label để dán vào CVAT (tab **Raw**) |
| `data/<task>/core/` | Ảnh bắt buộc. `stretch/` là phần làm thêm, không nộp |
| `examples/lane-*.png` | Ảnh minh hoạ worked example của card 1 (lane) |
| `refs/<task>.zip` | Reference của từng task, đã có sẵn trong repo — xem mục "Honour rule" bên dưới |
| `submission/` | Mọi thứ bạn nộp. Template đã có sẵn, còn chữ `TODO` là chưa xong |
| `gt/` | Trống lúc đầu. `make reference` giải nén reference vào đây; git bỏ qua thư mục này (`.gitignore`) |

## Vòng lặp của mỗi mini-task (4 lần, giống nhau)

`make lock` của task tiếp theo bị từ chối cho tới khi task trước đã đủ: lock còn nguyên, `reference.txt`,
`compare.md` và ít nhất 2 dòng trong `comparison_log.csv`. Chạy `make status` để xem đúng một bước tiếp theo.

1. **Gắn nhãn** ảnh core theo card. Không nhìn bài bạn khác, không mở `refs/` hay `gt/`.
2. **Self-QC** theo checklist trong card, sửa trước khi export.
3. **Export** từ CVAT (định dạng ghi trong card) → `make lock TASK=… FILE=…`. Lệnh in ra **mã khoá** dạng
   `XXXX-XXXX`. Sau khi khoá, file export không đổi nữa. Sửa bài sau khi khoá thì phải chạy lại với `RELOCK=1`.
4. **Chỉ làm nhóm** — đổi mã khoá + file `submission/<task>/annotations.xml` đã khoá với ít nhất một bạn cùng nhóm,
   rồi mỗi người chạy `make peer TASK=… FILE=<file của bạn kia> CODE=<mã của họ> NAME=<tên họ>` với bài **của
   mình** để so hai bài. Thảo luận chỗ lệch tối đa 5 phút — **trước khi mở reference**. Bạn cùng nhóm chưa khoá kịp
   trong 3 phút: đi tiếp, để dành `make peer` cho phút 205–225.
5. `make reference TASK=…` (cài `refs/<task>.zip`, chỉ chạy được sau khi đã khoá) → `make compare TASK=…`. Tool
   viết `submission/<task>/compare.md` và `compare.html` (mở bằng trình duyệt để xem overlay).
6. **Tự quyết định ai đúng** với từng khác biệt. Tool chỉ gợi ý chỗ khác, không phải đáp án. Ghi vào
   `submission/comparison_log.csv` và, nếu là ca mơ hồ, thêm một rule vào `submission/decision_log.csv`.
7. Trả lời mục của task đó trong `submission/scale_100k.md`: nếu lỗi này lặp lại trên 100 000 frame thì model học
   sai gì. Trả lời câu debrief trong card (tự nghĩ nếu cá nhân, bàn nhanh nếu nhóm).
8. **Commit và push `submission/` sau mỗi task** để có bản sao lưu và dấu tiến độ. Sau đó mới sang task kế tiếp.

## Honour rule: đừng mở trước khi khoá

Reference của cả 4 task đã nằm sẵn trong repo (`refs/<task>.zip`) ngay từ đầu — không phải chờ ai phát GT giữa buổi.
Không có mã hoá nào ngăn bạn mở file này sớm; đây là luật danh dự:

- `make reference` **từ chối chạy** nếu task chưa khoá, và từ chối nếu file `annotations.xml` đã khoá bị sửa sau
  khi khoá.
- Khi mở thành công, tool ghi lại thời điểm mở vào `submission/<task>/reference.txt` (mở lại thì thêm
  `reopened_at`).
- `make check` cảnh báo nếu bạn khoá lại **sau khi** đã mở reference — mở lại vẫn được, nhưng phải ghi lý do vào
  `decision_log.csv`.

**Tool ghi lại gì:**

- CVAT owner, task/job, lúc tạo task và lúc export;
- nguồn shape (`manual`, `file` hoặc nguồn khác);
- shape trùng từng đỉnh với reference hoặc bài peer;
- tóm tắt các tín hiệu đó trong `make check`.

Đây là tín hiệu để Lab Coach hỏi bạn về quy trình, không phải kết luận hay hình phạt tự động.

Không tự mở `refs/` hay `gt/` bằng tay trước khi khoá, và không mở file khoá của người khác ngoài luồng
`make peer`.

## Lịch (240 phút, cá nhân và nhóm giống nhau trừ chỗ đánh dấu)

| Phút | Việc |
|---|---|
| 0–15 | Clone repo bài làm, `make help`, bật CVAT và `make cvat-status`, đăng nhập CVAT; nhóm: `make team MEMBERS=…` |
| 15–70 | [Card 1 — Lane](cards/01-lane.md) (15–20 tạo task · 20–27 worked example: mở `examples/lane-*.png`, đọc 4 quyết định trong card, tự vẽ lại ảnh bb890202 · 27–53 5 ảnh còn lại + self-QC · 53–55 export + khoá · 55–60 nhóm: `make peer` / cá nhân: ghi log · 60–67 reference + compare + log · 67–70 câu hỏi debrief) |
| 70–110 | [Card 2 — Drivable](cards/02-drivable.md) (cùng nhịp) |
| 110–120 | Nghỉ |
| 120–160 | [Card 3 — Traffic sign](cards/03-traffic-sign.md) |
| 160–205 | [Card 4 — Traffic light](cards/04-traffic-light.md) |
| 205–225 | `submission/qc_report.md`: nhóm = review batch đã khoá của một bạn cùng nhóm (file `peer-*.html`/`.txt` + `annotations.xml` của họ); cá nhân = **cold QC** bài đầu tiên của chính mình (lane), sau khi vẽ ≥ 2 giờ, coi như bài của người khác |
| 225–235 | Ratify decision log: nhóm = cùng nhau; cá nhân = một mình, sau khi đã xem cả 4 reference. `status`: `ratified` (giữ, có bằng chứng) hoặc `escalated` (rule chưa đủ để phân xử, ghi rõ câu hỏi cụ thể) |
| 235–240 | `make check`, commit và push `submission/` lên repo bài làm của bạn (mục "Nộp gì") |

## Tự time-box

Chậm hơn lịch 5 phút ở một task: bỏ phần stretch, khoá bài đang có, chạy `make reference` + `make compare`, ghi 2
dòng `comparison_log.csv` rồi làm tiếp task sau (`make status` chỉ đúng bước còn thiếu). Phần so và log chỉ mất vài
phút nên không cắt. Lab Coach đi vòng theo mốc của lịch; được nhắc là đang chậm thì làm đúng như vậy.

## Khi bị kẹt

1. Tra [GUIDE mục 5](GUIDE.md): bảng thông báo lỗi và cách xử lý.
2. Vẫn kẹt sau 3 phút: giơ tay gọi Lab Coach (hoặc hỏi bạn cùng nhóm nếu nhanh hơn). Lab Coach gỡ kẹt về CVAT,
   Docker, lệnh `make`/Python và git. Trong lúc chờ, vẽ tiếp ảnh khác, đừng ngồi đợi.
3. Câu hỏi kiểu "vẽ thế này đúng chưa": Lab Coach chỉ bạn tới đoạn rule trong card hoặc handbook, nhưng **không xem
   hộ bài trước khi bạn khoá** — lần thử đầu phải là của bạn. Khi gọi, nói sẵn: ảnh nào, đoạn card nào, bạn đang
   phân vân giữa hai cách hiểu nào. Ca mơ hồ thật thì ghi vào `decision_log.csv` rồi vẽ tiếp.

Đừng tự tìm cách lách qua bước khoá.

## Hai log

**`comparison_log.csv`** — một dòng cho một khác biệt bạn đã xem xét, ≥ 2 dòng mỗi task.

| Cột | Giá trị |
|---|---|
| `task` | `lane` / `drivable` / `traffic_sign` / `traffic_light` |
| `sample` | tên ảnh hoặc số frame |
| `object` | object nào (ví dụ "vạch đứt bên trái", "track 2") |
| `difference` | khác ở đâu, bằng lời của bạn |
| `error_type` | `geometry`, `missing`, `class`, `attribute`, `temporal`, `guideline_gap` |
| `who_is_right` | `me`, `reference`, `guideline_gap` (rule chưa đủ để phân xử) |
| `action` | `keep`, `rework`, `add_rule`, `escalate` |
| `note` | bằng chứng: bạn nhìn thấy gì trong ảnh |

**`decision_log.csv`** — một dòng cho một rule, ≥ 1 mỗi task và ≥ 5 tổng. `status` là `proposed` khi bạn viết,
`ratified` khi chốt ở phút 225–235, `escalated` khi chưa chốt được. `evidence` phải chỉ ra ảnh/frame cụ thể.

Mở hai file này bằng editor văn bản hoặc Excel/Sheets, **giữ nguyên dòng header**, lưu lại dạng CSV.

## Nộp gì

`make check` liệt kê từng mục ✓ / ✗. Đó là kiểm tra đủ file, không phải điểm.

- `submission/<task>/annotations.xml`, `lock.txt`, `reference.txt`, `compare.md` cho cả 4 task
- Nhóm: `submission/<task>/peer-*.txt` cho ít nhất một task — `make check` báo lỗi nếu thiếu
- `submission/comparison_log.csv`, `submission/decision_log.csv`
- `submission/sign_tree.md`, `light_log.md`, `qc_report.md`, `scale_100k.md` — không còn chữ `TODO`

Bài nộp là repo bài làm của bạn (tạo từ template ở bước Chuẩn bị). Cuối buổi, trong thư mục `mini-task/`:

```bash
git add submission team.json
git commit -m "Day 9 lab submission"
git push
```

Làm cá nhân thì không có `team.json` — bỏ tên file đó khỏi lệnh `git add`. Push giữa buổi sau mỗi task cũng được,
bản cuối cùng trên GitHub là bản nộp. Làm nhóm: **mỗi người push repo của mình** (mỗi người có bài lock/compare
riêng) và ghi tên các thành viên nhóm ở đầu `qc_report.md`. Repo để public hay private theo quy định nộp bài của
lớp; dù thế nào, giữ nguyên `ATTRIBUTION.txt` trong repo.

## Luật của buổi

- Không mở `refs/`, `gt/` hay bài khoá của người khác trước khi đến lượt (xem "Honour rule" ở trên).
- Reference không phải đáp án tuyệt đối: lane là bản người thiết kế lab vẽ, các task khác là GT của dataset gốc,
  có giới hạn riêng (card mỗi task ghi rõ). Khác reference mà bạn có bằng chứng → `who_is_right = me`, được tính
  là làm đúng.
- Ảnh là dữ liệu dataset công khai, chỉ dùng cho học tập phi thương mại (xem `ATTRIBUTION.txt`). Không xoá
  `ATTRIBUTION.txt` khỏi repo, không dùng ảnh hay nhãn vào việc thương mại.
