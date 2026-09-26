# Ontology + CVAT setup

Bảng ontology là **source of truth** cho schema CVAT: `03_cvat_labels.json` phải khớp từng dòng ở đây. Thay mọi
placeholder mới là xong (gate G2).

## Ontology table

| Name | Geometry | Type (class / attribute) | Allowed values | Default | Mutable? | Rationale |
|---|---|---|---|---|---|---|
| lane | polyline | class | N/A | N/A | No | Lớp đối tượng chính dùng để đánh dấu ranh giới làn đường, vạch kẻ đường hoặc lề đường. |
| laneDirection | polyline | attribute | vertical, parallel | vertical | No | Phân định hướng làn đường: chọn vertical cho các làn chạy dọc theo chiều di chuyển của xe (từ đáy ảnh lên tiêu điểm); chọn parallel cho các làn đường cắt ngang tầm nhìn. |
| laneTypes | polyline | attribute | single white, double white, single yellow, double yellow, road curb, unknown | single white | No | Loại vạch kẻ/ranh giới làn: dùng road curb cho dải phân cách cứng/biên lề đường; dùng unknown khi vạch bị hư hỏng/mờ nát >50% không xác định được loại. |
| laneStyle | polyline | attribute | solid, dashed, unknown | solid | No | Kiểu đường nét: chọn solid cho nét liền, dashed cho nét đứt; chỉ dùng unknown khi mặt đường hỏng nặng không phân biệt được kiểu nét liền hay đứt.    |

## Class hay attribute
— vì sao mỗi thứ là class hay attribute (xem README mục "2 · Viết guideline"). Default nào có thể gây bias khi
annotator quên đổi?

lane (Class): Được chọn làm lớp đối tượng chính (class) vì đại diện cho một loại đối tượng hình học độc lập và duy nhất trong bài toán xe tự lái. Nó có quy tắc vẽ riêng (polyline bám theo đường kẻ) và là thực thể nền tảng để mô hình downstream nhận diện ranh giới làn đường.

laneDirection (Attribute): Là thuộc tính (attribute) vì chỉ dùng để mô tả hướng của làn đường so với góc nhìn camera (vertical hoặc parallel). Việc tách thành một Class riêng sẽ làm bùng nổ tổ hợp lớp không cần thiết và gây rối cho sơ đồ dữ liệu (ontology).

laneTypes (Attribute): Là thuộc tính (attribute) thể hiện chủng loại/chất liệu vạch kẻ (single white, double white, single yellow, double yellow, road curb, unknown). Đây là thuộc tính mô tả bản chất của vạch kẻ trên cùng một đối tượng hình học.

laneStyle (Attribute): Là thuộc tính (attribute) thể hiện hình dáng vật lý của đường nét (solid, dashed, unknown). Giúp phân loại đường nét đứt hay liền mà không cần tạo ra nhiều Class con riêng biệt.   

Rủi ro thiên vị do giá trị mặc định (Default Bias):

laneDirection = vertical (Default): Nếu nhãn viên quên điều chỉnh khi gặp các vạch kẻ cắt ngang hoặc ngã tư, sẽ dẫn đến lỗi hệ thống gán nhầm làn ngang thành làn dọc (vertical).

laneTypes = single white (Default): Nếu nhãn viên bỏ qua việc đổi thuộc tính khi gán nhãn dải phân cách/lề đường (road curb) hoặc vạch vàng, mô hình sẽ học sai lệch ranh giới an toàn của làn xe chạy.

laneStyle = solid (Default): Nếu nhãn viên quên chuyển sang dashed ở các đoạn vạch nét đứt, mô hình sẽ nhận diện nhầm vạch cho phép chuyển làn thành vạch cấm chuyển làn, ảnh hưởng trực tiếp đến thuật toán lập kế hoạch di chuyển (Path Planning). 

## CVAT

- **Phiên bản CVAT** (`make cvat-status`): 1.0
- **Tên task calibration** (có version guideline, ví dụ `team07-calib-v1`): TAM108-calib-v1
- **Guide của task đã dán `02_guideline.md`?** có (có / chưa)
- **Nhóm dùng Track hay Shape, vì sao:** Shape, vì task chỉ gồm ảnh tĩnh

## Setup test

Một thành viên **chưa tham gia setup** mở task và trả lời: label gì, dùng tool nào, gán attribute nào, khi nào
escalate. Ghi lại ai test và chỗ họ vấp:

1. Label sử dụng

lane: Sử dụng duy nhất 1 Class chính tên là lane cho toàn bộ các ranh giới làn đường, vạch kẻ đường, dải phân cách cứng hoặc lề đường (road curb). 

2. Công cụ (Tool) trong CVAT

Draw new polyline (N / Shift + N): Dùng công cụ vẽ đường polyline (Polyline) trong CVAT.

Đặt các điểm (points) bám sát vào đường trục chính/trung tâm của vạch kẻ đường.

Dùng tối thiểu số điểm cần thiết cho đường thẳng (2–3 điểm), bổ sung thêm điểm mịn ở các đoạn đường cong.

3. Thuộc tính (Attributes) cần gán cho mỗi Polyline
| Attribute | Giá trị chọn trong CVAT | Khi nào gán (Điều kiện) |
|---|---|---|
| laneDirection | vertical | Gán cho các vạch/làn đường chạy dọc theo chiều di chuyển của xe (hướng từ đáy ảnh lên tâm góc nhìn). (Mặc định) |
| laneDirection | parallel | Gán cho các vạch kẻ đường cắt ngang tầm nhìn của camera (ví dụ: vạch dừng ngã tư, vạch đi bộ qua đường). |
| laneTypes | single white | Vạch đơn màu trắng. (Mặc định) |
| laneTypes | double white | Vạch đôi màu trắng. |
| laneTypes | single yellow | Vạch đơn màu vàng. |
| laneTypes | double yellow | Vạch đôi màu vàng. |
| laneTypes | road curb | Ranh giới dải phân cách cứng, vỉa hè hoặc lề đường bê tông. |
| laneTypes | unknown | Chỉ chọn khi vạch kẻ bị bong tróc, hư hỏng nặng (>50%) không thể phân biệt được loại vạch/màu sơn. |
| laneStyle | solid | Vạch nét liền. (Mặc định) |
| laneStyle | dashed | Vạch nét đứt đoạn. |
| laneStyle | unknown | Chỉ chọn khi mặt đường bị hỏng/che lấp không rõ nét liền hay nét đứt. |

4. Khi nào Escalate và cách thể hiện trong CVAT

Trường hợp cần Escalate (Chuyển lên cấp trên/Lead xem xét):

Bất đồng quy tắc: Khi ranh giới giữa lề đường (road curb) và làn xe di chuyển không rõ ràng do vệt bánh xe hoặc đường thi công dở dang.

Che khuất/Mờ nhòe nặng: Ánh sáng lóa đèn ban đêm hoặc bóng râm lấp hoàn toàn mặt đường khiến không thể xác định được có vạch kẻ thực sự hay không.

Trường hợp ngoại lệ (Edge cases): Xuất hiện loại vạch kẻ lạ chưa có trong hướng dẫn (guideline gap).

Cách thể hiện trong CVAT (để xuất hiện trong export file):

Thêm Tag escalated: Tạo một Tag ở cấp độ Frame (Add Tag -> chọn escalated).

Ghi chú cụ thể: Trong phần thuộc tính note (hoặc comment của Object/Job), ghi rõ ngắn gọn lý do nghi vấn (Ví dụ: "Nghi vấn road curb hay single white do lóa đèn đêm, cần Lead xác nhận").
