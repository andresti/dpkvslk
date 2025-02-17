.PHONY: build start stop clean download_model

# Default model - you can override this with environment variable
MODEL_NAME ?= phi-2.Q4_K_M.gguf
MODEL_URL ?= https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/$(MODEL_NAME)

build: download_model
	docker compose build

up: build
	docker compose up

stop:
	docker compose down

clean:
	docker compose down -v
	rm -rf uploads/*
	rm -rf models/*

download_model:
	@echo "Downloading $(MODEL_NAME)..."
	@mkdir -p models
	@if [ ! -f "models/$(MODEL_NAME)" ]; then \
		wget -P models $(MODEL_URL); \
	else \
		echo "Model already exists in models/"; \
	fi

setup: download_model build
