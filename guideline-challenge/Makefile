PYTHON ?= python3
SOURCE ?=
SPLIT ?=
FILES ?=
FILE ?=

.PHONY: help samples pack calib freeze verify handoff score gts status check cvat-status

help:
	@echo "Day 9 · Guideline Design Challenge — lệnh học viên"
	@echo "  make samples [SOURCE=bdd100k|gtsdb|lisa]   Xem catalog sample"
	@echo "  make pack SPLIT=calibration               Dựng ảnh upload CVAT"
	@echo "  make calib FILES=\"project/06_calibration_exports/an.zip project/06_calibration_exports/binh.zip\""
	@echo "                                            Đo bất đồng calibration"
	@echo "  make freeze [REFREEZE=1]                  Freeze gold trước blind test"
	@echo "  make verify                               Kiểm freeze chưa bị sửa"
	@echo "  make handoff                              Tạo handoff/blind-pack.zip"
	@echo "  make score FILE=peer.zip                  Tạo bảng owner nhập correct"
	@echo "  make gts                                  Tính transferability score"
	@echo "  make status                               Xem gate G1–G6"
	@echo "  make check                                Kiểm đủ cả sáu gate"
	@echo "  make cvat-status                          Kiểm CVAT đang chạy"

samples:
	$(PYTHON) lab9.py samples $(if $(SOURCE),--source "$(SOURCE)",)

pack:
	@test -n "$(SPLIT)" || { echo "✗ Thiếu SPLIT — ví dụ: make pack SPLIT=calibration" >&2; exit 2; }
	$(PYTHON) lab9.py pack "$(SPLIT)"

calib:
	@test -n "$(FILES)" || { echo "✗ Thiếu FILES — ví dụ: make calib FILES=\"project/06_calibration_exports/an.zip project/06_calibration_exports/binh.zip\"" >&2; exit 2; }
	$(PYTHON) lab9.py calib $(FILES)

freeze:
	$(PYTHON) lab9.py freeze $(if $(filter 1,$(REFREEZE)),--refreeze,)

verify:
	$(PYTHON) lab9.py verify

handoff:
	$(PYTHON) lab9.py handoff

score:
	@test -n "$(FILE)" || { echo "✗ Thiếu FILE — ví dụ: make score FILE=peer.zip" >&2; exit 2; }
	$(PYTHON) lab9.py score "$(FILE)"

gts:
	$(PYTHON) lab9.py gts

status:
	$(PYTHON) lab9.py status

check:
	$(PYTHON) lab9.py check

cvat-status:
	$(PYTHON) lab9.py cvat
