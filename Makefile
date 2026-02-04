PYTHON ?= python3

.PHONY: setup test run-bot run-webhook set-webhook

setup:
	uv sync --dev

test:
	uv run pytest

run-bot:
	uv run python telegram_bot.py

run-webhook:
	uv run uvicorn telegram_webhook:app --host 0.0.0.0 --port 8000

set-webhook:
	uv run python -c "from telegram_webhook import set_webhook; set_webhook()"
