# Repo có hai bài độc lập; mọi lệnh của bài chạy trong thư mục bài.
.PHONY: help

help:
	@echo "Repo có hai bài lab Day 9. Vào thư mục bài Lab Coach giao rồi chạy make help:"
	@echo "  cd mini-task && make help            4 mini-task gắn nhãn, tự đối chiếu reference"
	@echo "  cd guideline-challenge && make help  Guideline Design Challenge theo nhóm"

.DEFAULT:
	@echo "✗ 'make $@' chạy trong thư mục bài: cd mini-task hoặc cd guideline-challenge, rồi chạy lại." >&2
	@exit 2
