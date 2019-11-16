import logging
import os

from aiogram import Bot, Dispatcher, executor, types

from aiogram.utils.exceptions import BadRequest


from utils import GoogleUtils, YoutubeUtils

TOKEN = os.getenv("BOT_TOKEN")
VERSION = "0.0.1"
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else 0

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
google_api = GoogleUtils()
youtube_api = YoutubeUtils()


async def not_found(message: types.Message) -> None:
    await types.ChatActions.typing()

    await message.reply_photo(
        types.InputFile("content/img/not-found.png"), caption="Я ничего не нашел."
    )


async def empty_query(message: types.Message) -> None:
    await bot.send_photo(
        message.chat.id,
        types.InputFile("content/img/empty-query.png"),
        caption="А запрос мне самому придумать?",
        reply_to_message_id=message.message_id,
    )


@dp.message_handler(content_types=["voice"])
async def voice_recognition(message: types.Message):
    await types.ChatActions.typing()

    await message.reply("Not Implemented Yet")


@dp.message_handler(commands=["ver"])
async def version(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await types.ChatActions.typing()
        await message.reply(f"<b>Version: {VERSION}</b>", parse_mode="HTML")


@dp.message_handler(commands=["g", "gi", "p"])
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

                result = f"<b>{response.title}</b>\n\n<i>{response.snippet}</i>\n\n{response.link}"
                return await message.reply(
                    result, parse_mode="HTML", disable_web_page_preview=True
                )
            else:
                return await not_found(message)

        if command in ["/gi", "/p"]:
            response = await google_api.search(query, search_type="image")

            if response.code != 404:
                try:
                    await types.ChatActions.typing()

                    caption = f"<i>{response.snippet}</i>\n\n{response.context_link}"
                    return await message.reply_photo(
                        photo=response.link, caption=caption, parse_mode="HTML"
                    )
                except BadRequest:
                    await types.ChatActions.typing()

                    message.reply(
                        "Ой! Какая-то неправильная картинка пришла. Попробуй еще раз."
                    )

            else:
                await types.ChatActions.typing()

                return await not_found(message)

    return await empty_query(message)


@dp.message_handler(commands=["y"])
async def youtube(message: types.Message):
    """
    YouTube Search
    """
    query = google_api.prepare_query(message)

    if query:
        response = await youtube_api.search(query)

        if response.code != 404:
            await types.ChatActions.typing()
            result = f"<b>{response.title}</b>\n\n<i>{response.description}</i>\n\n<b>{response.link}</b>"
            return await message.reply(result, parse_mode="HTML")

        else:
            await types.ChatActions.typing()

            return await not_found(message)

    return await empty_query(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
