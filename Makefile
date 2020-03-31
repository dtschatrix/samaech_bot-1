run:
	DOCKER_BUILDKIT=1 docker build ./src/ -t samaech-bot && docker run -it --name samaech-bot --rm --env-file=.env samaech-bot:latest /bin/bash

rund:
	DOCKER_BUILDKIT=1 docker build ./src/ -t samaech-bot && docker run -d --name samaech-bot --env-file=.env samaech-bot:latest

