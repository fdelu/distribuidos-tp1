SHELL := /bin/bash
DATASET_ID := 190kC3LtexSWKDIYS1IbAoCnrP9oHeE9j
DATASET_HASH := 8b80b71965721392857021c74bba58c6
DATASET_FILE := client/dataset.zip
SED_EXPR := s/^.*<form[^>]\+\?action=\"\([^\"]\+\?\)\"[^>]*\?>.*\$$/\1/p
default: docker-compose-up

get-dataset:
	HASH=$$([ -f ${DATASET_FILE} ] && (md5sum ${DATASET_FILE} | head -c 32) || ""); \
	if [ "$${HASH}" == "${DATASET_HASH}" ]; then \
		echo "Dataset already downloaded"; \
	else \
		if [ -z "$${HASH}" ]; then \
			echo "Dataset is not present, downloading..."; \
		else \
			echo "Dataset hash does not match (actual: '$${HASH}', expected: '${DATASET_HASH}')"; \
			echo "Re-downloading dataset..."; \
		fi; \
		wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=${DATASET_ID}' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=${DATASET_ID}" -O ${DATASET_FILE} && rm -rf /tmp/cookies.txt; \
	fi;
# The wget downloads from Google Drive. Source: https://superuser.com/a/1542118

	unzip -n ${DATASET_FILE} -d client/data

build: get-dataset
	docker compose build

docker-compose-up: build
	docker compose up -d --build

docker-compose-stop:
	docker compose stop -t 1

docker-compose-down: docker-compose-stop
	docker compose down

docker-compose-logs:
	docker compose logs -f

debug: docker-compose-down docker-compose-up docker-compose-logs

.PHONY: get-dataset build docker-compose-stop docker-compose-down -docker-compose-logs debug
.SILENT: get-dataset build docker-compose-stop docker-compose-down -docker-compose-logs debug