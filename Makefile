DOCKER_IMAGE_VERSION?=latest
DOCKER_IMAGE_TAG?=a2c-bivhack-1:${DOCKER_IMAGE_VERSION}

DATA_DIR?=./data
INPUT_TSV?=sample.tsv
OUTPUT_TSV?=out.tsv

.PHONY: all
all: build run

.PHONY: build
build:
	docker build -t ${DOCKER_IMAGE_TAG} .

.PHONY: run
run:
	docker run -v ${DATA_DIR}:/data ${DOCKER_IMAGE_TAG} \
		/data/${INPUT_TSV} \
		/data/${OUTPUT_TSV}
