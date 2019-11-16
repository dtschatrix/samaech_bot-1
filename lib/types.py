from typing import Optional, List


class GoogleSearchResult:
    def __init__(self, title: str, link: str, snippet: str) -> None:
        self.code = 200
        self.message = "OK"
        self.title = title
        self.link = link
        self.snippet = snippet


class GoogleImageResult:
    def __init__(self, link: str, snippet: str, context_link: str) -> None:
        self.code = 200
        self.message = "OK"
        self.link = link
        self.snippet = snippet
        self.title = ""
        self.context_link = context_link


class YoutubeSearchResult:
    def __init__(
        self, video_id: str, title: str, description: str, channel: str
    ) -> None:
        self.code = 200
        self.message = "OK"
        self.link = f"https://www.youtube.com/watch?v={video_id}"
        self.title = title
        self.description = description
        self.channel = channel


class NotFoundResult:
    def __init__(self) -> None:
        self.code = 404
        self.message = "Not Found"
        self.link = ""
        self.snippet = ""
        self.title = ""
        self.description = ""
        self.context_link = ""


class DvachThread:
    def __init__(self, link: str, image: str, thread_id: str) -> None:
        self.link = link
        self.image = image
        self.thread_id = thread_id


class DvachPost:
    def __init__(
        self, message: str, message_link: str, images: Optional[List[str]] = []
    ) -> None:
        self.message = message
        self.message_link = message_link
        self.images = images
