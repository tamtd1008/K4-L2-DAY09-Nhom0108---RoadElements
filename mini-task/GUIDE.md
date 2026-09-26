# GUIDE — thao tác CVAT cho Day 9

Tên nút và phím tắt theo CVAT v2.74.1 — bản bạn cài ở Day 2 (kiểm bằng `make cvat-status`, mục 1.1). Card của
từng task nói **vẽ cái gì**; file này nói **bấm ở đâu**.

## 1. Trước khi vẽ

### 1.1 Bật CVAT đã cài

Lab dùng lại CVAT local bạn đã cài ở Day 2 (thư mục `cvat-day2`, bản v2.74.1). **Không cài CVAT mới.** Nếu ở Day 8
bạn đã cài bản v2.76.0 trong thư mục `cvat` thì dùng bản đó cũng được.

1. Mở Docker Desktop, chờ Engine chạy xong.
2. Trong terminal, vào thư mục CVAT của bạn và bật lại:

   ```bash
   cd <đường dẫn tới>/cvat-day2
   docker compose start
   ```

3. Quay về thư mục `mini-task/` của repo lab, chạy `make cvat-status` (không có `make`: `python lab9.py cvat`). Lệnh in
   `✓ CVAT <phiên bản> tại http://localhost:8080` là xong.
4. Mở `http://localhost:8080`, đăng nhập bằng tài khoản CVAT bạn đã tạo từ Day 2. Quên mật khẩu: trong thư mục CVAT
   chạy `docker exec -it cvat_server bash -ic 'python3 ~/manage.py createsuperuser'` để tạo tài khoản mới.

Xong buổi, tắt bằng `docker compose stop` trong thư mục CVAT (giống Day 2). Tài khoản và annotation vẫn còn cho lần
sau. Không chạy `docker compose down -v` — tuỳ chọn `-v` có thể xoá task và nhãn đã lưu.

### 1.2 Làm việc trong CVAT

- Dùng Chrome hoặc Edge, đăng nhập tài khoản CVAT của bạn.
- Mỗi mini-task là **một task CVAT riêng** do bạn tạo. Bạn là chủ task nên tự export được.
- Lưu thường xuyên: **Ctrl+S** (hoặc nút **Save** trên thanh trên cùng). Export chỉ lấy bản đã lưu.

## 2. Tạo task

1. Trang **Tasks** → nút **+** → **Create a new task**.
2. **Name:** theo card, ví dụ `lane-<tên bạn>`.
3. **Labels:** bấm tab **Raw**, xoá nội dung có sẵn, dán **toàn bộ** file `data/<task>/schema.json`, bấm **Save**.
   Chuyển sang tab **Constructor** để kiểm tra: lane và drivable có 2 label (label chính + `image_context`), sign và
   light có 1 label. CVAT tạo task thành công **không** có nghĩa label đúng — kiểm ở bước này.
4. **Select files** → **My computer** → chọn **toàn bộ** ảnh trong `data/<task>/core/`. Không chọn ảnh `stretch/`.
5. Traffic light: mở **Advanced configuration**, giữ **Sorting method** là mặc định (lexicographical) để frame theo
   đúng thứ tự tên file 0 → 29.
6. **Submit & Open**. Trong trang task, bấm vào dòng **Job #…** để mở màn hình gắn nhãn.

Dán nhầm schema hoặc upload thiếu ảnh: xoá task đó và tạo lại. Nhanh hơn sửa.

## 3. Vẽ

### 3.1 Công cụ và attribute

Thanh công cụ bên trái có **Draw new polyline**, **Draw new polygon**, **Draw new rectangle** và **Setup tag**
(rê chuột để thấy tên). Bấm công cụ → chọn **Label** → bấm **Shape** (lane, drivable, sign) hoặc **Track** (chỉ light).

| Việc | Cách làm |
|---|---|
| Vẽ polyline / polygon | Click từng điểm. Xong bấm **N** hoặc nút **Done** trên thanh trên cùng. Polygon cần ≥ 3 điểm |
| Vẽ rectangle | Click góc trên trái rồi góc dưới phải |
| Vẽ tiếp object cùng loại | **N** (lặp lại công cụ vừa dùng) |
| Sửa hình | Chọn object, kéo điểm hoặc cạnh |
| Xoá object | Chọn object → **Del** |
| Hoàn tác | **Ctrl+Z** |
| Tag cả ảnh | **Setup tag** → label `image_context` → **Tag** |
| Gán attribute | Sidebar phải, tab **Objects** → mở object → chọn giá trị |
| Thấy vạch/curb dưới polygon | Sidebar phải, mục **Appearance** → giảm **Opacity** |
| Sang ảnh/frame kế / trước | **F** / **D**. Nhảy nhiều frame: **V** / **C** |

Attribute nào còn `__undefined__` là chưa gán. `make lock` vẫn nhận, nhưng đó tính là lỗi attribute khi chấm.

### 3.2 Attribute Annotation Mode (sign, light)

Khi đã vẽ hết box, gán attribute nhanh hơn ở chế độ này:

1. Góc trên phải, đổi **Standard** → **Attribute annotation**.
2. Màn hình phóng to một object và hỏi một attribute. **↑ / ↓** đổi attribute, **Tab / Shift+Tab** đổi object,
   **F / D** đổi frame. Chọn giá trị bằng phím số hiện cạnh giá trị, hoặc chọn trong danh sách (`sign_class` dài).
3. Xong, đổi lại **Standard** để vẽ hoặc sửa box.

### 3.3 Track cho traffic light

Track = một đầu đèn vật lý qua cả chuỗi frame. Đây là điểm khác lớn nhất so với 3 task trước.

1. Ở frame đầu tiên đèn xuất hiện, **Draw new rectangle** → label `traffic_light` → **Track**, vẽ box.
2. Gán `pictogram` và `relevance` một lần (cố định cho cả track), gán `state` ở frame này.
3. Bấm **F** đi qua các frame. CVAT **nội suy** box giữa hai keyframe. Khi box lệch khỏi đèn, kéo box đúng chỗ — CVAT
   tạo keyframe ở frame đó. **K** bật/tắt keyframe thủ công.
4. Đến frame đèn **đổi màu**, đổi `state`. CVAT tự tạo keyframe ở frame đó, giữ vị trí box đang nội suy, và giữ
   `state` mới cho các frame sau cho tới khi bạn đổi tiếp.
5. **Kết thúc track:** ở frame đầu tiên đèn ra khỏi khung hoặc bị che hẳn, chọn track → **O** (outside). Box biến mất
   từ frame đó. Nếu không làm, export sẽ có box ở mọi frame tới frame 29 dù đèn đã mất. Đèn quay lại → ở frame đó
   bấm **O** lần nữa.
6. Tua lại bằng **D** và **F**, kiểm box bám đèn và `state` từng frame.

Một đầu đèn = một track. Lỡ vẽ track thứ hai cho cùng đèn: xoá track thừa, kéo dài track gốc.

## 4. Export và khoá

1. Lưu (**Ctrl+S**).
2. Trong màn hình job: **Menu** (góc trên trái) → **Export job dataset**. Hoặc ở trang task: **Actions** →
   **Export task dataset**.
3. Chọn định dạng theo card: **CVAT for images 1.1** (lane, drivable, sign) hoặc **CVAT for video 1.1** (light).
   **Save images: tắt.**
4. CVAT báo khi file sẵn sàng. Tải từ thông báo hoặc trang **Requests** trên thanh trên cùng.
5. Trong terminal ở thư mục `mini-task/`: `make lock TASK=<task> FILE=<đường dẫn file zip vừa tải>`.
   Lệnh in ra **mã khoá** (dạng chữ và số ngắn). Làm nhóm thì ghi lại mã này, sẽ cần khi đổi bài với bạn cùng nhóm
   (xem README mục "Vòng lặp của mỗi mini-task").

`make lock` chép `annotations.xml` vào `submission/<task>/` và ghi `lock.txt`. Không sửa tay hai file này.

## 5. Khi lệnh báo lỗi

| Thông báo | Nghĩa | Làm gì |
|---|---|---|
| `CVAT chưa chạy ở http://localhost:8080` | Docker Desktop chưa mở, hoặc CVAT chưa bật | Mở Docker Desktop, trong thư mục CVAT (`cvat-day2` hoặc `cvat`) chạy `docker compose start` (báo không có container thì `docker compose up -d`), đợi CVAT khởi động xong, quay về thư mục `mini-task/` của repo lab rồi `make cvat-status` lại. Vẫn lỗi: trong thư mục CVAT chạy `docker compose ps` xem dịch vụ nào chưa chạy |
| `make: command not found` / `'make' is not recognized` | Máy không có `make` (thường là Windows) | Dùng lệnh `python lab9.py …` ở cột phải bảng lệnh trong README |
| `python: command not found` | Máy chỉ có `python3` hoặc `py` | Gõ `python3 lab9.py …` (macOS/Linux) hoặc `py lab9.py …` (Windows) |
| `Export dùng label ngoài schema` | Label trong task khác `schema.json` | Sửa label trong CVAT (hoặc tạo lại task) rồi export lại |
| `Không có shape nào trên mẫu core` | Export nhầm task, hoặc export trước khi lưu | Ctrl+S, kiểm tên task, export lại |
| `traffic_light phải export bằng CVAT for video 1.1` | Chọn nhầm định dạng **CVAT for images** | Export lại đúng định dạng (mục 4 bước 3) rồi khoá. Chưa khoá nên không tính khoá lại |
| `! … track đèn chỉ có 1 frame` | Thường là đèn vẽ bằng **Shape** (track thật chỉ hiện 1 frame cũng bị báo) | Mở task kiểm tra; nếu đúng là Shape thì vẽ lại bằng **Track** (mục 3.3), export, rồi khoá lại với `RELOCK=1` |
| `… đã khoá với file khác` | Bạn khoá lại với export khác | Ghi lý do vào `decision_log.csv`, rồi thêm `RELOCK=1` |
| `Chưa xong vòng … — chạy make status` | Task trước chưa đủ lock, reference, compare hoặc 2 dòng log | Chạy `make status`, làm đúng bước được chỉ ra rồi khoá task tiếp theo |
| `Chưa khoá … trước khi mở reference` | Chưa `make lock` task này | Khoá trước, `make reference` sau |
| `file đã đổi sau khi khoá` | `submission/<task>/annotations.xml` bị sửa | Chạy lại `make lock` với đúng file export đã khoá |
| `Chưa cài reference …` | Chưa chạy `make reference` cho task này | `make reference TASK=<task>` (task phải khoá trước) |
| `! Core … không có trong export` | Thiếu ảnh core trong task | Kiểm bước 4 mục 2 (đã chọn đủ ảnh trong `core/` chưa), tạo lại task nếu thiếu |
| `File của … và bài của bạn export từ cùng một task CVAT` | Hai file có cùng owner và lúc tạo task | Mỗi người tạo task CVAT riêng, tự vẽ và export lại |
| `! … source khác manual` | Có shape import từ file mà chưa sửa trong CVAT | Lab yêu cầu vẽ tay; chỉ khi import lại export cũ của chính mình sau khi tạo lại task mới ghi lý do vào `decision_log.csv` |
| `! … shape trùng từng đỉnh` | Hình học trùng với reference hoặc peer tới từng đỉnh | Kiểm tra hai người đã vẽ độc lập; nếu từng import reference/export cũ, ghi rõ trong `decision_log.csv` |

Kẹt quá 3 phút ở một thao tác: gọi Lab Coach (hoặc hỏi bạn cùng nhóm), đừng tự tìm cách lách qua bước khoá. Xem
thêm mục [Khi bị kẹt](README.md#khi-bị-kẹt) trong `README.md`.
