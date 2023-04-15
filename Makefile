SHELL := /bin/bash
PWD := $(shell pwd)

default: build

all:

build:
	unzip -n client/dataset.zip -d client/data
	docker compose build
.PHONY: build

docker-compose-up: build
	docker compose up -d --build
.PHONY: docker-compose-up

docker-compose-stop:
	docker compose stop -t 1
.PHONY: docker-compose-down

docker-compose-down: docker-compose-stop
	docker compose down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose logs -f
.PHONY: docker-compose-logs

debug: docker-compose-down docker-compose-up docker-compose-logs
.PHONY: debug