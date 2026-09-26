# Traffic sign tree

Họ tên: TODO · Chế độ: TODO (`cá nhân` hoặc `nhóm`) · Nếu nhóm — các thành viên: TODO

Viết sau mini-task traffic sign (phút ~155). Dựa vào những biển **bạn đã vẽ** trong 7 ảnh core, không chép danh sách
43 class. Xoá mọi chữ `TODO` khi xong — `make check` đếm chữ này.

## 1. Cây của bạn

Chỉ liệt kê class có trong ảnh core. Đếm số box của từng class. Class có 1 box trong cả batch là ứng viên "hiếm".

| family | class (`sign_class`) | Số box trong core | Phổ biến / hiếm | Ảnh ví dụ |
|---|---|---|---|---|
| prohibitory | TODO | TODO | TODO | TODO |
| mandatory | TODO | TODO | TODO | TODO |
| danger | TODO | TODO | TODO | TODO |
| other | TODO | TODO | TODO | TODO |

## 2. Hai quyết định merge/split

Mỗi quyết định: giữ tách hay gộp, vì sao, và cái giá nếu chọn sai (model downstream nhầm gì).

**Quyết định 1 — `09 no overtaking` và `10 no overtaking (trucks)`: tách hay gộp?**
TODO

**Quyết định 2 — nhóm `other` của GTSDB khi dùng ở Việt Nam.**
GTSDB xếp biển hết hạn chế (`06`, `32`, `41`, `42`) vào `other`. QCVN 41:2024/BGTVT xếp biển hết hiệu lực
(`DP.133`–`DP.135`) vào nhóm **biển báo cấm**. Cây của bạn theo cách nào, và cần rule gì để hai người label giống nhau?
TODO

## 3. Chính sách cho class hiếm và biển không đọc được

Khi gặp biển không có trong 43 class, hoặc quá nhỏ để đọc: bạn chọn `sign_family`, `sign_class`, `readable` thế nào?
Dẫn một box cụ thể (ảnh + vị trí) làm bằng chứng.
TODO

## 4. Dòng decision log tương ứng

Id của dòng trong `decision_log.csv` ghi rule ở mục 2 hoặc 3: TODO
