IMAGE=ampla-b2mml
TAG=latest

build:
	docker build -t $(IMAGE):$(TAG) .

run:
	docker run --rm -p 8000:8000 $(IMAGE):$(TAG)

up:
	docker-compose up --build

down:
	docker-compose down
