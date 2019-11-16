import os
import random
from typing import Dict, List, Optional, Union

from aiogram import types
from aiohttp import ClientSession

client = ClientSession()


class GoogleSearchResult:
    def __init__(self, title: str, link: str, snippet: str):
        self.code = 200
        self.message = "OK"
        self.title = title
        self.link = link
        self.snippet = snippet


class GoogleImageResult:
    def __init__(self, link: str, snippet: str, context_link: str):
        self.code = 200
        self.message = "OK"
        self.link = link
        self.snippet = snippet
        self.title = ""
        self.context_link = context_link


class YoutubeSearchResult:
    LINK_TEMPLATE = "https://www.youtube.com/watch?v="

    def __init__(self, video_id: str, title: str, description: str, channel: str):
        self.code = 200
        self.message = "OK"
        self.link = f"{self.LINK_TEMPLATE}{video_id}"
        self.title = title
        self.description = description
        self.channel = channel


class NotFoundResult:
    def __init__(self):
        self.code = 404
        self.message = "Not Found"
        self.link = ""
        self.snippet = ""
        self.title = ""
        self.description = ""
        self.context_link = ""


class CommonUtils:
    def prepare_query(self, message: types.Message) -> Optional[str]:
        args = message.text.split()[1:]
        if args:
            return " ".join(args)

    def prepare_inline_query(self, message: types.Message) -> Optional[str]:
        args = message.split()[1:]
        if args:
            return " ".join(args)


class YoutubeUtils(CommonUtils):
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    BASE_URL: str = f"https://www.googleapis.com/youtube/v3/search?part=snippet&key={GOOGLE_API_KEY}&maxResults=1&type=video"

    async def search(self, query: str):
        try:
            async with client.get(
                url=self.BASE_URL, params={"q": query}, verify_ssl=False
            ) as request:
                json_data = await request.json()
                item = json_data["items"][0]

            return YoutubeSearchResult(
                video_id=item["id"]["videoId"],
                title=item["snippet"]["title"],
                description=item["snippet"]["description"],
                channel=item["snippet"]["channelTitle"],
            )

        except (KeyError, IndexError):
            return NotFoundResult()


class GoogleUtils(CommonUtils):
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CX: Optional[str] = os.getenv("GOOGLE_CX")
    BASE_URL: str = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"

    async def search(
        self, query: str, search_type: str = "text"
    ) -> Union[GoogleSearchResult, GoogleImageResult, NotFoundResult]:
        try:
            if search_type == "text":
                async with client.get(
                    url=f"{self.BASE_URL}",
                    params={"q": query, "num": 1},
                    verify_ssl=False,
                ) as request:
                    json_data = await request.json()
                    item = json_data["items"][0]

                return GoogleSearchResult(
                    title=item["title"], link=item["link"], snippet=item["snippet"]
                )

            if search_type == "image":
                async with client.get(
                    url=f"{self.BASE_URL}",
                    params={"q": query, "searchType": "image"},
                    verify_ssl=False,
                ) as request:
                    json_data = await request.json()
                    item = random.choice(json_data["items"])

                return GoogleImageResult(
                    link=item["link"],
                    snippet=item["snippet"],
                    context_link=item["image"]["contextLink"],
                )

            return NotFoundResult()

        except (KeyError, IndexError):
            return NotFoundResult()


class DvachThread:
    def __init__(self, link: str, image: str):
        self.link = link
        self.image = image


class DvachUtils(CommonUtils):
    async def parse_thread_data(
        self, response: Dict, subject: str, board: str
    ) -> Optional[DvachThread]:
        for thread in response["threads"]:
            if thread["posts"][0]["tags"] == subject:
                image = f'https://2ch.hk{random.choice(thread["posts"][0]["files"])["path"]}'
                print(image)
                thread_link = f'https://2ch.hk/{board}/res/{thread["thread_num"]}.html'
                return DvachThread(link=thread_link, image=image)

    async def get_thread(
        self, board: str, subject: str, pages: List[str] = ["index", "1"]
    ) -> DvachThread:
        for page in pages:
            async with client.get(
                url=f"https://2ch.hk/{board}/{page}.json", verify_ssl=False
            ) as request:
                json_data = await request.json()

                result = await self.parse_thread_data(json_data, subject, board)

                if result:
                    return result

        return DvachThread(
            link="Тред на нулевой не найден", image="./content/img/not-found.png"
        )
