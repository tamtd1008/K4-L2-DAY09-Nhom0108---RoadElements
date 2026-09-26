# Nếu scale lên 100k frames

Họ tên: Tưởng Đức Tâm

Mỗi mini-task trả lời một câu: **"Nếu scale lên 100k frames, lỗi nào sẽ trở thành systematic defect?"** Viết ngay sau
khi ghi comparison log của task đó. Dựa vào một lỗi bạn **thật sự** gặp hôm nay. Xoá mọi chữ  khi xong.

Mỗi câu trả lời có 3 phần: lỗi (và bằng chứng: task + sample), vì sao nó lặp lại có hệ thống thay vì ngẫu nhiên,
và cách phát hiện sớm (lát nào cần oversample, tín hiệu QC nào).

## Lane

Lỗi gán sai thuộc tính hướng làn `laneDirection` (nhầm giữa `vertical` và `parallel` - bằng chứng: task `lane`, sample `b75f355e-b3f098b9.jpg`) sẽ trở thành systematic defect vì gán nhầm quy chuẩn góc nhìn camera (hiểu sai làn đường chạy dọc theo chiều di chuyển của xe là `parallel` thay vì `vertical`), dẫn đến việc toàn bộ nhãn viên áp dụng sai quy định này một cách đồng bộ trên hàng loạt ảnh; để phát hiện sớm, cần oversample các lát cắt ảnh có làn đường thu hẹp về phía tâm (perspective convergence) hoặc đường cong/đổi hướng, đồng thời thiết lập tín hiệu QC bằng tự động hóa script kiểm tra tỷ lệ bất thường giữa số lượng polyline mang thuộc tính `parallel` so với `vertical` trong từng lô dữ liệu.

## Drivable area



## Traffic sign



## Traffic light


