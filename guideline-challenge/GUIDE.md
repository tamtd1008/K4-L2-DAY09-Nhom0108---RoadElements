# GUIDE — thao tác CVAT cho Day 9

Tên nút và phím tắt theo CVAT v2.74.1 — bản bạn cài ở Day 2 (kiểm bằng `make cvat-status`). `README.md` nói **làm
gì, khi nào**; file này nói **bấm ở đâu**. Không có `make`: dùng lệnh `python lab9.py …` tương ứng trong bảng lệnh
của README.

## 1. Bật CVAT đã cài

Lab dùng lại CVAT local bạn đã cài ở Day 2 (thư mục `cvat-day2`, bản v2.74.1). **Không cài CVAT mới.** Nếu ở Day 8
bạn đã cài bản v2.76.0 trong thư mục `cvat` thì dùng bản đó cũng được.

1. Mở Docker Desktop, chờ Engine chạy xong.
2. Trong terminal, vào thư mục CVAT của bạn và bật lại:

   ```bash
   cd <đường dẫn tới>/cvat-day2
   docker compose start
   ```

3. Quay về thư mục `guideline-challenge/` của repo lab, chạy `make cvat-status`. Lệnh in `✓ CVAT <phiên bản> tại http://localhost:8080` là xong.
4. Mở `http://localhost:8080` bằng Chrome hoặc Edge, đăng nhập tài khoản CVAT bạn đã tạo từ Day 2. Quên mật khẩu:
   trong thư mục CVAT chạy `docker exec -it cvat_server bash -ic 'python3 ~/manage.py createsuperuser'` để tạo tài
   khoản mới.

Xong buổi, tắt bằng `docker compose stop` trong thư mục CVAT. Tài khoản và annotation vẫn còn cho lần sau. Không chạy
`docker compose down -v` — tuỳ chọn `-v` có thể xoá task và nhãn đã lưu.

Mỗi người dùng CVAT trên máy mình. Task là của người tạo nên người đó tự export được. Lưu thường xuyên: **Ctrl+S**
(hoặc nút **Save** trên thanh trên cùng). Export chỉ lấy bản đã lưu.

## 2. Tạo task calibration

### 2.1 Viết `03_cvat_labels.json`

CVAT nhận danh sách label ở định dạng JSON trong tab **Raw**. Viết file này theo ontology table của nhóm — ontology
table là source of truth, JSON chỉ là bản dịch. Ví dụ định dạng (không phải đáp án cho topic nào):

```json
[
  {
    "name": "traffic_light",
    "color": "#F9A825",
    "type": "rectangle",
    "attributes": [
      {
        "name": "state",
        "mutable": true,
        "input_type": "select",
        "default_value": "__undefined__",
        "values": ["__undefined__", "red", "yellow", "green", "off", "unknown"]
      },
      {
        "name": "needs_review",
        "mutable": false,
        "input_type": "checkbox",
        "default_value": "false",
        "values": ["false"]
      }
    ]
  },
  {
    "name": "image_escalate",
    "color": "#8E24AA",
    "type": "tag",
    "attributes": []
  }
]
```

| Trường | Giá trị |
|---|---|
| `name` | tên label, viết giống hệt ontology table |
| `type` | `rectangle`, `polygon`, `polyline`, `points`, `tag` (nhãn cho cả ảnh) hoặc `any` |
| `input_type` | `select` (danh sách thả xuống), `radio`, `checkbox`, `number`, `text` |
| `default_value` | phải nằm trong `values`. Checkbox: `"false"` và `values` là `["false"]` |
| `mutable` | `true` khi giá trị có thể đổi giữa các frame của cùng một track (ví dụ `state` của đèn) |

Default là một quyết định thiết kế: nếu default là `green`, annotator quên gán sẽ tạo ra đèn xanh "im lặng". Muốn
buộc annotator chọn, để `__undefined__` đứng đầu `values` và làm default — giá trị này còn trong export nghĩa là chưa
gán. Kiểm file hợp lệ trước khi dán: `python -m json.tool project/03_cvat_labels.json`.

### 2.2 Tạo task

1. `make pack SPLIT=calibration` gom ảnh calibration vào `build/calibration/`.
2. Trong CVAT: trang **Tasks** → nút **+** → **Create a new task**.
3. **Name:** `<tên nhóm>-calib-<tên bạn>`.
4. **Labels:** bấm tab **Raw**, xoá nội dung có sẵn, dán **toàn bộ** `project/03_cvat_labels.json`, bấm **Save**.
   Chuyển sang tab **Constructor** kiểm tra đủ label và attribute. CVAT tạo task thành công **không** có nghĩa label
   đúng — kiểm ở bước này.
5. **Select files** → **My computer** → chọn **toàn bộ** ảnh trong `build/calibration/`.
6. Mở **Advanced configuration**, giữ **Sorting method** mặc định (lexicographical) để ảnh theo thứ tự tên file.
7. **Submit & Open**. Trong trang task, bấm dòng **Job #…** để mở màn hình gắn nhãn.

Dán nhầm labels hoặc upload thiếu ảnh: xoá task và tạo lại. Nhanh hơn sửa. Đổi ontology sau calibration thì tạo task
mới với JSON mới — task cũ giữ nguyên làm bằng chứng.

### 2.3 Dán guideline vào Guide của task

1. Ở trang task, dưới **Task description** bấm **Edit**.
2. Dán toàn bộ nội dung `project/02_guideline.md` vào ô Markdown, bấm **Submit**.
3. Trong màn hình gắn nhãn, nút **Guide** ở góc trên phải mở lại guideline. CVAT tự mở Guide lần đầu người được giao
   vào job.

CVAT **không lưu phiên bản** của Guide: sửa là mất bản cũ. Bản gốc và dòng `Version` nằm trong
`project/02_guideline.md`; mỗi lần đổi guideline, dán lại vào Guide của task đang dùng. Ảnh kéo thả vào Guide chỉ
nằm trên CVAT của máy bạn, nhóm peer không thấy — ví dụ trong guideline gọi ảnh bằng `sample_id` (ví dụ `BDD03`).

## 3. Vẽ

### 3.1 Công cụ và attribute

Thanh công cụ bên trái có **Draw new rectangle**, **Draw new polygon**, **Draw new polyline**, **Draw new points** và
**Setup tag** (rê chuột để thấy tên). Bấm công cụ → chọn **Label** → bấm **Shape** (một ảnh) hoặc **Track** (một
object qua nhiều frame).

| Việc | Cách làm |
|---|---|
| Vẽ rectangle | Click góc trên trái rồi góc dưới phải |
| Vẽ polygon / polyline | Click từng điểm. Xong bấm **N** hoặc nút **Done** trên thanh trên cùng. Polygon cần ≥ 3 điểm |
| Vẽ tiếp object cùng loại | **N** (lặp lại công cụ vừa dùng) |
| Sửa hình | Chọn object, kéo điểm hoặc cạnh |
| Xoá object | Chọn object → **Del** |
| Hoàn tác | **Ctrl+Z** |
| Tag cả ảnh | **Setup tag** → chọn label kiểu `tag` → **Tag** |
| Gán attribute | Sidebar phải, tab **Objects** → mở object → chọn giá trị. Dropdown bấm chuột không ăn thì bấm vào ô rồi dùng **↓** + **Enter** |
| Thấy biên dưới polygon | Sidebar phải, mục **Appearance** → giảm **Opacity** |
| Sang ảnh kế / trước | **F** / **D**. Nhảy nhiều ảnh: **V** / **C** |

Nhiều object, nhiều attribute: vẽ hết hình trước, rồi đổi **Standard** → **Attribute annotation** ở góc trên phải.
Màn hình phóng to từng object và hỏi từng attribute: **↑ / ↓** đổi attribute, **Tab / Shift+Tab** đổi object,
**F / D** đổi ảnh, phím số chọn giá trị. Xong đổi lại **Standard**.

### 3.2 Track (chỉ khi topic có temporal rule)

Track = một object vật lý qua cả chuỗi frame (ví dụ một đầu đèn trong clip LISA).

1. Ở frame đầu tiên object xuất hiện: công cụ vẽ → label → **Track**, vẽ hình.
2. Gán attribute cố định một lần; attribute `mutable` gán lại ở frame nó đổi.
3. Bấm **F** qua các frame. CVAT **nội suy** hình giữa hai keyframe; khi hình lệch, kéo lại — CVAT tạo keyframe ở
   frame đó. **K** bật/tắt keyframe.
4. **Kết thúc track:** ở frame đầu tiên object ra khỏi khung hoặc bị che hẳn, chọn track → **O** (outside). Không làm
   thì export có hình ở mọi frame tới cuối clip.

Một object = một track. Task có track phải export bằng **CVAT for video 1.1** (mục 4).

### 3.3 LABEL / IGNORE / UNKNOWN / ESCALATE trong CVAT

Quyết định không thấy được trong file export thì không đo, không chấm được. Vài cách thể hiện — chọn cách nào là
quyết định của nhóm, ghi vào ontology table:

| Quyết định | Cách có thể dùng trong CVAT |
|---|---|
| LABEL | vẽ object với label + attribute |
| IGNORE một vùng | label riêng (ví dụ kiểu `rectangle` hoặc `polygon`) cho vùng bỏ qua, hoặc rule "không vẽ" viết rõ trong guideline |
| UNKNOWN một thuộc tính | giá trị `unknown` trong attribute |
| ESCALATE một object | checkbox kiểu `needs_review` trên object |
| ESCALATE cả ảnh | label kiểu `tag` cho ảnh |

`make calib` đếm số object theo label, so giá trị attribute và so tag cả ảnh giữa các annotator — cách thể hiện càng
rõ trong export thì bảng bất đồng càng có ích.

## 4. Export

1. Lưu (**Ctrl+S**).
2. Trong màn hình job: **Menu** (góc trên trái) → **Export job dataset**. Hoặc ở trang task: **Actions** →
   **Export task dataset**.
3. Định dạng **CVAT for images 1.1**; task có track thì **CVAT for video 1.1**. **Save images: tắt.**
4. CVAT báo khi file sẵn sàng. Tải từ thông báo hoặc trang **Requests** trên thanh trên cùng.
5. Đổi tên file zip theo tên bạn (ví dụ `an.zip`) rồi chép vào `project/06_calibration_exports/`. `make calib` lấy
   tên file làm tên annotator.

## 5. Làm peer tester

Bạn nhận `blind-pack.zip` từ nhóm owner. Giải nén, đọc `PEER_README.md` trước.

1. Tạo task mới: **Name** `peer-<tên nhóm owner>`; **Labels** tab **Raw** dán toàn bộ `cvat_labels.json` trong gói;
   **Select files** chọn toàn bộ ảnh trong `images/`; **Submit & Open**.
2. Dán `guideline.md` vào Guide của task (mục 2.3).
3. Label theo guideline trong 15 phút. Không đoán ý owner. Chỗ nào phải hỏi hoặc không hiểu: ghi lại nguyên văn câu
   hỏi và giờ — owner ghi từng câu vào `clarification_log.csv` của họ. Lỗi CVAT kỹ thuật thì gọi Lab Coach, không
   tính là câu hỏi.
4. Export theo mục 4 (không cần chép vào repo của bạn). Đổi tên file thành `<tên nhóm bạn>-blind.zip`.
5. Gửi file export cho owner qua kênh Lab Coach công bố, kèm câu trả lời 5 câu feedback trong `PEER_README.md`.

## 6. Xem export của peer

Geometry decision và những chỗ `peer_evidence` tóm tắt chưa đủ thì cần xem hình peer vẽ.

1. `make pack SPLIT=blind` gom ảnh blind vào `build/blind/`.
2. Tạo task `review-<tên nhóm peer>` với **đúng** `project/03_cvat_labels.json` đã freeze và toàn bộ ảnh trong
   `build/blind/`.
3. Ở trang task: **Actions** → **Upload annotations** → **Import format** chọn **CVAT 1.1** → **Import mode** giữ
   **Replace** → kéo file export của peer (trong `project/07_blind_handoff/peer_output/`) vào ô **Click or drag file
   to this area** → **OK**. Định dạng này nhận cả export for images lẫn for video.
4. Mở job, đối chiếu từng dòng `transfer_score.csv` với hình peer đã vẽ, điền `correct` và `note`.

Upload báo lỗi label: task review phải dùng đúng labels JSON đã gửi cho peer. Upload xong không thấy hình: kiểm lại
đã chọn đủ ảnh blind khi tạo task.

## 7. Khi lệnh báo lỗi

Lệnh luôn in dòng `✗` với lý do và bước sửa. Các lỗi hay gặp:

| Thông báo | Nghĩa | Làm gì |
|---|---|---|
| `CVAT chưa chạy ở http://localhost:8080` | Docker Desktop chưa mở, hoặc CVAT chưa bật | Mở Docker Desktop, trong thư mục CVAT chạy `docker compose start` (báo không có container thì `docker compose up -d`), đợi khởi động xong rồi `make cvat-status` lại. Vẫn lỗi: `docker compose ps` trong thư mục CVAT xem dịch vụ nào chưa chạy |
| `make: command not found` / `'make' is not recognized` | Máy không có `make` (thường là Windows) | Dùng lệnh `python lab9.py …` ở cột phải bảng lệnh trong README |
| `python: command not found` | Máy chỉ có `python3` hoặc `py` | Gõ `python3 lab9.py …` (macOS/Linux) hoặc `py lab9.py …` (Windows) |
| `Chưa có tag gold-freeze trong clone này` | `make freeze` chưa commit/tag được (thường do git chưa có `user.name`/`user.email`), hoặc bạn cùng nhóm đã freeze và push nhưng clone của bạn chưa lấy tag | Chạy đúng lệnh `make freeze` đã in. Bạn cùng nhóm đã freeze: `git pull && git fetch --tags --force` |
| `Clone này đã có tag gold-freeze nhưng thiếu project/FREEZE.txt` | Bạn cùng nhóm đã freeze; mỗi nhóm chỉ **một người** chạy `make freeze` | `git pull`. Vẫn thiếu vì lỡ xoá `FREEZE.txt`: `git restore --source=gold-freeze -- project/FREEZE.txt`. Nhóm thật sự cần freeze lại và chưa nhận export của peer: `make freeze REFREEZE=1` |
| `Khác bản đã commit ở tag gold-freeze` ngay sau khi bạn cùng nhóm refreeze | Clone của bạn còn tag cũ; `git fetch --tags` thường không ghi đè tag đã có | `git pull && git fetch --tags --force`. Vẫn báo khác: bạn đã sửa gold/sample pack sau freeze — hoàn tác bằng `git checkout gold-freeze -- <file>` |
| `Thư mục này không phải git clone` | Lab mở từ file ZIP tải về hoặc thư mục chép ra ngoài clone, nên không có tag `gold-freeze` | Mở lab trong clone repo nhóm (`git clone`), chép `project/` vào đó rồi chạy lại |
| `Export không có <image>, <track> hay <tag> nào` | File export không có annotation nào nên tool không biết ảnh nào có mặt | Export lại bằng **CVAT for images 1.1** (mục 4) |

Kẹt quá 3 phút ở một thao tác kỹ thuật: gọi Lab Coach. Đừng tự tìm cách lách qua bước freeze. Xem thêm mục
[Khi bị kẹt](README.md#khi-bị-kẹt) trong `README.md`.
