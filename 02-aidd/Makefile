.PHONY: sync run docker-build docker-run

sync:
	uv sync

run:
	uv run python -m assistant.main

docker-build:
	docker build -t assistant .

docker-run:
	docker run --rm --env-file .env assistant
