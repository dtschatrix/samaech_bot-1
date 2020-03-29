import os
import random
from typing import Dict, List, Optional, Union

from aiogram import types
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ContentTypeError

from html.parser import HTMLParser

from lib.types import (
    DvachPost,
    DvachThread,
    GoogleImageResult,
    GoogleSearchResult,
    NotFoundResult,
    YoutubeSearchResult,
    SteamStatPost,
)

client = ClientSession(timeout=ClientTimeout(total=30))

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


class CommonUtils:
    def prepare_query(self, message: types.Message) -> Optional[str]:
        args = message.text.split()[1:]
        if args:
            return " ".join(args)

    def prepare_inline_query(self, message: types.Message) -> Optional[str]:
        args = message.split()[1:]
        if args:
            return " ".join(args)

    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()


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


class DvachUtils(CommonUtils):
    async def parse_thread_data(
        self, response: Dict, subject: str, board: str
    ) -> Optional[DvachThread]:
        for thread in response["threads"]:
            if thread["posts"][0]["tags"] == subject:
                image = f'https://2ch.hk{random.choice(thread["posts"][0]["files"])["path"]}'

                thread_link = f'https://2ch.hk/{board}/res/{thread["thread_num"]}.html'
                return DvachThread(
                    link=thread_link, image=image, thread_id=thread["thread_num"]
                )

    async def get_thread(
        self, board: str, subject: str, pages: List[str] = ["index", "1", "2"]
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
            link="Тред на нулевой не найден",
            image="./content/img/not-found.png",
            thread_id="",
        )

    async def get_post(
        self, thread_id: str, offset: str = "random"
    ) -> Optional[DvachPost]:
        URL = f"https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board=vg&thread={thread_id}&num={thread_id}"
        THREAD_LINK = f"https://2ch.hk/vg/res/{thread_id}.html"
        async with client.get(URL, verify_ssl=False) as response:
            try:
                if offset == "last":
                    post_data = (await response.json())[-1]
                elif offset == "random":
                    post_data = random.choice(await response.json())
                else:
                    return

                images = [
                    f'https://2ch.hk{_file["path"]}'
                    for _file in post_data["files"]
                    if post_data["files"]
                ]

                message = self.strip_tags(post_data["comment"].replace("<br>", "\n"))
                message_link = f'{THREAD_LINK}#{post_data["num"]}'

                return DvachPost(
                    message=message, message_link=message_link, images=images
                )
            except ContentTypeError:
                return DvachPost(message="API отвалилось.", message_link="#")
class SteamStatUtils(CommonUtils):
    user_fake_agent = f"Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"
    available_services = {"dota2": {33}, "csgo": {4,11,13,14,15,20,22}, "ingame": {38}, "online": {46}, "store": {54}}
    async def get_response(self, data) -> str:
        try:
            URL = f"https://crowbar.steamstat.us/gravity.json"
            param = data.split()[1] if len(data.split()) >= 2 else ''  
            async with client.get(URL, verify_ssl=False, headers={'User-Agent':self.user_fake_agent}) as response:
                json_data = await response.json()
                data = await self.format_data(json_data, param)
                return SteamStatPost(message=data)
        except Exception:
            return SteamStatPost(message="Что-то прозиошло с парсингом:(")

    async def format_data(self, data, params) -> str:
            json_data = f""
            service = []
            if params == '':
                service_set = list(self.available_services.values())
                for x in service_set:
                    for v in x:
                        service.append(v)

            elif params in self.available_services.keys():
                service = self.available_services.get(params)
            
            else:
             return f"Какой-то странный ключ пришёл :("

            for k in service:
                json_data += data["services"][k][0] + ': ' + data["services"][k][2] + '\n'
            return '`' + json_data +  '`'      
            
            

