# Day 9 Lab — Road Elements Guideline Design Challenge · 240 phút

Mỗi nhóm thiết kế một annotation project **bàn giao được**: bài toán rõ, guideline đủ dùng, task CVAT chạy được, edge
case có gold decision, QA đo được — và **một nhóm khác làm theo được mà không cần tác giả đứng cạnh**.

Lab này không chấm ai vẽ đẹp nhất. Nó chấm nhóm có dựng được một annotation system mà người khác vận hành được hay
không. Definition of done: một nhóm khác dùng guideline + CVAT task của bạn và tạo ra output đúng theo expectation bạn
đã **freeze trước**.

`Research → Specify → Configure → Calibrate → QA → Blind test → Revise`

## Ai làm gì

| Vai | Được làm | Không làm |
|---|---|---|
| Nhóm bạn | Research, chọn scope, thiết kế ontology/guideline, setup CVAT, tạo edge case, QA, test nhóm khác | Hỏi giảng viên "đáp án label đúng là gì" |
| Lab Coach | Giữ timeline, hỗ trợ CVAT/login/import/export/git, ghép cặp, xác nhận gold đã freeze | Sửa guideline, quyết định domain semantics thay nhóm |
| Giảng viên | Briefing, duyệt topic, chấm cuối | Đưa starter solution, giải edge case thay nhóm |
| Nhóm peer | Dùng guideline/task như annotator mới, label blind sample, góp ý usability | Xem gold trước khi test, nhờ owner "giảng lại" guideline trong blind window |

Hỏi "vẽ thế này đúng chưa?" sẽ được trả lời bằng câu hỏi ngược: rule của nhóm là gì, bằng chứng gì, nếu không đủ bằng
chứng thì guideline có escalation path không?

## Chuẩn bị (trước phút 0)

1. **Một repo cho cả nhóm.** Một người chọn **Use this template → Create a new repository** trên trang repo mẫu, rồi
   vào **Settings → Collaborators** thêm các thành viên còn lại. Mọi người clone repo đó về một thư mục **không có dấu
   tiếng Việt và khoảng trắng** trong đường dẫn.
2. Mở terminal trong thư mục `guideline-challenge/` của repo (`cd guideline-challenge`), chạy `make help`. Bài này
   chỉ dùng thư mục `guideline-challenge/`; thư mục `mini-task/` là bài khác, để nguyên. Không có `make` (thường gặp trên Windows) thì dùng lệnh
   `python lab9.py …` ở cột phải bảng lệnh — hai cách cho cùng kết quả. Tool chỉ cần Python 3, không cài thêm gì.
3. **Mỗi người** bật CVAT **đã cài từ Day 2** trên máy mình — không cài lại. Mở Docker Desktop, vào thư mục CVAT
   (`cvat-day2`, hoặc `cvat` nếu đã cài bản mới ở Day 8), chạy `docker compose start`, quay về thư mục
   `guideline-challenge/` chạy `make cvat-status`. Chi tiết: [GUIDE mục 1](GUIDE.md#1-bật-cvat-đã-cài).

Nhóm 3–5 người (tối thiểu 2 — calibration cần ít nhất 2 người label độc lập). Lab Coach công bố cặp peer: A ↔ B,
C ↔ D…; số nhóm lẻ thì ring 3 nhóm A → B → C → A.

## Lệnh dùng trong buổi

| Việc | Có `make` | Không có `make` |
|---|---|---|
| Kiểm CVAT đang chạy | `make cvat-status` | `python lab9.py cvat` |
| Xem danh sách ảnh | `make samples [SOURCE=bdd100k\|gtsdb\|lisa]` | `python lab9.py samples [--source …]` |
| Gom ảnh một split để upload CVAT | `make pack SPLIT=calibration` | `python lab9.py pack calibration` |
| Đo bất đồng calibration | `make calib FILES="project/06_calibration_exports/an.zip project/06_calibration_exports/binh.zip"` | `python lab9.py calib project/06_calibration_exports/an.zip project/06_calibration_exports/binh.zip` |
| Freeze gold trước handoff | `make freeze` | `python lab9.py freeze` |
| Tạo gói blind cho nhóm peer | `make handoff` | `python lab9.py handoff` |
| Nhận export của peer, lập bảng chấm | `make score FILE=peer.zip` | `python lab9.py score peer.zip` |
| Tính GTS | `make gts` | `python lab9.py gts` |
| Xem gate G1–G6 và việc còn thiếu | `make status` | `python lab9.py status` |
| Kiểm gói nộp cuối | `make check` | `python lab9.py check` |
| (Lab Coach) Kiểm freeze còn nguyên | `make verify` | `python lab9.py verify` |

Tool không bao giờ quyết định label nào đúng. Nó kiểm quy trình (đủ file, freeze còn nguyên, blind không lộ gold) và
tính điểm từ quyết định `correct` do nhóm owner điền.

## Trong repo

| Đường dẫn | Là gì |
|---|---|
| `data/catalog.csv` | Danh sách ảnh: `sample_id`, nguồn, file, thời tiết/giờ/cảnh (BDD) hoặc frame (LISA) |
| `data/bdd100k/BDD01.jpg …` | 26 ảnh BDD100K |
| `data/gtsdb/GTS01 …` | 28 ảnh GTSDB (biển báo Đức, có ảnh không có biển) |
| `data/lisa/LISA01.jpg …` | 30 frame LISA liên tiếp của một clip đèn giao thông ban ngày |
| `project/` | Mọi thứ nhóm nộp. File còn chữ `TODO` là chưa xong |
| `GUIDE.md` | Thao tác CVAT: tạo task, dán Guide, vẽ, export, xem export của peer |
| `RUBRIC.md` | Người chấm nhìn gì, ở file nào |
| `build/`, `handoff/` | Tool sinh ra (ảnh gom theo split, gói blind). Git bỏ qua hai thư mục này |

## Lịch 240 phút

| Phút | Pha | Output | Gate |
|---|---|---|---|
| 0–15 | Briefing + topic lock | `00_team.md`, problem family, cặp peer | |
| 15–35 | Research + downstream contract | `01_problem_statement.md` | **G1** topic lock |
| 35–80 | Guideline v1 + ontology | `02_guideline.md` v1, `03_ontology_and_cvat_setup.md`, kế hoạch edge case | |
| 80–110 | CVAT setup + sample pack | `03_cvat_labels.json`, `sample_pack.csv`, task calibration mở được | **G2** CVAT ready |
| 110–120 | Nghỉ | | |
| 120–140 | Calibration nội bộ | exports, `06_calibration_measure.csv`, `06_calibration_report.csv` | |
| 140–160 | Refine + QA plan + freeze | guideline v2, `05_qa_plan.md`, `gold_decisions.csv`, `make freeze` | **G3** calibration · **G4** gold frozen |
| 160–185 | Blind handoff test (song song hai chiều) | gói blind gửi đi, bài peer nhận về, clarification log | **G5** handoff complete |
| 185–205 | Score + diagnose | `transfer_score.csv`, `make gts`, phân tích nguyên nhân | |
| 205–225 | Final revision | guideline v3, `08_revision_log.md`, edge case ≥ 8 | |
| 225–240 | Nộp + debrief theo cặp | `make check`, push, 2 phút owner/peer mỗi chiều | **G6** final handoff |

Lab Coach đi vòng theo mốc gate và chỉ check **quy trình**, không check "đáp án". `make status` cho biết gate nào xong
và việc đầu tiên còn thiếu.

## 1 · Chọn bài toán (0–35')

Từ "label road elements" thành một production problem đủ hẹp để làm sâu:

| Quá rộng | Đủ cụ thể |
|---|---|
| "Label traffic lights" | Traffic-light state + ego relevance tại giao lộ nhiều đầu đèn |
| "Label lane" | Lane boundary tại merge/split + vạch mờ/tạm thời |
| "Road segmentation" | Drivable area ở vỉa hè / bãi đỗ / lề đường dễ nhầm |
| "Label traffic signs" | Hierarchical sign taxonomy cho biển nhỏ / xa / bị che |

Topic menu chỉ là điểm xuất phát. Chỉ dùng ảnh trong `data/` (license đã kiểm cho lớp học):

| Problem family | Ảnh phù hợp trong `data/` | Lưu ý dữ liệu |
|---|---|---|
| Lane geometry / semantics | `bdd100k` | 26 ảnh, chủ yếu highway và city street ban ngày |
| Drivable area | `bdd100k` | cùng 26 ảnh |
| Traffic light (state, relevance, direction) | `bdd100k` (12 ảnh có đèn, gồm đêm và chạng vạng) + `lisa` | LISA chỉ là **một** clip 30 frame — blind nên lấy ảnh BDD để là cảnh chưa thấy |
| Traffic sign taxonomy | `gtsdb` + `bdd100k` (23 ảnh có biển) | GTSDB là biển Đức; có ảnh không có biển để làm negative |
| Low visibility | `bdd100k` (2 đêm, 2 chạng vạng, 2 tuyết, 1 mưa) | ít ảnh — ghép ảnh ban ngày làm case normal |
| Temporal road elements | `lisa` | 30 frame liên tiếp; khó tạo blind "unseen", ghi rõ giới hạn |
| Construction zone | chưa kiểm có đủ ảnh | chỉ chọn nếu tìm được đủ ≥ 12 ảnh trong `data/` |

`make samples SOURCE=bdd100k` in thời tiết, giờ, cảnh của từng ảnh BDD; mở thư mục `data/…` để xem ảnh.

**Topic approval (G1):** bài toán thuộc Road Elements, có downstream use case rõ, có ambiguity thật, thể hiện được
trong CVAT, và tạo được blind test có expected decision. Viết `01_problem_statement.md` tối đa nửa trang, trả lời đủ
4 câu downstream contract. Nếu contract không rõ, taxonomy sẽ phình to và annotator phải tự đoán.

## 2 · Viết guideline (35–80')

`02_guideline.md` có sẵn 10 mục bắt buộc: objective + scope, annotation unit, geometry rule, taxonomy,
inclusion/exclusion, visibility/occlusion, ambiguity/escalation, temporal rule, examples, common mistakes.

- **No hidden rules:** rule chỉ giải thích bằng miệng thì coi như không tồn tại. Nhóm peer chỉ nhận đúng file này.
- **Class hay attribute:** dùng class khi object type khác nghĩa rõ rệt, downstream cần phân loại trực tiếp, hoặc
  geometry/QA rule khác nhau; dùng attribute khi là thuộc tính của cùng object, có thể đổi theo frame, hoặc tách class
  sẽ nổ ra hàng chục tổ hợp. Ví dụ: `traffic_light` là class; `state`, `relevance`, `direction` hợp lý hơn là attribute.
- **Ontology table** trong `03_ontology_and_cvat_setup.md`: name · geometry · class/attribute · allowed values ·
  default · mutable? · rationale.
- **LABEL / IGNORE / UNKNOWN / ESCALATE:** ghi rõ mỗi quyết định thể hiện trong CVAT bằng cách nào. Quyết định không
  nhìn thấy trong file export thì không chấm được.
- Bắt đầu `04_edge_cases/edge_case_cards.md` ngay từ lúc này: case mà hai annotator hợp lý có thể làm khác nhau.

Khi xong bản nháp đầu, đổi dòng `Version` trong `02_guideline.md` thành `v1`.

## 3 · CVAT setup + sample pack (80–110')

1. Viết `03_cvat_labels.json` theo ontology table — định dạng Raw của CVAT, ví dụ định dạng ở
   [GUIDE mục 2](GUIDE.md#2-tạo-task-calibration).
2. Chia ảnh vào `sample_pack.csv`, mỗi dòng một ảnh:

   | Cột | Giá trị |
   |---|---|
   | `sample_id` | như trong `data/catalog.csv`, ví dụ `BDD07` |
   | `split` | `example` (3–5 ảnh, dùng làm ví dụ trong guideline) · `calibration` (5–8 ảnh) · `blind` (4–5 ảnh chưa ai trong nhóm peer thấy) |
   | `tags` | một hoặc nhiều giá trị, cách nhau bằng `;`: `normal`, `edge`, `critical`, `ambiguity`, `negative`, `occlusion`, `small_far`, `low_visibility`, `temporal`, `conflict` |
   | `reason` | vì sao chọn ảnh này, nó thử rule nào |

   Blind set phải có ít nhất **1 `normal` + 2 `edge` + 1 `critical`**, và **1 `ambiguity`** nếu dùng 5 ảnh. Một ảnh
   chỉ thuộc một split. Rule có thể giống, nhưng cảnh blind phải chưa xuất hiện trong example/calibration (LISA: tool
   cảnh báo frame blind nằm sát frame đã dùng).
3. `make pack SPLIT=calibration` gom ảnh calibration vào `build/calibration/`. Tạo task CVAT từ thư mục đó, dán
   `03_cvat_labels.json` vào tab **Raw**, dán `02_guideline.md` vào **Guide** của task
   ([GUIDE mục 2](GUIDE.md#2-tạo-task-calibration)).
4. **Setup test:** một thành viên chưa setup mở task và phải hiểu ngay label gì, tool nào, attribute nào, khi nào
   escalate. Ghi kết quả vào `03_ontology_and_cvat_setup.md`.

## 4 · Calibration nội bộ (120–140')

1. **Mỗi thành viên** tạo task riêng trên CVAT của mình từ `build/calibration/` (cùng labels JSON, cùng guideline v1)
   và label **độc lập** — không nhìn màn hình nhau, không chốt chung trước.
2. Mỗi người export ([GUIDE mục 4](GUIDE.md#4-export)), đặt tên file theo tên mình, bỏ vào
   `project/06_calibration_exports/` (ví dụ `an.zip`, `binh.zip`).
3. `make calib FILES="project/06_calibration_exports/an.zip project/06_calibration_exports/binh.zip"` →
   `project/06_calibration_measure.csv`: mỗi ảnh × label × phép đo (số object, giá trị attribute, tag) × người label,
   cột `agree`. Lệnh in top chỗ lệch nhiều nhất. Nó chỉ đo **bất đồng**, không nói ai đúng.
4. Chọn ít nhất 3 bất đồng lớn nhất, ghi vào `06_calibration_report.csv`:

   | Cột | Giá trị |
   |---|---|
   | `sample_id`, `item` | ảnh nào, object/attribute nào |
   | `values_by_annotator` | mỗi người làm gì, ví dụ `an=relevant; binh=not_relevant` |
   | `diagnosis` | `guideline_gap` (rule thiếu/mơ hồ) · `data_ambiguity` (ảnh không đủ bằng chứng) · `execution_error` (rule rõ, người làm sai) |
   | `action` | `revise_rule`, `add_example`, `add_escalation`, `coaching`, `no_change` |
   | `rule_change` | rule đổi thế nào và vì sao. Mục tiêu 3 rule change; dòng `execution_error` + `coaching` để trống được (`make status` chỉ chặn khi không dòng nào có) |

Đừng mặc định lỗi nằm ở annotator, và đừng "ép consensus" bằng miệng — biến bất đồng thành rule, exception, escalation
hoặc ví dụ. Không cần mọi người thống nhất 100%. Sửa guideline, đổi `Version` thành `v2`, ghi dòng v2 vào
`08_revision_log.md`.

## 5 · QA plan + gold freeze (140–160')

**QA plan** (`05_qa_plan.md`): ai review, review bao nhiêu, chọn sample theo rule nào, severity
(critical / major / minor / question) theo hậu quả downstream, metric nào, threshold nào PASS / REWORK / REJECT, issue
đóng thế nào, guideline gap thì version ra sao. Threshold là đề xuất của nhóm, không phải chuẩn ngành — giải thích
trade-off.

**Gold decisions** (`04_edge_cases/gold_decisions.csv`) — expected decision cho **từng ảnh blind**, viết trước khi
nhóm peer thấy ảnh:

```csv
sample_id,decision_id,expected,severity,rationale
BDD07,d1,label=traffic_light x2,major,hai đầu đèn nhìn thấy vỏ
BDD07,d2,relevance=not_relevant (đèn trái),critical,đèn điều khiển làn rẽ trái
BDD07,d3,geometry: box ôm vỏ đèn nhìn thấy,minor,theo mục 3 guideline
BDD12,d1,ESCALATE,major,không suy ra được làn nào đèn điều khiển
```

- Tối thiểu **10 decision**, trong đó **≥ 2 `critical`** và **≥ 1 geometry decision** (`expected` bắt đầu bằng
  `geometry:`). Mỗi ảnh blind có ít nhất một decision.
- `expected` viết sao cho người khác nhìn file export của peer là biết đúng hay sai.
- Trước khi freeze, mở từng ảnh blind ở kích thước gốc và quét hết object nhỏ, xa, ban đêm. Decision kiểu "không có
  X" dễ sai nhất: gold bỏ sót một object thì peer vẽ đúng vẫn bị chấm sai.

**Chỉ một người** (người giữ gold) chạy `make freeze`; những người khác đợi người đó push rồi
`git pull && git fetch --tags --force` — hai người cùng freeze sẽ ra hai tag khác nhau. `make freeze` kiểm guideline ≥ v2, labels JSON, sample pack, thành phần blind set và gold; đạt thì ghi
`project/FREEZE.txt` (thời điểm + hash của gold, sample pack, guideline, labels), commit và gắn tag `gold-freeze`.
Push ngay để Lab Coach thấy (`git push --follow-tags`). Sau freeze **không sửa gold và sample pack**. Cần sửa trước khi
gửi blind: `make freeze REFREEZE=1` rồi chạy lệnh push nó in ra (đẩy đè tag) — bị từ chối khi đã nhận bài peer. Sau
mỗi lần refreeze, cả nhóm chạy lại `git pull && git fetch --tags --force` (thiếu `--force`, git giữ tag cũ).

## 6 · Blind handoff test (160–185')

**Owner gửi:** `make handoff` → `handoff/blind-pack.zip` gồm guideline, labels JSON, ảnh blind và hướng dẫn cho
peer. Không có gold, tag hay edge-case card trong gói. Gửi file zip cho nhóm peer qua kênh chia sẻ file Lab Coach công
bố. Guideline phải giữ nguyên từ lúc freeze tới lúc gửi (lệnh từ chối nếu đã sửa).

**Nhóm peer nhận** (15 phút): tạo task CVAT từ `images/` trong gói, dán labels và guideline
([GUIDE mục 5](GUIDE.md#5-làm-peer-tester)), label 4–5 ảnh theo guideline, **không đoán ý owner**. Ghi lại mọi chỗ
phải hỏi hoặc không hiểu. Export, gửi file export + câu trả lời 5 câu feedback cho owner.

**Blind window:** trong 15 phút, owner không giải thích domain rule. Câu hỏi của peer không được trả lời bằng miệng —
mỗi câu là một dòng trong `07_blind_handoff/clarification_log.csv` (`time,asker,question,answered_how,guideline_change`),
và cũng là bằng chứng guideline chưa transferable. Lab Coach chỉ gỡ lỗi CVAT kỹ thuật; lỗi kỹ thuật không ghi vào log.

## 7 · Score + diagnose (185–205')

1. `make score FILE=<export của peer>.zip` chép file vào `07_blind_handoff/peer_output/` và tạo
   `07_blind_handoff/transfer_score.csv`: mỗi gold decision một dòng, cột `peer_evidence` tóm tắt peer đã vẽ gì trên
   ảnh đó.
2. Nhóm owner điền `correct` (`1` / `0`) và `note` cho từng dòng. Geometry decision cần xem hình: mở export của peer
   trong CVAT ([GUIDE mục 6](GUIDE.md#6-xem-export-của-peer)). Chạy lại `make score` không xoá cột đã điền.
   Peer làm đúng guideline nhưng gold sai (owner bỏ sót hoặc chốt nhầm): vẫn chấm `0` theo gold đã freeze, `note` bắt
   đầu bằng `gold sai:` kèm bằng chứng. Không sửa gold sau freeze; `make gts` đếm riêng các dòng này để debrief.
3. `make gts` tính **GTS = 0.60 D + 0.20 C + 0.10 G + 0.10 I** và ghi `07_blind_handoff/gts_summary.md`:
   - **D** decision accuracy — decision không phải geometry đúng / tổng;
   - **C** critical — decision critical đúng / tổng critical (tool đếm critical escape);
   - **G** geometry — geometry decision đúng / tổng;
   - **I** independence — 100 (0 câu hỏi), 70 (1–2), 40 (3–4), 0 (≥ 5).
4. Chép 5 câu trả lời của peer vào `07_blind_handoff/peer_feedback.md`, rồi phân loại từng feedback và từng decision
   sai: guideline gap / data ambiguity / execution error → accept + revise / reject with evidence / add escalation rule.

GTS đo **độ chuyển giao được của specification**, không đo năng lực của peer. Peer sai thì owner phân tích nguyên
nhân bằng bằng chứng, không đổ lỗi. Nhóm peer xem `transfer_score.csv` trong debrief; chỗ không đồng ý ghi vào `note`.

## 8 · Final revision + nộp (205–240')

- Guideline `v3` từ bằng chứng blind test; dòng v3 trong `08_revision_log.md`.
- `edge_case_cards.md` đủ ≥ 8 card, có case critical và case escalation.
- `09_cvat_export_or_task_reference.txt` điền đủ.
- `make check` phải báo đủ 6 gate. Rồi commit và push:

```bash
git add project
git commit -m "Day 9 project submission"
git push --follow-tags
```

Debrief theo cặp: mỗi chiều 2 phút — owner nói guideline vỡ ở đâu và đã sửa gì, peer nói chỗ khó nhất.

**5 câu tự kiểm trước khi nộp:** annotator mới có biết label gì / không label gì mà không cần hỏi? Gặp edge case chưa
thấy, guideline có giúp họ quyết định hoặc escalate? CVAT schema có phản ánh đúng ontology hay đang tạo default sai?
QA plan có bắt được lỗi quan trọng bằng metric/threshold cụ thể? Blind test cho thấy guideline transferable tới đâu,
và nhóm đã sửa gì từ bằng chứng đó?

## Làm chung một repo

- Mỗi file một người sửa chính (`00_team.md` có cột "File phụ trách"). `git pull` trước khi sửa, commit nhỏ, push
  thường xuyên.
- Xung đột git mà không tự gỡ được trong 3 phút: gọi Lab Coach.
- Nhóm xong sớm: tối đa 1–2 stretch, không hy sinh phần core — ví dụ validator nhỏ bắt tổ hợp attribute sai, QA
  sampling theo rủi ro, decision tree cho một ambiguity khó, so guideline với một public dataset. Tool mới hay
  dashboard đẹp không bù được một guideline không dùng được.

## Khi bị kẹt

1. Tra [GUIDE mục 7](GUIDE.md#7-khi-lệnh-báo-lỗi): bảng thông báo lỗi và cách xử lý.
2. Kẹt kỹ thuật (CVAT, Docker, git, lệnh) quá 3 phút: giơ tay gọi Lab Coach.
3. Kẹt domain ("cái này có phải lane không?"): quyết định của nhóm, ghi thành rule, UNKNOWN hoặc ESCALATE trong
   guideline. Lab Coach không trả lời thay.

## Luật của buổi

- Không sửa gold hay sample pack sau freeze. Không cho nhóm peer xem gold, tag hay edge-case card trước khi test xong.
- Không giải thích rule bằng miệng trong blind window. Log câu hỏi trung thực — Lab Coach ghi nhận nếu blind protocol
  bị phá.
- Ảnh là dữ liệu dataset công khai, chỉ dùng cho học tập phi thương mại (xem `ATTRIBUTION.txt`). Giữ nguyên
  `ATTRIBUTION.txt` trong repo; không dùng ảnh ngoài `data/`.
