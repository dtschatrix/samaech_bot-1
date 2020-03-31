from typing import NamedTuple

import requests


class SteamStatsDTO(NamedTuple):
    status: str
    service: str


class SteamStatsAPI:
    def __init__(self):
        self._headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) "
            "AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"
        }
        self._services = {
            "dota2": 33,
            "csgo": 4,
            "ingame": 38,
            "online": 46,
            "store": 54,
        }
        self._session = None
        self._base_url = "https://crowbar.steamstat.us/gravity.json"

    def __enter__(self):
        if self._session is None:
            self._session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_online_status(self, service: str = "dota2"):
        try:
            response = self._session.get(self._base_url, headers=self._headers)
            data = response.json()

            service_key = self._services[service]

            result = data["services"][service_key][2]
            return SteamStatsDTO(status=result, service=service)
        except KeyError:
            return
