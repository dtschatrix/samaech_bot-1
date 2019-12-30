import logging
import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BadRequest
from aiogram.utils import executor

from utils import DvachUtils, GoogleUtils, YoutubeUtils

TOKEN = os.getenv("BOT_TOKEN")
VERSION = "0.0.2"
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else 0

BOT_NAME = "Валентин"
first_word = ("Я думаю, ", "", "Наверное, ", "Базарю, ", "Возможно, ", "Конечно же, ")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

google_api = GoogleUtils()
youtube_api = YoutubeUtils()
dvach_api = DvachUtils()

stickers = [
    "CAADAgADHgADybg6G8cUXx1GrTg8FgQ",
    "CAADAgADkAEAAuaV7QYOHYd-PBwUiRYE",
    "CAADAgADQAIAAuaV7QaT-yoFW4mwjRYE",
]


async def not_found(message: types.Message) -> None:
    await types.ChatActions.typing()

    await message.reply_photo(types.InputFile("content/img/not-found.png"), caption="Я ничего не нашел.")


async def empty_query(message: types.Message) -> None:
    await bot.send_photo(
        message.chat.id,
        types.InputFile("content/img/empty-query.png"),
        caption="А запрос мне самому придумать?",
        reply_to_message_id=message.message_id,
    )


@dp.message_handler(regexp="^(ору[\s]|jhe)|[\s]ору[\s]|орунах")
async def rofl_handler(message: types.Message) -> None:
    await bot.send_sticker(message.chat.id, sticker=random.choice(stickers))


@dp.message_handler(content_types=["voice"])
async def voice_recognition(message: types.Message):
    await types.ChatActions.typing()

    await message.reply("Not Implemented Yet")


@dp.message_handler(commands=["ver"], user_id=ADMIN_ID)
async def version(message: types.Message):
    await types.ChatActions.typing()
    await message.reply(f"<b>Version: {VERSION}</b>", parse_mode="HTML")


@dp.message_handler(commands=["g", "gi", "p"], chat_id=-1001141653473)
async def google(message: types.Message):
    """
    Google Search
    """
    query = google_api.prepare_query(message)
    command = message.text.split()[0]

    if query:

        if command == "/g":

            response = await google_api.search(query)

            if response.code != 404:
                await types.ChatActions.typing()

                result = f"<b>{response.title}</b>\n\n<i>{response.snippet}</i>"

                keys = types.InlineKeyboardMarkup()
                keys.add(types.InlineKeyboardButton("Source Link", url=response.link))

                return await message.reply(result, parse_mode="HTML", reply_markup=keys)
            else:
                return await not_found(message)

        if command in ["/gi", "/p"]:
            response = await google_api.search(query, search_type="image")

            if response.code != 404:
                try:
                    await types.ChatActions.typing()

                    caption = f"<i>{response.snippet}</i>"

                    keys = types.InlineKeyboardMarkup()
                    keys.add(types.InlineKeyboardButton("Source Link", url=response.context_link))

                    return await message.reply_photo(
                        photo=response.link, caption=caption, parse_mode="HTML", reply_markup=keys,
                    )
                except BadRequest:
                    await types.ChatActions.typing()

                    await message.reply("Ой! Какая-то неправильная картинка пришла. Попробуй еще раз.")

            else:
                await types.ChatActions.typing()

                return await not_found(message)

    return await empty_query(message)


@dp.message_handler(commands=["y"], chat_id=-1001141653473)
async def youtube(message: types.Message):
    """
    YouTube Search
    """
    query = google_api.prepare_query(message)

    if query:
        response = await youtube_api.search(query)

        if response.code != 404:
            await types.ChatActions.typing()
            result = f'<a href="{response.link}">{response.title}</a>\n\n<i>{response.description}</i>'
            keys = types.InlineKeyboardMarkup()
            keys.add(types.InlineKeyboardButton("Open in YouTube", url=response.link))
            return await message.reply(result, parse_mode="HTML", reply_markup=keys)

        else:
            await types.ChatActions.typing()

            return await not_found(message)

    return await empty_query(message)


@dp.message_handler(commands=["thread"])
async def get_last_dotathread(message: types.Message):
    thread = await dvach_api.get_thread("vg", "dota2")

    keys = types.InlineKeyboardMarkup()
    keys.add(types.InlineKeyboardButton("Go to thread!", url=thread.link))

    return await message.reply_photo(
        thread.image if "https" in thread.image else types.InputFile(thread.image), reply_markup=keys,
    )


@dp.message_handler(commands=["randpost", "lastpost"])
async def get_post_from_dotathread(message: types.Message):
    command = message.text.split()[0]
    thread = await dvach_api.get_thread("vg", "dota2")
    post_data = None

    if command == "/randpost" or command == "/randpost@samaech_bot":
        post_data = await dvach_api.get_post(thread_id=thread.thread_id)

    elif command == "/lastpost" or command == "/lastpost@samaech_bot":
        post_data = await dvach_api.get_post(thread_id=thread.thread_id, offset="last")

    keys = types.InlineKeyboardMarkup()
    keys.add(types.InlineKeyboardButton("Go to message!", url=post_data.message_link))

    if post_data.images:
        content = post_data.images[0]
        content_extension = content.split(".")[-1]

        if content_extension == "jpg" or content_extension == "png":
            return await message.reply_photo(content, caption=post_data.message, reply_markup=keys)

        if content_extension == "mp4":
            return await message.reply_video(content, caption=post_data.message, reply_markup=keys)

    return await message.reply(post_data.message, reply_markup=keys)


@dp.message_handler(regexp=rf"{BOT_NAME}, (.*\S.*) или (.*\S.*)\?")
async def fate_decision_or(message: types.Message):
    _message = message.text[len(BOT_NAME) + 2 : -1]
    return await message.reply(f"{random.choice(first_word)}{random.choice(_message.split(' или '))}.")


@dp.message_handler(regexp=rf"{BOT_NAME}, (.*\S.*) ли (.*\S.*)\?")
async def fate_decision(message: types.Message):
    _message = message.text[len(BOT_NAME) + 2 : -1]

    correct_answer = f"{random.choice(first_word)}{_message.split(' ли ')[1]} {_message.split(' ли ')[0]}."
    incorrect_answer = random.choice(("Нет.", "Ни в коем случае."))

    return await message.reply(random.choice([correct_answer, incorrect_answer]))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
