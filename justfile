init:
    if [ ! -f requirements.lock ]; then rye sync; fi
    rye run pre-commit install
    docker build -t isat-base:latest . && docker-compose build

start:
    docker-compose up

stop:
    docker-compose down