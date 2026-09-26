# RUBRIC — người chấm đọc bài Day 9 như thế nào

Tiêu chí, điểm và cap lấy từ playbook *Road Elements Lab · Guideline Design Challenge* của giảng viên. Cột "Nhìn vào
đâu" là chỗ bằng chứng nằm trong repo này. Topic và lời giải mở; rubric chung cho mọi nhóm.

Người chấm chấm **artifact và bằng chứng**, không chấm độ mới của tool. Một guideline trình bày đẹp nhưng nhóm peer
không dùng được sẽ mất điểm lớn ở transferability.

## Thang 100 điểm

| Tiêu chí | Điểm | Bằng chứng tốt trông như thế nào | Nhìn vào đâu |
|---|---|---|---|
| Problem + downstream framing | 10 | Use case hẹp, failure/risk rõ, scope/ignore/escalation hợp lý | `01_problem_statement.md` |
| Ontology + CVAT setup | 15 | Geometry/class/attribute hợp lý; task chạy được; setup phản ánh guideline | `03_ontology_and_cvat_setup.md`, `03_cvat_labels.json`, `09_cvat_export_or_task_reference.txt` |
| Guideline clarity + completeness | 20 | Rule actionable, không có rule chỉ nói miệng, cover cả case normal và ambiguous | `02_guideline.md` (v3) |
| Edge-case library | 15 | ≥ 8 case có ý nghĩa, đa dạng, expected decision và rationale rõ | `04_edge_cases/edge_case_cards.md`, `gold_decisions.csv` |
| QA design + metrics | 15 | Severity, sampling, metric, threshold, rework, gate cụ thể và đo được | `05_qa_plan.md` |
| Calibration evidence | 5 | Có phân tích bất đồng + rule refinement có rationale | `06_calibration_measure.csv`, `06_calibration_report.csv`, dòng v2 trong `08_revision_log.md` |
| Blind handoff transferability | 20 | GTS + feedback usability của peer + root cause + guideline revision | `07_blind_handoff/`, dòng v3 trong `08_revision_log.md` |
| **Tổng** | **100** | | |

### 20 điểm Blind Handoff

| Tiêu chí con | Điểm | Bằng chứng |
|---|---|---|
| Decision accuracy | 10 | D trong GTS: đúng inclusion / class / attribute / ignore / escalate |
| Critical decision correctness | 4 | Không có critical decision sai hoặc lọt; blind set có ≥ 2 cơ hội critical |
| Geometry-rule compliance | 2 | Output theo tolerance/rule đã viết, không theo "cảm giác" |
| Clarification independence | 2 | Ít câu hỏi ngoài guideline; log trung thực |
| Revision quality | 2 | Feedback của peer thành rule / example / escalation, hoặc bị từ chối có bằng chứng |

**Critical cap:** nếu peer mắc critical error vì guideline thiếu hoặc mơ hồ, và owner không có rule hay escalation để
ngăn, phần Blind Handoff tối đa **10/20**.

GTS (`make gts`) là bằng chứng cho 18/20 điểm con đầu, không phải điểm thẳng. Người chấm đọc cùng `transfer_score.csv`
(cột `note` giải thích từng `correct`), `clarification_log.csv` và phân loại nguyên nhân trong `peer_feedback.md`.

## Checklist cuối

| Specification | Validation |
|---|---|
| Problem + downstream contract rõ | CVAT task dùng được bởi người khác |
| Scope / inclusion / exclusion viết được | QA có metric + threshold + rework |
| Ontology + geometry + attribute có rationale | Calibration có bằng chứng |
| ≥ 8 edge case, có case critical và case escalation | Gold freeze trước handoff |
| Không có rule chỉ nói miệng | GTS + peer feedback + revision log hoàn tất |

`make check` chỉ kiểm **đủ file và đúng quy trình** (6 gate). Đủ gate không có nghĩa là đủ điểm.

## Những điều không làm giảm đánh giá

- GTS thấp mà owner chẩn đoán đúng nguyên nhân bằng bằng chứng và sửa guideline tương ứng. GTS đo độ chuyển giao của
  specification lúc freeze; revision quality chấm việc nhóm học được gì từ đó.
- Peer ghi câu hỏi trung thực vào clarification log — log trung thực là một phần của tiêu chí independence.
- Threshold QA khác nhóm khác, miễn giải thích được trade-off cost/risk theo downstream contract.
- Không làm stretch.

## Những điều người chấm sẽ hỏi lại

- `make verify` báo gold hoặc sample pack đổi sau freeze, hoặc `FREEZE.txt` có `refreeze_count` mà không có lý do
  trong `08_revision_log.md`.
- `correct = 1` nhưng `peer_evidence` và `note` không cho thấy vì sao.
- Clarification log trống trong khi Lab Coach ghi nhận owner đã giải thích rule bằng miệng.
- Ontology table và `03_cvat_labels.json` không khớp (tên label, attribute, default).
- Owner đổ lỗi cho peer mà không phân loại guideline gap / data ambiguity / execution error.
