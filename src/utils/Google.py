import os
import random
from enum import Enum
from typing import Optional, NamedTuple, Union

import requests


class GoogleResponse(NamedTuple):
    title: str
    url: str
    snippet: str


class GoogleImageResponse(NamedTuple):
    url: str
    source_url: str
    snippet: str


class SEARCH_TYPE(Enum):
    TEXT = 1
    IMAGE = 2


class GoogleAPI:
    def __init__(
        self,
        api_key: Optional[str] = os.getenv("GOOGLE_API_KEY"),
        cx: Optional[str] = os.getenv("GOOGLE_CX"),
    ):
        self.API_KEY = api_key
        self.CX = cx
        self.BASE_URL = f"https://www.googleapis.com/customsearch/v1?key={self.API_KEY}&cx={self.CX}"
        self._session = requests.Session()

    def __enter__(self):
        if self._session is None:
            self._session = requests.Session()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _search_main(self, query) -> Optional[GoogleResponse]:
        response = self._session.get(
            url=self.BASE_URL, params={"q": query, "num": 1}
        )
        try:
            data = response.json()["items"][0]

            return GoogleResponse(
                title=data["title"],
                url=data["formattedUrl"],
                snippet=data["htmlSnippet"],
            )
        except (IndexError, KeyError):
            return None

    def _search_image(self, query) -> Optional[GoogleImageResponse]:
        response = self._session.get(
            url=self.BASE_URL, params={"q": query, "searchType": "image"}
        )
        try:
            data = random.choice(response.json()["items"])

            item = GoogleImageResponse(
                url=data["link"],
                source_url=data["image"]["contextLink"],
                snippet=data["snippet"],
            )

            return item
        except KeyError:
            return None

    def search(
        self, query, search_type
    ) -> Union[GoogleImageResponse, GoogleResponse]:
        if search_type == SEARCH_TYPE.TEXT:
            return self._search_main(query)

        if search_type == SEARCH_TYPE.IMAGE:
            return self._search_image(query)
