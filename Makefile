#!make
include .env.example
export


profile.tests:
	docker compose --file docker-compose.profile-tests.yml up --build --force-recreate

profile.tests.down:
	docker compose --file docker-compose.profile-tests.yml down

logs.movies:
	docker compose --file docker-compose.profile-tests.yml logs movies-api

logs.es:
	docker compose --file docker-compose.profile-tests.yml logs elasticsearch
