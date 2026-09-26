# Traffic light log

Họ tên: TODO

Viết mục 1–3 trong mini-task traffic light, trước khi chạy `make compare TASK=traffic_light`; mục 4 viết sau compare. Mỗi track là một đầu đèn bạn đã
vẽ. Xoá mọi chữ `TODO` khi xong.

## 1. Các track

`state` theo frame: ghi dạng khoảng, ví dụ `red 0–14, green 15–29`. Frame đếm từ 0 như trong CVAT.

| Track (#id CVAT) | pictogram | state theo frame | relevance | Bằng chứng cho relevance |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

## 2. Điểm chuyển state

- Đèn đổi state ở frame nào? Frame liền trước trông ra sao (đèn tắt, hai màu cùng sáng, mờ)? TODO
- Bạn đặt keyframe ở đâu, và bạn đã kiểm tra mọi frame giữa hai keyframe chưa? TODO

## 3. Các đầu đèn nhỏ ở ngã tư phía xa

Bạn có vẽ không? Nếu có: `relevance` là gì, `state` đọc được ở frame nào? Nếu không: vì sao? TODO

## 4. Sau khi so với reference

Điền sau `make compare`. Reference (LISA) không có `relevance` và không gán các đèn nhỏ ở xa.

- Khác biệt về state/pictogram, và ai đúng: TODO
- Track của bạn không có trong reference: giữ hay bỏ, vì sao: TODO
