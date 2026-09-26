# So sánh traffic_sign

> Các số dưới đây là số của công cụ so sánh, không phải ngưỡng chấm.

Box GTSDB (43 class Đức). GT không có readable, truncated, relevant_to_ego — các attribute này tự đối chiếu bằng decision log.

Trùng từng đỉnh với reference: 0/24 shape (<= 0,5 px).

## 00026.png

- R1/B2: IoU 0.796
- readable, truncated, relevant_to_ego: GT không có, không so — tự đối chiếu bằng decision log
- B1: box bạn vẽ không có trong reference — gợi ý `guideline_gap`

## 00054.png

- R4/B1: IoU 0.848
- R1/B2: IoU 0.830
- R2/B3: IoU 0.738
- readable, truncated, relevant_to_ego: GT không có, không so — tự đối chiếu bằng decision log
- R3: bạn thiếu biển có trong reference — gợi ý `missing`
- B4: box bạn vẽ không có trong reference — gợi ý `guideline_gap`

## 00073.png

- R3/B3: IoU 0.867
- R1/B1: IoU 0.824
- R1/B1: sign_class: bạn 31 animals, reference 23 slippery road — gợi ý `class`
- R6/B6: IoU 0.823
- R4/B4: IoU 0.822
- R4/B4: sign_class: bạn 31 animals, reference 23 slippery road — gợi ý `class`
- R2/B2: IoU 0.778
- R5/B5: IoU 0.772
- readable, truncated, relevant_to_ego: GT không có, không so — tự đối chiếu bằng decision log

## 00088.png

- R4/B3: IoU 0.779
- R3/B1: IoU 0.776
- R1/B4: IoU 0.725
- R1/B4: sign_class: bạn 09 no overtaking, reference 10 no overtaking (trucks) — gợi ý `class`
- R2/B2: IoU 0.706
- R2/B2: sign_class: bạn 09 no overtaking, reference 10 no overtaking (trucks) — gợi ý `class`
- readable, truncated, relevant_to_ego: GT không có, không so — tự đối chiếu bằng decision log

## 00206.png

- R4/B2: IoU 0.943
- R2/B5: IoU 0.906
- R3/B1: IoU 0.888
- R1/B3: IoU 0.865
- R5/B4: IoU 0.821
- readable, truncated, relevant_to_ego: GT không có, không so — tự đối chiếu bằng decision log

## 00223.png

- R1/B1: IoU 0.879
- readable, truncated, relevant_to_ego: GT không có, không so — tự đối chiếu bằng decision log
- B2: box bạn vẽ không có trong reference — gợi ý `guideline_gap`
- B3: box bạn vẽ không có trong reference — gợi ý `guideline_gap`

## Dòng gợi ý cho comparison_log.csv

```csv
task,sample,object,difference,error_type,who_is_right,action,note
traffic_sign,00026.png,B1,B1: box bạn vẽ không có trong reference,guideline_gap,,,
traffic_sign,00054.png,R3,R3: bạn thiếu biển có trong reference,missing,,,
traffic_sign,00054.png,B4,B4: box bạn vẽ không có trong reference,guideline_gap,,,
traffic_sign,00073.png,R1/B1,"R1/B1: sign_class: bạn 31 animals, reference 23 slippery road",class,,,
traffic_sign,00073.png,R4/B4,"R4/B4: sign_class: bạn 31 animals, reference 23 slippery road",class,,,
traffic_sign,00088.png,R1/B4,"R1/B4: sign_class: bạn 09 no overtaking, reference 10 no overtaking (trucks)",class,,,
traffic_sign,00088.png,R2/B2,"R2/B2: sign_class: bạn 09 no overtaking, reference 10 no overtaking (trucks)",class,,,
traffic_sign,00223.png,B2,B2: box bạn vẽ không có trong reference,guideline_gap,,,
traffic_sign,00223.png,B3,B3: box bạn vẽ không có trong reference,guideline_gap,,,
```

Hãy điền `who_is_right`, `action`, `note`; loại lỗi chỉ là gợi ý.
