import logging
import os

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class Stripe:
    BASE_URL = "https://api.stripe.com/v1"

    def __init__(self):
        self.key = os.getenv("STRIPE_KEY")

    def create_payment_link(self, price: str, quantity: int) -> dict:
        r = self._send_post(
            "/payment_links",
            data={
                "line_items[0][price]": price,
                "line_items[0][quantity]": quantity,
            }
        )

        if r and "id" in r and "url" in r:
            return {"stripe_id": r["id"], "link": r["url"]}

    def create_price(self, amount: int, product: str) -> str:
        r = self._send_post(
            "/prices",
            data={
                "currency": "usd",
                "unit_amount": amount,  # in cents
                "product": product,
            }
        )

        if r and "id" in r:
            return r["id"]

    def create_product(self, name: str) -> str:
        r = self._send_post("/products", data={"name": name})

        if r and "id" in r:
            return r["id"]

    def search_product(self, name: str) -> str | None:
        r = self._send_get(
            "/products/search",
            data={
                "query": f"name:'{name}'",
            }
        )

        if r:
            if len(r["data"]):
                first_prod = r["data"][0]
                return first_prod["id"]

    def _send_get(self, uri: str, data: dict = None):
        r = requests.get(
            f"{self.BASE_URL}{uri}",
            data=data,
            auth=HTTPBasicAuth(self.key, ""),
        )

        if r.status_code == 200:
            return r.json()
        else:
            self._log_request_error(r)

    def _send_post(self, uri: str, data: dict = None):
        r = requests.post(
            f"{self.BASE_URL}{uri}",
            data=data,
            auth=HTTPBasicAuth(self.key, ""),
        )

        if r.status_code == 200:
            return r.json()
        else:
            self._log_request_error(r)

    def _log_request_error(self, r: requests.Response) -> None:
        logger.error(f"Request error: {r.status_code} - {r.text}")
