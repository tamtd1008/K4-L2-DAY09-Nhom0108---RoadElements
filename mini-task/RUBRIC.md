# RUBRIC — người chấm đọc bài Day 9 như thế nào

Năm tiêu chí và trọng số lấy từ slide Day 9 của giảng viên. Mô tả từng mức là của người thiết kế lab cho buổi này.
Đây là rubric **phản hồi**, không có điểm sàn đạt/trượt.

Người chấm chấm **bằng chứng** trong `submission/`, không chấm độ lớn IoU hay số khác biệt tool đếm được. Khác
reference mà bạn giải thích được bằng ảnh và rule thì không bị trừ.

| Tiêu chí | Trọng số | Nhìn vào đâu |
|---|---|---|
| Geometry | 20 | `annotations.xml` 4 task, `compare.html` |
| Attribute | 25 | `annotations.xml`, `compare.md`, `light_log.md` |
| Ambiguity | 20 | `decision_log.csv`, `sign_tree.md`, `light_log.md` |
| QC mindset | 20 | `comparison_log.csv`, `qc_report.md` |
| Communication | 15 | `scale_100k.md`, cột `note` / `evidence` |

## Mô tả mức

| Tiêu chí | Chưa vững | Đạt mục tiêu buổi | Vững |
|---|---|---|---|
| **Geometry** | Box ôm cột, polyline zig-zag, polygon lấn vỉa hè; thiếu object gần ego | Bám đúng biên theo card; điểm đầu/cuối lane theo một rule; track đèn có `outside` khi đèn mất | Nhất quán qua mọi ảnh; tự bắt được và sửa lỗi hình học của mình trước khi khoá |
| **Attribute** | Còn `__undefined__`; đoán class khi không đọc được; `state` sai ở frame chuyển | Attribute đúng với thứ nhìn thấy; dùng `unknown` / `needs_review` khi thiếu bằng chứng | Không drift giữa các ảnh cùng loại; `state` đúng tới từng frame chuyển; family đúng cả khi class `unknown` |
| **Ambiguity** | Không ghi ca mơ hồ, hoặc rule chỉ nói "tuỳ trường hợp" | ≥ 1 rule mỗi task, có `evidence` chỉ ảnh/frame cụ thể, áp được cho người khác | Rule tách được ca biên (khi nào áp, khi nào không); ratify hoặc escalate có lý do rõ |
| **QC mindset** | Log chỉ chép lại output của tool; mọi dòng `who_is_right = reference` | Mỗi dòng log có quyết định ai đúng và `action`; peer QC / cold QC có sample plan theo lát dễ lỗi | Phân biệt `geometry` / `attribute` / `temporal` / `guideline_gap` chính xác; severity gắn với hậu quả cho ego |
| **Communication** | Câu trả lời 100k chung chung ("model sẽ sai") | Nói được lỗi nào thành systematic defect và model học sai gì | Nêu được cách phát hiện sớm trên dữ liệu lớn (lát nào cần sample, rule nào cần thêm) |

## Bằng chứng nằm ở đâu trong `submission/`

- **Khoá và so sánh**: `<task>/lock.txt`, `<task>/reference.txt`, `<task>/compare.md` — cho cả 4 task.
- **Peer QC (nhóm)**: `<task>/peer-*.txt` và `.html` do `make peer` ghi tự động, ít nhất một task.
- **Cold QC (cá nhân)**: `qc_report.md` — QC lại task đầu tiên của chính mình sau ≥ 2 giờ, coi như bài người khác.
- **Log**: `comparison_log.csv`, `decision_log.csv` — cột `who_is_right`, `evidence`, `note` là nơi bằng chứng nằm.
- Một dòng `who_is_right = me` kèm `note`/`evidence` cụ thể (chỉ ra ảnh, frame, hoặc vị trí) được tính là **làm
  đúng**, kể cả khi khác reference — reference có giới hạn riêng, không phải đáp án tuyệt đối.

## Những điều không làm giảm đánh giá

- Khác reference ở chỗ reference có giới hạn đã ghi trong card (lane là bản người thiết kế lab vẽ; sign không có
  `readable`; light không có `relevance` và không gán đèn xa) — nếu bạn ghi rõ lý do.
- `who_is_right = guideline_gap` khi rule thật sự không đủ để phân xử.
- Không làm phần stretch.

## Những điều người chấm sẽ hỏi lại

- Khoá lại nhiều lần mà không ghi lý do (`relock_count` trong `lock.txt`, không có dòng tương ứng trong
  `decision_log.csv`).
- Log có dòng nhưng `evidence` / `note` trống.
- Thiếu task nào trong `make check`.
