# So sánh drivable

> Các số dưới đây là số của công cụ so sánh, không phải ngưỡng chấm.

Polygon BDD100K đổi từ toạ độ normalized sang pixel 1280×720. BDD không có tag needs_review.

Trùng từng đỉnh với reference: 0/10 shape (<= 0,5 px).

## bb5cc516-c98d1fbe.jpg

- direct: IoU 0.431; chỉ reference 21977 px; chỉ bạn 3490 px
- direct: vùng hình học khác reference (21977 px thiếu, 3490 px thừa) — gợi ý `geometry`
- alternative: IoU 0.612; chỉ reference 2954 px; chỉ bạn 26115 px
- alternative: vùng hình học khác reference (2954 px thiếu, 26115 px thừa) — gợi ý `geometry`
- mọi vùng: IoU 0.782; chỉ reference 8938 px; chỉ bạn 13612 px
- mọi vùng: vùng hình học khác reference (8938 px thiếu, 13612 px thừa) — gợi ý `geometry`

## be860305-899a96c3.jpg

- direct: IoU 0.513; chỉ reference 31345 px; chỉ bạn 197 px
- direct: vùng hình học khác reference (31345 px thiếu, 197 px thừa) — gợi ý `geometry`
- alternative: IoU 0.000; chỉ reference 39403 px; chỉ bạn 34460 px
- alternative: vùng hình học khác reference (39403 px thiếu, 34460 px thừa) — gợi ý `geometry`
- mọi vùng: IoU 0.545; chỉ reference 43337 px; chỉ bạn 7246 px
- mọi vùng: vùng hình học khác reference (43337 px thiếu, 7246 px thừa) — gợi ý `geometry`

## c068a67b-03b6e200.jpg

- direct: IoU 0.933; chỉ reference 1818 px; chỉ bạn 5639 px
- direct: vùng hình học khác reference (1818 px thiếu, 5639 px thừa) — gợi ý `geometry`
- alternative: IoU 0.000; chỉ reference 59261 px; chỉ bạn 81615 px
- alternative: vùng hình học khác reference (59261 px thiếu, 81615 px thừa) — gợi ý `geometry`
- mọi vùng: IoU 0.413; chỉ reference 61079 px; chỉ bạn 87254 px
- mọi vùng: vùng hình học khác reference (61079 px thiếu, 87254 px thừa) — gợi ý `geometry`

## c3cd6c82-b5d52beb.jpg

- direct: IoU 0.879; chỉ reference 6224 px; chỉ bạn 4466 px
- direct: vùng hình học khác reference (6224 px thiếu, 4466 px thừa) — gợi ý `geometry`
- alternative: IoU 0.977; chỉ reference 739 px; chỉ bạn 360 px
- alternative: vùng hình học khác reference (739 px thiếu, 360 px thừa) — gợi ý `geometry`
- mọi vùng: IoU 0.914; chỉ reference 6963 px; chỉ bạn 4826 px
- mọi vùng: vùng hình học khác reference (6963 px thiếu, 4826 px thừa) — gợi ý `geometry`

## c723ad21-efed33e5.jpg

- direct: IoU 0.891; chỉ reference 2097 px; chỉ bạn 14323 px
- direct: vùng hình học khác reference (2097 px thiếu, 14323 px thừa) — gợi ý `geometry`
- alternative: IoU 0.000; chỉ reference 26105 px; chỉ bạn 0 px
- alternative: vùng hình học khác reference (26105 px thiếu, 0 px thừa) — gợi ý `geometry`
- mọi vùng: IoU 0.759; chỉ reference 28202 px; chỉ bạn 14323 px
- mọi vùng: vùng hình học khác reference (28202 px thiếu, 14323 px thừa) — gợi ý `geometry`

## Dòng gợi ý cho comparison_log.csv

```csv
task,sample,object,difference,error_type,who_is_right,action,note
drivable,bb5cc516-c98d1fbe.jpg,direct,"direct: vùng hình học khác reference (21977 px thiếu, 3490 px thừa)",geometry,,,
drivable,bb5cc516-c98d1fbe.jpg,alternative,"alternative: vùng hình học khác reference (2954 px thiếu, 26115 px thừa)",geometry,,,
drivable,bb5cc516-c98d1fbe.jpg,mọi vùng,"mọi vùng: vùng hình học khác reference (8938 px thiếu, 13612 px thừa)",geometry,,,
drivable,be860305-899a96c3.jpg,direct,"direct: vùng hình học khác reference (31345 px thiếu, 197 px thừa)",geometry,,,
drivable,be860305-899a96c3.jpg,alternative,"alternative: vùng hình học khác reference (39403 px thiếu, 34460 px thừa)",geometry,,,
drivable,be860305-899a96c3.jpg,mọi vùng,"mọi vùng: vùng hình học khác reference (43337 px thiếu, 7246 px thừa)",geometry,,,
drivable,c068a67b-03b6e200.jpg,direct,"direct: vùng hình học khác reference (1818 px thiếu, 5639 px thừa)",geometry,,,
drivable,c068a67b-03b6e200.jpg,alternative,"alternative: vùng hình học khác reference (59261 px thiếu, 81615 px thừa)",geometry,,,
drivable,c068a67b-03b6e200.jpg,mọi vùng,"mọi vùng: vùng hình học khác reference (61079 px thiếu, 87254 px thừa)",geometry,,,
drivable,c3cd6c82-b5d52beb.jpg,direct,"direct: vùng hình học khác reference (6224 px thiếu, 4466 px thừa)",geometry,,,
drivable,c3cd6c82-b5d52beb.jpg,alternative,"alternative: vùng hình học khác reference (739 px thiếu, 360 px thừa)",geometry,,,
drivable,c3cd6c82-b5d52beb.jpg,mọi vùng,"mọi vùng: vùng hình học khác reference (6963 px thiếu, 4826 px thừa)",geometry,,,
drivable,c723ad21-efed33e5.jpg,direct,"direct: vùng hình học khác reference (2097 px thiếu, 14323 px thừa)",geometry,,,
drivable,c723ad21-efed33e5.jpg,alternative,"alternative: vùng hình học khác reference (26105 px thiếu, 0 px thừa)",geometry,,,
drivable,c723ad21-efed33e5.jpg,mọi vùng,"mọi vùng: vùng hình học khác reference (28202 px thiếu, 14323 px thừa)",geometry,,,
```

Hãy điền `who_is_right`, `action`, `note`; loại lỗi chỉ là gợi ý.
