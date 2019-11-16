# RUN

## .env file

Create and fill `.env` file with variables:

```
BOT_TOKEN=bot-token

GOOGLE_API_KEY=google-api-key
GOOGLE_CX=google-cx-key

ADMIN_ID=admin-chat-id
```

## BUILD

`docker build -t samaech-bot .`

## RUN

`docker run -it --rm --env-file .env --name samaech-bot samaech-bot:latest`
