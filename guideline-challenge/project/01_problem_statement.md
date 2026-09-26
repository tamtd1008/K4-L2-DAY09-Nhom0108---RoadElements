# Problem statement + downstream contract

Tối đa nửa trang, viết **trước khi mở CVAT**. Đây là bằng chứng của gate G1 (topic lock). Thay mọi placeholder
mới là xong.

## Bài toán
— một câu: road element nào, trong tình huống nào, khó ở đâu. "Label traffic signs" là quá rộng; "hierarchical
sign taxonomy cho biển nhỏ/xa/bị che" là đủ cụ thể.

"Label lane": Lane boundary tại merge/split + vạch mờ/tạm thời

## Downstream contract

1. **Downstream task / model / user là ai?** 
Mô hình / Hệ thống tiêu thụ: Mô hình phát hiện làn đường (Lane Detection / Path Prediction Model) và hệ thống lập kế hoạch quỹ đạo di chuyển (Path Planning) thuộc bài toán xe tự lái (Autonomous Driving System).   
Người sử dụng đầu ra: Đội ngũ kĩ sư AI/Data Science huấn luyện mô hình xe tự lái và bộ phận kiểm thử an toàn vận hành.
2. **Output annotation nào thực sự cần?** (geometry, class, attribute nào) 
Hình học (Geometry): Các polyline chính xác đánh dấu trục đường kẻ làn và dải phân cách/lề đường.   

Class: Duy nhất class lane.

Attributes bắt buộc:

laneDirection: Phân định làn đường dọc (vertical) hay cắt ngang (parallel).   

laneTypes: Xác định loại ranh giới (single white, double white, single yellow, double yellow, road curb, unknown). 

laneStyle: Xác định kiểu nét vẽ (solid, dashed, unknown).  
3. **Failure nào gây hậu quả lớn nhất?** (đây sẽ là decision `critical` trong gold) 

Nhầm lẫn hướng làn (laneDirection): Gán nhầm làn xe chạy dọc (vertical) thành làn ngang (parallel). Hậu quả làm hệ thống lập kế hoạch di chuyển (Path Planning) hiểu sai quỹ đạo chạy của xe, dẫn đến nguy cơ chệch làn hoặc mất lái đột ngột trên đường cao tốc.   

Bỏ sót dải phân cách / Lề đường (road curb): Bỏ sót vạch biên hoặc gán sai lề đường thành vạch đơn trắng, khiến xe tự lái có thể đâm vào vỉa hè hoặc dải phân cách bê tông. 
4. **Khi ambiguity không resolve được, ai / ở đâu là escalation path?** 
Quy trình Escalate: Gán Tag escalated ở cấp độ Frame trong CVAT và ghi rõ mô tả lý do vào thuộc tính note (hoặc phần comment).   

Người tiếp nhận (Escalation Path): Chuyển trực tiếp lên Annotation Lead / QC Senior qua kênh trao đổi nội bộ dự án hoặc danh sách decision_log.csv để họp chốt quy tắc (Ratify). 

## Scope

- **Trong scope (bắt buộc label):** 
Tất cả các vạch kẻ phân chia làn đường (vạch trắng, vạch vàng, vạch đơn, vạch đôi, vạch nét liền, vạch nét đứt) còn nhìn rõ trên mặt đường.   

Các dải phân cách cứng, vỉa hè, biên lề đường (road curb) có vai trò định hình ranh giới di chuyển của làn xe.   

Các vạch kẻ làn bị che khuất một khoảng ngắn bởi phương tiện khác nhưng vẫn lộ rõ đường tiếp diễn (vẽ amodal nối liền).

- **Ngoài scope (ignore):** 
Vạch gờ giảm tốc ngắn, vạch kẻ ô bàn cờ (grid lines) cấm dừng đỗ ở ngã tư.

Vạch sơn phân luồng trong bãi đỗ xe nội bộ, sân nhà dân, hoặc khu vực không thuộc đường giao thông công cộng.

Vạch kẻ đã bị xóa bỏ, bị bong tróc/mờ nát quá 80% không thể xác định được quỹ đạo làn.

- **Geometry tolerance:**  (ví dụ "box ôm phần vỏ đèn nhìn thấy, lệch ≤ 2 px mỗi cạnh là đạt")
Polyline phải bám chính xác vào đường trục trung tâm (centerline) của vạch kẻ đường, sai số khoảng cách lệch ≤3 px so với đường gốc.

Các điểm đầu/cuối (endpoints) phải kéo dài sát mép ảnh hoặc chân trời, không được bỏ lửng ngắt chừng khi vạch kẻ vẫn còn hiển thị rõ.

## Output chấm được
— loại decision nào sẽ có trong blind test: LABEL / IGNORE / UNKNOWN / ESCALATE, class, attribute, geometry.
Mỗi loại phải nhìn thấy được trong file export CVAT, nếu không thì không chấm được.

Output chấm được
LABEL:

Geometry: Tất cả các đường kẻ làn/dải phân cách được vẽ bằng polyline chính xác trong CVAT.

Class: Gán nhãn lane duy nhất cho toàn bộ các polyline.

Attributes: Mỗi polyline có đầy đủ các thuộc tính laneDirection (vertical/parallel), laneTypes (single white, road curb,...), và laneStyle (solid/dashed). Xuất hiện trực tiếp dưới dạng trường thuộc tính (attributes) của từng object trong file export (Datumaro/COCO/CVAT XML).

IGNORE:

Các đường kẻ vạch quá mờ (>80%), vạch ô bàn cờ hay vạch giảm tốc ngắn sẽ không được vẽ polyline (hoặc đặt thuộc tính outside_scope nếu dự án yêu cầu) để loại trừ khỏi tập đánh giá IoU/Precision.

UNKNOWN:

Thể hiện rõ qua giá trị thuộc tính laneTypes = unknown hoặc laneStyle = unknown khi vạch kẻ đường bị bong tróc/che lấp không thể nhận diện chính xác loại vạch hay kiểu nét. Trường này được lưu trực tiếp dưới dạng giá trị attribute trong file export.

ESCALATE:

Thể hiện bằng Tag escalated ở cấp độ Frame và kèm theo đoạn văn bản mô tả lý do nghi vấn trong thuộc tính/comment note của object hoặc frame. Khi xuất dữ liệu export (CVAT XML/Datumaro), Tag và comment này sẽ xuất hiện ở cấp độ image/frame header để reviewer/lead lọc tự động và chấm điểm quyết định.

## Dữ liệu và giới hạn
— nguồn ảnh, số ảnh dự kiến dùng, giới hạn đã biết (ví dụ LISA trong repo chỉ có một clip 30 frame liên tiếp).

Nguồn ảnh: Dữ liệu hình ảnh quan sát làn đường cắt từ bộ dữ liệu chuẩn BDD100K (hoặc các khung hình thực tế từ camera hành trình phía trước của xe ego).

Số ảnh dự kiến dùng:

Tập Core calibration/test: 6 ảnh core (dùng cho vòng đối soát compare.html và compare.md).

Mở rộng (Scaleup): Dự kiến thử nghiệm trên lô nhỏ 500 – 1,000 frames trước khi mở rộng lên 100,000 frames.

Giới hạn đã biết (Known limitations):

Dữ liệu hiện tại chủ yếu là ảnh tĩnh cắt từ video (single frames), không có thông tin theo dõi liên tục (tracking ID) qua các khung hình thời gian.

Một số khung hình có chất lượng ánh sáng kém (lóa đèn ban đêm, bóng râm cây cối che khuất mặt đường) hoặc điều kiện thời tiết phức tạp (mặt đường ướt phản chiếu) gây khó khăn cho việc phân định màu sắc vạch kẻ (laneTypes).

Mật độ vạch kẻ đường phía cuối chân trời (xa camera) bị nhòe pixel, cần giới hạn khoảng cách gán nhãn để tránh sai số vẽ polyline.
