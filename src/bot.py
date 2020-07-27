import os
import random
from datetime import datetime
from time import sleep
from uuid import uuid4

from py_2ch_api.client import ChAPI
from py_2ch_api.constants import FILE_TYPE, MEDIA_TYPE
from py_2ch_api.models import Thread
from pyrogram import (
    Client,
    Message,
    Filters,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram.errors import MediaEmpty

from constants import constants
from middlewares.middlewares import is_chat_allowed, admin_only
from utils.Google import (
    GoogleAPI,
    SEARCH_TYPE,
    GoogleImageResponse,
    GoogleResponse,
)
from utils.GreenText import GreenTextImage
from utils.SteamStats import SteamStatsAPI
from utils.YouTube import YouTubeAPI
from utils.common import Common

VERSION = "0.0.5"
BOT_NAME = os.environ.get("BOT_NAME", "Валентин")

app = Client(
    ":memory:",
    os.getenv("API_ID"),
    os.getenv("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN"),
    workers=10,
).start()

bot_username = app.get_me()["username"]


@app.on_message(Filters.command(["ver", f"ver@{bot_username}"]))
@admin_only
def start(client: Client, message: Message) -> None:
    reply_message = message.reply_text(VERSION)
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


@app.on_message(Filters.command(["dotathread", f"dotathread@{bot_username}"]))
def get_last_dotathread_link(client: Client, message: Message) -> Thread:
    with ChAPI(board="vg") as ch:
        threads = ch.get_board_threads(tag="dota")

        if threads:
            thread = threads[0]
            thread_url = f"https://2ch.hk/vg/res/{thread.num}.html"
            buttons = [[InlineKeyboardButton(text="thread", url=thread_url)]]

            client.send_photo(
                message.chat.id,
                ch.build_url(thread.opening_post.files[0].path),
                caption=thread.opening_post.comment,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML",
            )
            return thread


@app.on_message(
    Filters.command(
        [
            "lastpost",
            "randpost",
            f"lastpost@{bot_username}",
            f"randpost@{bot_username}",
        ]
    )
)
def get_post_from_dotathread(client: Client, message: Message):
    command = message.command[0]

    with ChAPI(board="vg") as ch:
        threads = ch.get_board_threads(tag="dota")

        if threads:
            thread = threads[0]
            posts = ch.get_thread(thread=thread)

            if command == "lastpost" or command == f"lastpost@{bot_username}":
                post_data = posts[-1]
            if command == "randpost" or command == f"randpost@{bot_username}":
                post_data = random.choice(posts)

            comment = post_data.comment.replace("<br>", "\n")

            if post_data.files:
                content = post_data.files[0]
                content_type = FILE_TYPE().get(content.type)
                content_url = ch.build_url(content.path)
                try:
                    if (
                        content_type == MEDIA_TYPE.JPEG
                        or content_type == MEDIA_TYPE.PNG
                    ):
                        return client.send_photo(
                            message.chat.id, content_url, caption=comment,
                        )

                    if content_type == MEDIA_TYPE.MP4:
                        return client.send_video(
                            message.chat.id,
                            content_url,
                            caption=comment,
                            parse_mode="html",
                        )
                except MediaEmpty:
                    return client.send_message(
                        message.chat.id, comment, parse_mode="html"
                    )

        return client.send_message(message.chat.id, comment, parse_mode="html")


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


@app.on_message(
    Filters.command(
        [
            "steamstats",
            "steamstat",
            f"steamstats@{bot_username}",
            f"steamstat@{bot_username}",
        ]
    )
)
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


@app.on_message(
    Filters.command(["t", "w", f"t@{bot_username}", f"w@{bot_username}"])
)
@is_chat_allowed
def get_random_video_from_2ch(client: Client, message: Message) -> None:
    command = message.command[0]

    try:
        with ChAPI(board="b") as ch:

            if command == "t" or command == f"t@{bot_username}":
                threads = ch.get_board_threads(subject="tik tok")
            elif command == "w" or command == f"w@{bot_username}":
                threads = ch.get_board_threads(subject="webm")

            if threads:

                thread = threads[0]
                media = ch.get_all_media_from_thread(
                    thread=thread, media_type=MEDIA_TYPE.MP4
                )

                if media:
                    random.seed(datetime.now())

                    result = random.choice(media)

                    client.send_video(
                        message.chat.id, ch.build_url(result.path)
                    )
    except:
        get_random_video_from_2ch(client, message)


@app.on_message(Filters.regex("^>[а-яА-Яa-zA-Z0-9\sёъїі]+"))
def text_to_greentext_picture(client: Client, message: Message):
    GTI = GreenTextImage(
        sender=message.from_user.first_name, text=message.text
    )

    outfile = f"{uuid4()}.png"
    image = GTI.create_image()
    image.save(outfile)

    # send as byte sequence?
    # imgByte = io.BytesIO()
    # image.save(imgByte, format='PNG')
    # imgByte = imgByte.getvalue()

    client.send_photo(message.chat.id, photo=outfile)

    os.remove(outfile)
