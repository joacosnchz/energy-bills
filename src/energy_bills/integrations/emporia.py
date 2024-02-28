import logging
import os

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class Emporia:
    BASE_URL = "https://emporia-connect.xyt.co.za/api"

    def __init__(self, username: str = None, password: str = None) -> None:
        self.username = username if username else os.getenv("EMPORIA_USR")
        self.password = password if password else os.getenv("EMPORIA_PWD")

    def get_devices(self) -> list | None:
        r = requests.get(f"{self.BASE_URL}/devices", auth=HTTPBasicAuth(self.username, self.password))

        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Request error: {r.status_code} - {r.text}")

    def get_historical_usage(
            self, device: int, channel: str, start: str, end: str, scale: str, unit: str
    ) -> dict | None:
        request_url = (
            f"{self.BASE_URL}/devices/{device}/channels/{channel}/historical-usage"
            f"?start={start}&end={end}&scale={scale}&unit={unit}"
        )

        r = requests.get(request_url, auth=HTTPBasicAuth(self.username, self.password))

        if r.status_code == 200:
            return r.json()
        else:
            logger.error(f"Request error: {r.status_code} - {r.text}")
