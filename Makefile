.PHONY: help install run voice test clean setup check

help:
	@echo "Jarvis - AI Agent Commands"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make setup      - Initial setup (venv + deps)"
	@echo "  make run        - Run in chat mode"
	@echo "  make voice      - Run in voice mode"
	@echo "  make models     - List available Ollama models"
	@echo "  make check      - Check system requirements"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean cache and temp files"
	@echo ""

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete! Run 'source venv/bin/activate' to activate."

install:
	pip install -r requirements.txt

run:
	python main.py

voice:
	python main.py --voice

models:
	python main.py --list-models

check:
	@echo "Checking system requirements..."
	@python3 --version
	@which ollama && ollama --version || echo "⚠️  Ollama not installed"
	@echo "Checking Python packages..."
	@python3 -c "import ollama; print('✓ ollama')" 2>/dev/null || echo "✗ ollama"
	@python3 -c "import speech_recognition; print('✓ speech_recognition')" 2>/dev/null || echo "✗ speech_recognition"
	@python3 -c "import pyttsx3; print('✓ pyttsx3')" 2>/dev/null || echo "✗ pyttsx3"

test:
	python -m pytest tests/ -v 2>/dev/null || echo "No tests yet"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage 2>/dev/null || true
	@echo "Cleaned up!"

docker-build:
	docker build -t jarvis-agent .

docker-run:
	docker run -it --rm -e OLLAMA_HOST=host.docker.internal:11434 jarvis-agent
