# QA plan + quality gates

Không được viết "reviewer kiểm tra lại". Phải có sampling, metric, threshold và action khi fail. Thay mọi placeholder
mới là xong (gate G6).

## Flow

Guideline → Calibration → Production → Self-QC → Review → Rework → Quality Gate. Ghi cụ thể cho project của nhóm:

- **Ai review, review bao nhiêu:** TODO
- **Chọn sample theo rule nào** (random, theo tag rủi ro, theo annotator mới…): TODO
- **Issue được ghi ở đâu, đóng thế nào:** TODO
- **Khi phát hiện guideline gap thì update và version ra sao:** TODO

## Defect severity

Nhóm được đổi mapping nếu downstream contract khác, nhưng phải giải thích và chốt trước khi QA.

| Severity | Định nghĩa cho project này | Ví dụ | Action mặc định |
|---|---|---|---|
| Critical | TODO | TODO | TODO |
| Major | TODO | TODO | TODO |
| Minor | TODO | TODO | TODO |
| Question | TODO | TODO | TODO |

## Metrics

| Metric | Cách tính | Vì sao phù hợp với bài toán |
|---|---|---|
| TODO | TODO | TODO |

Metric high-risk tách riêng (ví dụ critical defect escape rate): TODO

## Quality gate

Threshold là đề xuất của nhóm, không phải chuẩn ngành. Giải thích trade-off cost/risk.

```text
PASS if:
  TODO
REWORK if: TODO
REJECT / ESCALATE if: TODO
```

Trade-off: TODO
