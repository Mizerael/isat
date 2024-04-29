# isat-ssu

just:

```sh
just init
just start
just stop
```

или:

```sh
rye sync
rye run pre-commit install
docker build -t isat-base:latest . && docker-compose build
```
и 
```sh
docker-compose up
docker-compose down
```