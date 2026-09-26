# Problem statement + downstream contract

Tối đa nửa trang, viết **trước khi mở CVAT**. Đây là bằng chứng của gate G1 (topic lock). Thay mọi placeholder
mới là xong.

## Bài toán

TODO — một câu: road element nào, trong tình huống nào, khó ở đâu. "Label traffic signs" là quá rộng; "hierarchical
sign taxonomy cho biển nhỏ/xa/bị che" là đủ cụ thể.

## Downstream contract

1. **Downstream task / model / user là ai?** TODO
2. **Output annotation nào thực sự cần?** (geometry, class, attribute nào) TODO
3. **Failure nào gây hậu quả lớn nhất?** (đây sẽ là decision `critical` trong gold) TODO
4. **Khi ambiguity không resolve được, ai / ở đâu là escalation path?** TODO

## Scope

- **Trong scope (bắt buộc label):** TODO
- **Ngoài scope (ignore):** TODO
- **Geometry tolerance:** TODO (ví dụ "box ôm phần vỏ đèn nhìn thấy, lệch ≤ 2 px mỗi cạnh là đạt")

## Output chấm được

TODO — loại decision nào sẽ có trong blind test: LABEL / IGNORE / UNKNOWN / ESCALATE, class, attribute, geometry.
Mỗi loại phải nhìn thấy được trong file export CVAT, nếu không thì không chấm được.

## Dữ liệu và giới hạn

TODO — nguồn ảnh, số ảnh dự kiến dùng, giới hạn đã biết (ví dụ LISA trong repo chỉ có một clip 30 frame liên tiếp).
