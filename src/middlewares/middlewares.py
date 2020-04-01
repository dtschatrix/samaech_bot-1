import functools
import os

from pyrogram import Client, Message


def is_chat_allowed(func):

    # do not use hardcoded values
    allowed_chats = (
        int(os.getenv("ADMIN_ID")),
        -1001141653473,
    )

    @functools.wraps(func)
    def inner(client: Client, message: Message, *args, **kwargs):
        if message.chat.id in allowed_chats:
            return func(client, message, *args, **kwargs)

    return inner


def admin_only(func):
    @functools.wraps(func)
    def inner(client: Client, message: Message, *args, **kwargs):
        if message.chat.id == int(os.getenv("ADMIN_ID")):
            return func(client, message, *args, **kwargs)

    return inner
