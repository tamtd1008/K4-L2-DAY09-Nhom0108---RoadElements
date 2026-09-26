# Day 9 Lab — Road Elements

Repo mẫu này chứa **hai bài lab Day 9 độc lập**. Đầu buổi Lab Coach báo lớp làm bài nào; bạn chỉ làm bài đó và để
nguyên thư mục bài kia.

| Thư mục | Bài | Tạo repo | Đọc tiếp |
|---|---|---|---|
| `mini-task/` | Gắn nhãn 4 mini-task (lane, drivable area, traffic sign, traffic light) trên CVAT, khoá bài, tự đối chiếu reference và ghi log | Mỗi người một repo | [mini-task/README.md](mini-task/README.md) |
| `guideline-challenge/` | Guideline Design Challenge: nhóm thiết kế guideline + task CVAT, freeze gold, nhóm peer label blind rồi chấm | Một repo cho cả nhóm | [guideline-challenge/README.md](guideline-challenge/README.md) |

## Bắt đầu

1. Tạo repo bài làm bằng **Use this template → Create a new repository** theo cột "Tạo repo" của bài được giao, rồi
   clone về một thư mục **không có dấu tiếng Việt và khoảng trắng** trong đường dẫn.
2. Vào thư mục của bài rồi chạy `make help`:

   ```bash
   cd mini-task            # hoặc: cd guideline-challenge
   make help
   ```

   Không có `make` (thường gặp trên Windows) thì chạy `python lab9.py --help` (máy chỉ có `python3` hoặc `py`: gõ
   `python3 lab9.py --help` / `py lab9.py --help`). Mọi lệnh `make …` và `python lab9.py …` của bài đều chạy
   **trong thư mục bài**, không chạy ở gốc repo.
3. Làm tiếp theo README của bài. Mọi file bạn tạo và nộp đều nằm trong thư mục bài đó.

Hai bài không dùng chung file nào. Nguồn và giấy phép dữ liệu ảnh: [ATTRIBUTION.txt](ATTRIBUTION.txt) — giữ nguyên
file này ở gốc repo và trong từng thư mục bài.
