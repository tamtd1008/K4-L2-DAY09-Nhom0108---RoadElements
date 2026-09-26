# So sánh lane

> Các số dưới đây là số của công cụ so sánh, không phải ngưỡng chấm.

Reference lane do người thiết kế lab vẽ theo card 1 trên 6 ảnh core, KHÔNG phải GT chính thức BDD100K. Khác reference chưa chắc là bạn sai: ghi who_is_right và lý do.

Trùng từng đỉnh với reference: 0/20 shape (<= 0,5 px).

## b75f355e-b3f098b9.jpg

- B-tag: weather: bạn clear, reference partly cloudy — gợi ý `attribute`
- R1/B2: khoảng cách 3.5 px
- R1/B2: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R2: bạn thiếu polyline reference — gợi ý `missing`
- B1: polyline bạn vẽ không có trong reference — gợi ý `guideline_gap`

## bb890202-d9d48310.jpg

- B-tag: weather: bạn clear, reference partly cloudy — gợi ý `attribute`
- R1/B1: khoảng cách 0.7 px
- R1/B1: laneStyle: bạn solid, reference dashed — gợi ý `attribute`
- R1/B1: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R5/B5: khoảng cách 1.2 px
- R5/B5: laneTypes: bạn road curb, reference single white — gợi ý `attribute`
- R5/B5: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R2/B2: khoảng cách 1.6 px
- R2/B2: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R6/B4: khoảng cách 2.6 px
- R6/B4: laneTypes: bạn road curb, reference single white — gợi ý `attribute`
- R6/B4: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R3/B3: khoảng cách 17.5 px
- R3/B3: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R4: bạn thiếu polyline reference — gợi ý `missing`

## c0f739d8-6ff93525.jpg

- R1/B1: khoảng cách 2.2 px
- R1/B1: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R2: bạn thiếu polyline reference — gợi ý `missing`
- B2: polyline bạn vẽ không có trong reference — gợi ý `guideline_gap`

## c1589305-200e315b.jpg

- B-tag: weather: bạn clear, reference partly cloudy — gợi ý `attribute`
- R2/B2: khoảng cách 2.0 px
- R2/B2: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R1/B1: khoảng cách 3.2 px
- R1/B1: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R3/B5: khoảng cách 4.8 px
- R3/B5: laneDirection: bạn parallel, reference vertical — gợi ý `attribute`
- R4/B4: khoảng cách 13.7 px
- R4/B4: laneDirection: bạn parallel, reference vertical — gợi ý `attribute`
- R5: bạn thiếu polyline reference — gợi ý `missing`
- R6: bạn thiếu polyline reference — gợi ý `missing`
- B3: polyline bạn vẽ không có trong reference — gợi ý `guideline_gap`

## c3cd6c82-b5d52beb.jpg

- B-tag: weather: bạn clear, reference overcast — gợi ý `attribute`
- R2/B2: khoảng cách 1.7 px
- R2/B2: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R3/B3: khoảng cách 1.8 px
- R3/B3: laneTypes: bạn road curb, reference single white — gợi ý `attribute`
- R3/B3: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R1/B1: khoảng cách 3.3 px
- R1/B1: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R4/B4: khoảng cách 3.5 px
- R4/B4: laneTypes: bạn road curb, reference single white — gợi ý `attribute`
- R4/B4: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`

## c95fecc3-41401a5f.jpg

- R2/B1: khoảng cách 0.8 px
- R2/B1: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R3/B2: khoảng cách 2.5 px
- R3/B2: laneDirection: bạn vertical, reference parallel — gợi ý `attribute`
- R1: bạn thiếu polyline reference — gợi ý `missing`
- R4: bạn thiếu polyline reference — gợi ý `missing`
- R5: bạn thiếu polyline reference — gợi ý `missing`

## Dòng gợi ý cho comparison_log.csv

```csv
task,sample,object,difference,error_type,who_is_right,action,note
lane,b75f355e-b3f098b9.jpg,B-tag,"B-tag: weather: bạn clear, reference partly cloudy",attribute,,,
lane,b75f355e-b3f098b9.jpg,R1/B2,"R1/B2: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,b75f355e-b3f098b9.jpg,R2,R2: bạn thiếu polyline reference,missing,,,
lane,b75f355e-b3f098b9.jpg,B1,B1: polyline bạn vẽ không có trong reference,guideline_gap,,,
lane,bb890202-d9d48310.jpg,B-tag,"B-tag: weather: bạn clear, reference partly cloudy",attribute,,,
lane,bb890202-d9d48310.jpg,R1/B1,"R1/B1: laneStyle: bạn solid, reference dashed",attribute,,,
lane,bb890202-d9d48310.jpg,R1/B1,"R1/B1: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,bb890202-d9d48310.jpg,R5/B5,"R5/B5: laneTypes: bạn road curb, reference single white",attribute,,,
lane,bb890202-d9d48310.jpg,R5/B5,"R5/B5: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,bb890202-d9d48310.jpg,R2/B2,"R2/B2: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,bb890202-d9d48310.jpg,R6/B4,"R6/B4: laneTypes: bạn road curb, reference single white",attribute,,,
lane,bb890202-d9d48310.jpg,R6/B4,"R6/B4: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,bb890202-d9d48310.jpg,R3/B3,"R3/B3: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,bb890202-d9d48310.jpg,R4,R4: bạn thiếu polyline reference,missing,,,
lane,c0f739d8-6ff93525.jpg,R1/B1,"R1/B1: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c0f739d8-6ff93525.jpg,R2,R2: bạn thiếu polyline reference,missing,,,
lane,c0f739d8-6ff93525.jpg,B2,B2: polyline bạn vẽ không có trong reference,guideline_gap,,,
lane,c1589305-200e315b.jpg,B-tag,"B-tag: weather: bạn clear, reference partly cloudy",attribute,,,
lane,c1589305-200e315b.jpg,R2/B2,"R2/B2: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c1589305-200e315b.jpg,R1/B1,"R1/B1: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c1589305-200e315b.jpg,R3/B5,"R3/B5: laneDirection: bạn parallel, reference vertical",attribute,,,
lane,c1589305-200e315b.jpg,R4/B4,"R4/B4: laneDirection: bạn parallel, reference vertical",attribute,,,
lane,c1589305-200e315b.jpg,R5,R5: bạn thiếu polyline reference,missing,,,
lane,c1589305-200e315b.jpg,R6,R6: bạn thiếu polyline reference,missing,,,
lane,c1589305-200e315b.jpg,B3,B3: polyline bạn vẽ không có trong reference,guideline_gap,,,
lane,c3cd6c82-b5d52beb.jpg,B-tag,"B-tag: weather: bạn clear, reference overcast",attribute,,,
lane,c3cd6c82-b5d52beb.jpg,R2/B2,"R2/B2: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c3cd6c82-b5d52beb.jpg,R3/B3,"R3/B3: laneTypes: bạn road curb, reference single white",attribute,,,
lane,c3cd6c82-b5d52beb.jpg,R3/B3,"R3/B3: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c3cd6c82-b5d52beb.jpg,R1/B1,"R1/B1: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c3cd6c82-b5d52beb.jpg,R4/B4,"R4/B4: laneTypes: bạn road curb, reference single white",attribute,,,
lane,c3cd6c82-b5d52beb.jpg,R4/B4,"R4/B4: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c95fecc3-41401a5f.jpg,R2/B1,"R2/B1: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c95fecc3-41401a5f.jpg,R3/B2,"R3/B2: laneDirection: bạn vertical, reference parallel",attribute,,,
lane,c95fecc3-41401a5f.jpg,R1,R1: bạn thiếu polyline reference,missing,,,
lane,c95fecc3-41401a5f.jpg,R4,R4: bạn thiếu polyline reference,missing,,,
lane,c95fecc3-41401a5f.jpg,R5,R5: bạn thiếu polyline reference,missing,,,
```

Hãy điền `who_is_right`, `action`, `note`; loại lỗi chỉ là gợi ý.
