#!/bin/bash

docker container stop samaech-bot
docker container rm samaech-bot
docker build -t samaech-bot .
docker run -it -d --env-file .env --name samaech-bot samaech-bot:latest
