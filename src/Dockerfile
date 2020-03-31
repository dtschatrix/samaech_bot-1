# syntax = docker/dockerfile:experimental

FROM python:3.7

RUN --mount=target=/samaech_bot,type=bind,rw,source=. cd /samaech_bot      && \
    pip install -r /samaech_bot/requirements.txt                           && \
    mkdir /app_bin && cp -r /samaech_bot/* /app_bin/                       && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app_bin

CMD python bot.py