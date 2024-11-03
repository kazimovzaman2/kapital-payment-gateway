import json
from base64 import b64encode
from typing import Optional, Union

import requests


class Kapital:
    """A simple client for Kapital payment gateway."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        default_base_url = "https://txpgtst.kapitalbank.az/api"
        default_username = "TerminalSys/kapital"
        default_password = "kapital123"

        is_partial_custom = (
            (base_url is not None and (username is None or password is None))
            or (
                username is not None and (base_url is None or password is None)
            )
            or (
                password is not None and (base_url is None or username is None)
            )
        )

        if is_partial_custom:
            raise ValueError(
                "All credentials (base_url, username, password) must be provided if any are set."
            )

        self.base_url = base_url or default_base_url
        self.username = username or default_username
        self.password = password or default_password

    def _encode_credentials(self) -> str:
        """Encodes the credentials for basic auth."""
        credentials = f"{self.username}:{self.password}"
        return b64encode(credentials.encode()).decode()

    def _build_headers(self) -> dict:
        """Builds headers for requests with encoded credentials."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._encode_credentials()}",
        }

    def create_order(
        self,
        redirect_url: str,
        amount: Union[int, float],
        description: str,
        currency: str = "AZN",
        language: str = "az",
    ) -> dict:
        """Creates a payment order and returns the response data."""
        payload = json.dumps(
            {
                "order": {
                    "typeRid": "Order_SMS",
                    "amount": str(amount),
                    "currency": currency,
                    "language": language,
                    "description": description,
                    "hppRedirectUrl": redirect_url,
                    "hppCofCapturePurposes": ["Cit"],
                }
            }
        )

        headers = self._build_headers()
        response = requests.post(
            f"{self.base_url}/order", headers=headers, data=payload
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create order: {response.text}")

        order_data = response.json().get("order", {})
        if not order_data:
            raise ValueError("Invalid response format: 'order' key missing")

        order_id = order_data.get("id")
        password = order_data.get("password")
        hpp_url = order_data.get("hppUrl")
        status = order_data.get("status")
        cvv2_auth_status = order_data.get("cvv2AuthStatus")
        secret = order_data.get("secret")

        redirect_url = (
            f"{hpp_url}?id={order_id}&password={password}"
            if order_id and password
            else None
        )

        return {
            "order_id": order_id,
            "password": password,
            "hppUrl": hpp_url,
            "status": status,
            "cvv2AuthStatus": cvv2_auth_status,
            "secret": secret,
            "redirect_url": redirect_url,
        }
