from datetime import datetime
from time import sleep
import random
from pyrogram import (
    Client,
    Message,
    Filters,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import os
from constants import constants
from utils.common import Common
from utils.Google import (
    GoogleAPI,
    SEARCH_TYPE,
    GoogleImageResponse,
    GoogleResponse,
)
from utils.YouTube import YouTubeAPI
from utils.Dvach import DvachAPI, POST_OFFSET
from utils.SteamStats import SteamStatsAPI

from middlewares.middlewares import is_chat_allowed, admin_only

VERSION = "0.0.3"
BOT_NAME = os.getenv("BOT_NAME") or "Валентин"

app = Client(
    ":memory:",
    os.getenv("API_ID"),
    os.getenv("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN"),
    workers=10,
)


@app.on_message(Filters.command("ver"))
@admin_only
def start(client: Client, message: Message) -> None:
    reply_message = message.reply_text(VERSION, message.chat.id)
    sleep(2)
    client.delete_messages(
        message.chat.id, [message.message_id, reply_message.message_id]
    )


@app.on_message(
    Filters.regex(pattern=r"(?i)^(ору[\s]|jhe)|[\s]ору[\s]|орунах")
)
def rofl_handler(client: Client, message: Message) -> None:
    client.send_sticker(
        message.chat.id, random.choice(constants.ROFL_STICKERS)
    )


@app.on_message(Filters.command(["g", "gi", "p"]))
@is_chat_allowed
def google(client: Client, message: Message) -> None:
    query = " ".join(message.command[1:])
    command = message.command[0]

    with GoogleAPI() as g_client:
        if command == "g":
            response: GoogleResponse = g_client.search(
                query, search_type=SEARCH_TYPE.TEXT
            )
            if response:
                client.send_chat_action(message.chat.id, "typing")
                client.send_message(
                    message.chat.id,
                    f"<b>{response.title}</b>\n\n{response.snippet}\n\n{response.url}",
                    parse_mode="HTML",
                )
            else:
                Common.send_not_found_message(message)

        if command == "gi" or command == "p":
            response: GoogleImageResponse = g_client.search(
                query, search_type=SEARCH_TYPE.IMAGE
            )

            if response:
                client.send_chat_action(message.chat.id, "upload_photo")
                client.send_photo(
                    message.chat.id,
                    response.url,
                    caption=f"<i>{response.snippet}</i>\n\n{response.source_url}",
                    parse_mode="HTML",
                )
            else:
                Common.send_not_found_message(message)


@app.on_message(Filters.command(["y"]))
@is_chat_allowed
def youtube(client: Client, message: Message) -> None:
    query = " ".join(message.command[1:])

    with YouTubeAPI() as y_client:
        response = y_client.search(query)

        if response:
            client.send_chat_action(message.chat.id, "typing")
            result = f'<b><a href="{response.url}">{response.title}</a></b>'
            client.send_message(message.chat.id, result, parse_mode="HTML")
        else:
            Common.send_not_found_message(message)


@app.on_message(Filters.command("dotathread"))
def get_last_dotathread_link(client: Client, message: Message) -> None:
    # TODO add get latest thread by tags
    with DvachAPI() as ch_client:
        thread = ch_client.get_thread("vg", "dota2")

        if thread:
            buttons = [[InlineKeyboardButton(text="thread", url=thread.url)]]

            client.send_photo(
                message.chat.id,
                thread.image,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            Common.send_not_found_message(message)


@app.on_message(Filters.command(["lastpost", "randpost"]))
def get_post_from_dotathread(client: Client, message: Message):
    command = message.command[0]

    with DvachAPI() as ch_client:
        thread = ch_client.get_thread("vg", "dota2")

        if command == "lastpost":
            post_data = ch_client.get_post(
                thread_id=thread.id, board="vg", offset=POST_OFFSET.LAST
            )

        if command == "randpost":
            post_data = ch_client.get_post(
                thread_id=thread.id, board="vg", offset=POST_OFFSET.RANDOM
            )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Go to message!", url=post_data.message_link
                    )
                ]
            ]
        )

        if post_data.images:
            content = post_data.images[0]
            content_ext = content.split(".")[-1]

            if content_ext == "jpg" or content_ext == "png":
                return message.reply_photo(
                    content, caption=post_data.message, reply_markup=buttons
                )

            if content_ext == "mp4":
                return message.reply_video(
                    content, caption=post_data.message, reply_markup=buttons
                )
        return message.reply_text(post_data.message, reply_markup=buttons)


@app.on_message(
    Filters.regex(
        pattern=f"(?i)^{BOT_NAME}(,|\s)(\s|)(.*\S.*)\sили\s(.*\S.*)\?"
    )
)
def fate_decision_or(client: Client, message: Message) -> None:
    random.seed(datetime.now())
    _message = message.text.replace("?", "").split()
    message.reply_text(
        f"{random.choice(constants.FIRST_WORD)}{random.choice([_message[1], _message[-1]])}."
    )


@app.on_message(
    Filters.regex(f"(?i)^{BOT_NAME}(,|\s)(\s|)(.*\S.*)\sли\s(.*\S.*)\?")
)
def fate_question(client: Client, message: Message) -> None:
    _message = " ".join(
        Common.pronoun_replace(message.text).replace("?", "").split()[1:]
    )

    random.seed(datetime.now())

    correct_answer = f"{_message.split('ли')[1]} {_message.split('ли')[0]}"
    incorrect_answer = random.choice(("Нет.", "Ни в коем случае."))

    message.reply_text(random.choice((correct_answer, incorrect_answer)))


@app.on_message(Filters.command(["steamstats", "steamstat"]))
def steamstats(client: Client, message: Message):
    query = " ".join(message.command[1:]) if len(message.command) > 1 else None

    with SteamStatsAPI() as steam_client:
        if query:
            result = steam_client.get_online_status(query)
        else:
            result = steam_client.get_online_status()

        if result:
            return client.send_message(
                message.chat.id,
                f"<b>{result.service}</b>: <code>{result.status}</code>",
                parse_mode="HTML",
            )

    return Common.send_not_found_message(message)


@app.on_message(Filters.command(["v"]))
@is_chat_allowed
def get_random_video_from_2ch(client: Client, message: Message) -> None:
    with DvachAPI() as dvch:
        try:
            thread = dvch.get_thread(board="b", subject="tik tok")

            if not thread:
                thread = dvch.get_thread(board="b", subject="webm")

            post_data = dvch.get_random_mp4_post(
                thread_id=thread.id, board="b"
            )

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Go to message!", url=post_data.message_link
                        )
                    ]
                ]
            )

            message.reply_video(
                post_data.images[0],
                caption=post_data.message,
                reply_markup=buttons,
            )
        except:
            get_random_video_from_2ch(client, message)


if __name__ == "__main__":
    app.run()
