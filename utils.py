from typing import Optional, Union
from aiogram import types
import os
import requests
import random


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

    def search(self, query: str):
        try:
            request = requests.get(self.BASE_URL, params={"q": query})
            json_data = request.json()
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

    def search(
        self, query: str, search_type: str = "text"
    ) -> Union[GoogleSearchResult, GoogleImageResult, NotFoundResult]:
        try:
            if search_type == "text":
                request = requests.get(
                    f"{self.BASE_URL}", params={"q": query, "num": 1}
                )
                json_data = request.json()
                item = json_data["items"][0]

                return GoogleSearchResult(
                    title=item["title"], link=item["link"], snippet=item["snippet"]
                )

            if search_type == "image":
                request = requests.get(
                    f"{self.BASE_URL}", params={"q": query, "searchType": "image"}
                )
                json_data = request.json()
                item = random.choice(json_data["items"])

                return GoogleImageResult(
                    link=item["link"],
                    snippet=item["snippet"],
                    context_link=item["image"]["contextLink"],
                )

            return NotFoundResult()

        except (KeyError, IndexError):
            return NotFoundResult()

