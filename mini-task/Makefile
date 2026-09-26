PYTHON ?= python3
TASK ?=
FILE ?=
CODE ?=
NAME ?=
MEMBERS ?=

.PHONY: help lock reference peer team compare status check cvat-status

help:
	@echo "Day 9 Lab — lệnh học viên"
	@echo "  make lock TASK=lane FILE=export.zip [RELOCK=1]"
	@echo "  make reference TASK=lane [FILE=reference.zip]"
	@echo "  make peer TASK=lane FILE=annotations.xml CODE=XXXX-XXXX NAME=An"
	@echo "  make team [MEMBERS=\"An, Bình\"]"
	@echo "  make compare TASK=lane"
	@echo "  make status"
	@echo "  make check"
	@echo "  make cvat-status   Kiểm CVAT đã cài ở Day 2/Day 8 đang chạy"

lock:
	@test -n "$(TASK)" || { echo "✗ Thiếu TASK — ví dụ: make lock TASK=lane FILE=export.zip" >&2; exit 2; }
	@test -n "$(FILE)" || { echo "✗ Thiếu FILE — ví dụ: make lock TASK=lane FILE=export.zip" >&2; exit 2; }
	$(PYTHON) lab9.py lock $(TASK) "$(FILE)" $(if $(filter 1,$(RELOCK)),--relock,)

reference:
	@test -n "$(TASK)" || { echo "✗ Thiếu TASK — ví dụ: make reference TASK=lane" >&2; exit 2; }
	$(PYTHON) lab9.py reference $(TASK) $(if $(FILE),--file "$(FILE)",)

peer:
	@test -n "$(TASK)" || { echo "✗ Thiếu TASK — ví dụ: make peer TASK=lane FILE=annotations.xml CODE=XXXX-XXXX NAME=An" >&2; exit 2; }
	@test -n "$(FILE)" || { echo "✗ Thiếu FILE — chọn annotations.xml của bạn cùng nhóm" >&2; exit 2; }
	@test -n "$(CODE)" || { echo "✗ Thiếu CODE — nhập mã khoá của file bạn cùng nhóm" >&2; exit 2; }
	@test -n "$(NAME)" || { echo "✗ Thiếu NAME — nhập tên bạn cùng nhóm" >&2; exit 2; }
	$(PYTHON) lab9.py peer $(TASK) --file "$(FILE)" --code "$(CODE)" --name "$(NAME)"

team:
	$(PYTHON) lab9.py team $(if $(MEMBERS),--members "$(MEMBERS)",)

compare:
	@test -n "$(TASK)" || { echo "✗ Thiếu TASK — ví dụ: make compare TASK=lane" >&2; exit 2; }
	$(PYTHON) lab9.py compare $(TASK)

status:
	$(PYTHON) lab9.py status

check:
	$(PYTHON) lab9.py check

cvat-status:
	$(PYTHON) lab9.py cvat
