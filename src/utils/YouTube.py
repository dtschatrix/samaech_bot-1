import os
from enum import Enum
from typing import NamedTuple, Optional

import requests


class YOUTUBE_SEARCH_TYPE(Enum):
    VIDEO = 1


class YouTubeSearchResult(NamedTuple):
    video_id: str
    title: str
    description: str
    channel: str
    url: str


class YouTubeAPI:
    def __init__(
        self, api_key: str = os.environ.get("GOOGLE_API_KEY")
    ) -> None:
        self._session = requests.Session()
        self._api_key = api_key
        self.BASE_URL = (
            f"https://www.googleapis.com/"
            f"youtube/v3/"
            f"search?part=snippet&key={self._api_key}"
            f"&maxResults=1&type="
        )

    def __enter__(self):
        if self._session is None:
            self._session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _search_video(
        self, query: str = None
    ) -> Optional[YouTubeSearchResult]:
        response = self._session.get(
            url=self.BASE_URL + "video", params={"q": query}
        )

        try:
            data = response.json()
            item = data["items"][0]

            result = YouTubeSearchResult(
                video_id=item["id"]["videoId"],
                title=item["snippet"]["title"],
                description=item["snippet"]["description"],
                channel=item["snippet"]["channelTitle"],
                url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            )

            return result
        except (IndexError, KeyError):
            return None

    def search(
        self,
        query: str = None,
        search_type: YOUTUBE_SEARCH_TYPE = YOUTUBE_SEARCH_TYPE.VIDEO,
    ) -> Optional[YouTubeSearchResult]:
        if search_type == YOUTUBE_SEARCH_TYPE.VIDEO:
            return self._search_video(query)
