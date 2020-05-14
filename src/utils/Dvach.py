from datetime import datetime
from enum import Enum
from typing import Dict, NamedTuple, List, Optional
import random
import requests
from constants.constants import MESSAGES
from html.parser import HTMLParser


class DvachThread(NamedTuple):
    url: str
    image: str
    id: str


class DvachPost(NamedTuple):
    message: str
    message_link: str
    images: Optional[List[str]]


class POST_OFFSET(Enum):
    RANDOM = 1
    LAST = 2


class POST_TYPE:
    MP4 = "mp4"
    ANY = "any"


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
        super().__init__()

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


class DvachAPI:
    def __init__(self):
        self._session = None

    def __enter__(self):
        if self._session is None:
            self._session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    @staticmethod
    def _strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    @staticmethod
    def _parse_thread_data(
        response: Dict, subject: str, board: str
    ) -> DvachThread:
        for thread in response["threads"]:
            print(
                f'CHECK {subject} in {thread["posts"][0]["comment"].lower()}'
            )
            if thread["posts"][0]["tags"] == subject or (
                subject in thread["posts"][0]["comment"].lower()
            ):
                image = f'https://2ch.hk{random.choice(thread["posts"][0]["files"])["path"]}'

                thread_url = (
                    f'https://2ch.hk/{board}/res/{thread["thread_num"]}.html'
                )

                return DvachThread(
                    url=thread_url, image=image, id=thread["thread_num"]
                )

    def get_thread(
        self,
        board: str,
        subject: str,
        pages: List[str] = ("index", "1", "2", "3", "4", "5", "6"),
    ) -> Optional[DvachThread]:
        for page in pages:
            response = self._session.get(
                url=f"https://2ch.hk/{board}/{page}.json"
            )

            data = response.json()

            result = self._parse_thread_data(data, subject, board)

            if result:
                return result

    def get_post(
        self,
        thread_id: str = None,
        board: str = "vg",
        offset: POST_OFFSET = POST_OFFSET.RANDOM,
    ):
        url = f"https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={board}&thread={thread_id}&num={thread_id}"
        THREAD_LINK = f"https://2ch.hk/{board}/res/{thread_id}.html"
        response = self._session.get(url=url)
        data = response.json()

        if offset == POST_OFFSET.LAST:
            post_data = data[-1]

        if offset == POST_OFFSET.RANDOM:
            post_data = random.choice(data)

        images = [
            f'https://2ch.hk{_file["path"]}'
            for _file in post_data["files"]
            if post_data["files"]
        ]

        message = self._strip_tags(post_data["comment"].replace("<br>", "\n"))
        message_link = f'{THREAD_LINK}#{post_data["num"]}'

        return DvachPost(
            message=message, message_link=message_link, images=images
        )

    def get_random_mp4_post(self, thread_id: str = None, board: str = None):
        url = f"https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={board}&thread={thread_id}&num={thread_id}"
        thread_url = f"https://2ch.hk/{board}/res/{thread_id}.html"
        response = self._session.get(url=url)
        data = response.json()

        found = False

        post_data = random.choice(data)

        while not found:
            media = [
                f'https://2ch.hk{_file["path"]}'
                for _file in post_data["files"]
                if post_data["files"]
            ]
            for item in media:
                if "mp4" in item:
                    found = item
                    break
            else:
                random.seed(datetime.now())
                post_data = random.choice(data)

        message = self._strip_tags(post_data["comment"].replace("<br>", "\n"))
        message_link = f'{thread_url}#{post_data["num"]}'

        return DvachPost(
            message=message, message_link=message_link, images=[found]
        )
