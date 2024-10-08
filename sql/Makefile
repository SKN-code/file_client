.PHONY: run stop

run:
	docker compose down && docker compose up -d && docker compose logs -f

stop:
	docker compose stop && docker compose down