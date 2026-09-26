# Annotation guideline — Label lane

**Version:** v1

<!--
v0 = chưa có bản nháp. Đổi dòng Version ở trên thành v1 khi xong bản nháp đầu, v2 sau calibration, v3 sau blind
handoff; mỗi lần tăng version ghi một dòng vào 08_revision_log.md. `make freeze` đòi v2 trở lên.

File này là thứ nhóm peer nhận nguyên văn trong blind pack và là Guide dán vào CVAT. Peer KHÔNG nhận
edge_case_cards.md, gold_decisions.csv hay sample_pack.csv. Rule nào peer cần biết phải nằm ở đây.
No hidden rules: rule chỉ giải thích bằng miệng thì coi như không tồn tại.
Ví dụ trong guideline chỉ dùng ảnh split example hoặc calibration, không dùng ảnh blind.
-->

## 1. Objective + scope

Mục đích (Objective): Gán nhãn các vạch kẻ đường, ranh giới làn đường (lane) phục vụ mô hình bài toán tự lái (Autonomous Driving / Path Planning).

In scope (Trong phạm vi):

Tất cả các vạch kẻ đường phân chia làn cùng chiều, ngược chiều, vạch giới hạn lề đường (road curb).

Các vạch kẻ hiển thị rõ ràng hoặc bị che khuất nhẹ nhưng vẫn nhìn rõ quỹ đạo tiếp diễn.

Out of scope (Ngoài phạm vi):

Vạch gờ giảm tốc quá ngắn, vạch kẻ ô bàn cờ (grid lines) ở ngã tư không phải đường đi chính.

Vạch kẻ sơn trong khu vực bãi đỗ xe nội bộ, sân nhà dân.

## 2. Annotation unit

Đơn vị gán nhãn: Ảnh tĩnh (Single Frame) / Polyline Instance.

Phân định Instance: Mỗi vạch kẻ làn đường độc lập được coi là một polyline instance. Nếu vạch kẻ bị đứt đoạn (đường nét đứt dashed), vẫn vẽ nối liền thành 1 polyline instance kéo dài dọc theo chiều đi của làn đường trừ khi ranh giới đường bị ngắt quãng hoàn toàn bởi ngã tư lớn.

## 3. Geometry rule

Dạng hình học: Polyline.Độ chính xác (Tightness): Polyline phải bám sát vào trung tâm/đường trục chính của vạch sơn kẻ đường.Điểm bắt đầu & kết thúc (Endpoints):Point đầu tiên: Nơi vạch bắt đầu xuất hiện gần xe nhất (đbottom ảnh) hoặc từ tiêu điểm biến mất phía xa.Point cuối cùng: Nơi vạch kẻ biến mất ở chân trời / bị che khuất hoàn toàn / ra khỏi mép ảnh.Mật độ điểm (Point density): Đường thẳng chỉ cần 2–3 điểm gốc; các đoạn cua cong cần bổ sung các đỉnh (vertex) mịn để ôm sát độ cong của làn.Mức dung sai (Tolerance): Sai số khoảng cách chấp nhận được $\le 3\text{ px}$.

## 4. Taxonomy
 — class hierarchy; cái gì là class, cái gì là attribute; allowed values; default và khi nào dùng `unknown`.
Bảng đầy đủ ở `03_ontology_and_cvat_setup.md` — hai nơi phải khớp nhau.

| Class | Attribute | Allowed Values | Default | Notes / Description |
|---|---|---|---|---|
| lane | laneDirection | vertical, parallel | vertical | không sử dụng unknown. Bắt buộc phải xác định dựa trên hướng di chuyển của xe (xe chạy dọc tầm nhìn là vertical, cắt ngang là parallel). |
| lane | laneTypes | single white, double white, single yellow, double yellow, road curb | single white | Khi vạch kẻ đường bị mờ nát nặng, bị bong tróc quá 50%, bị bùn đất/tuyết che lấp hoặc ánh sáng quá xấu (đêm tối, chói đèn) dẫn đến không thể phân biệt được đó là vạch trắng, vạch vàng, vạch đơn hay vạch đôi. |
| lane | laneStyle | solid, dashed | solid | Khi vạch kẻ bị mờ ngắt quãng bất thường, không thể khẳng định chắc chắn đó là vạch nét liền (solid) hay vạch nét đứt (dashed). |

## 5. Inclusion / exclusion

Bắt buộc gán nhãn (Inclusion):

Các làn đường chính di chuyển của xe ego và các làn kế cận.

Lề đường (road curb) có ranh giới rõ ràng điều hướng xe.

Bỏ qua / Ignore (Exclusion):

Vạch sơn đã cũ mờ bị xóa gần hết (> 80% độ mờ).

Vạch kẻ tạm thời của công trình đã bị phân luồng bỏ.

## 6. Visibility / occlusion

Bị che một phần (Occlusion): Nếu vạch kẻ đường bị xe khác đè lên một đoạn ngắn ($\le 2\text{ m}$), tiếp tục nối polyline amodal qua dưới gầm xe dựa trên xu hướng chuyển động.
Bị cắt mép ảnh (Truncation): Kéo dài polyline chạm sát viền mép ảnh (image border).Nhỏ / Xa (Distance): Bỏ qua các vạch kẻ quá xa ở cuối chân trời khi chiều dài vạch $< 10\text{ px}$.
Phản chiếu / Lóa sáng: Nếu do mặt đường ướt/nắng lóa không phân biệt được vạch kẻ thực, chỉ vẽ đoạn nhìn thấy rõ.

## 7. Ambiguity / escalation

Quy tắc xử lý bằng chứng không đủ:LABEL: Nếu nhận diện rõ $> 70\%$ đường kẻ.IGNORE / UNKNOWN: Nếu thuộc tính đường nét/loại làn bị mờ không nhìn rõ màu sơn.ESCALATE: Nếu không xác định được đó là đường lề hay làn đường di chuyển chính.Thể hiện trong CVAT:Tạo Tag escalated ở cấp độ Frame/Job.Trong trường thuộc tính note của object, ghi rõ lý do nghi vấn (ví dụ: "Mờ nhòe do ánh đèn đêm, cần Lead xác nhận").

## 8. Temporal rule

Không áp dụng — task ảnh tĩnh.

## 9. Examples

— positive, negative và edge case, mỗi ví dụ có sample_id (split example/calibration) và expected output.

| sample_id | Thấy gì | Expected output | Rule áp dụng |
|---|---|---|---|
| b75f355e-b3f098b9.jpg | Vạch kẻ đường chạy thẳng về phía trước theo hướng góc nhìn của camera | Polyline với laneDirection = vertical | Làn đường hướng dọc theo chiều di chuyển của xe gắn nhãn vertical.     |
| bb890202-d9d48310.jpg | Ranh giới bê tông/lề đường sát biên bên phải ảnh | Polyline với laneTypes = road curb | Biên lề đường hoặc dải phân cách cứng gán nhãn road curb. |
| c1589305-200e315b.jpg | Vạch kẻ phân chia làn đường dạng nét đứt màu trắng | Polyline với laneStyle = dashed, laneTypes = single white | Phân định chính xác loại vạch đứt đoạn và kiểu vạch đơn. |
| c0f739d8-6ff93525.jpg | Vạch kẻ bị xe khác che khuất một đoạn ngắn trên mặt đường | Polyline nối liền (Amodal) qua vùng bị che | Vẽ ước lượng tiếp diễn qua khoảng che ngắn (dưới 2m) nếu rõ xu hướng làn. |

## 10. Common mistakes

Gán sai hướng làn (laneDirection): Nhầm lẫn giữa vertical (hướng dọc theo tầm mắt/hướng di chuyển) thành parallel.   Cách tránh: Nhớ quy tắc: Tất cả các làn xe chạy thẳng từ đáy ảnh lên gần tâm là vertical.   Bỏ sót làn lề đường sát mép ảnh (missing): Thường bỏ qua các vạch lề sát viền phải/trái của camera.   Cách tránh: Rà soát kỹ khu vực sát mép ảnh trước khi Submit.Vẽ thừa đường suy đoán không có thật (guideline_gap): Tự ý nối các đoạn không có vạch sơn trên mặt đường.   Cách tránh: Chỉ vẽ amodal khi vạch bị xe đè ngắn; không tự suy diễn làn đường ở ngã tư lớn.
