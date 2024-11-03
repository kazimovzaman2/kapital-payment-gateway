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
                "All credentials (base_url, username, password) must be provided if any are set."  # noqa: E501
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
    ) -> tuple[dict, int]:
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
        }, response.status_code

    def save_card(
        self,
        redirect_url: str,
        amount: int,
        description: str = "Saving card.",
        currency: str = "AZN",
        language: str = "az",
    ) -> tuple[dict, int]:
        """Saves a card for future transactions."""
        payload = json.dumps(
            {
                "order": {
                    "typeRid": "Order_DMS",
                    "amount": str(amount),
                    "currency": currency,
                    "language": language,
                    "description": description,
                    "hppRedirectUrl": redirect_url,
                    "hppCofCapturePurposes": ["Cit", "Recurring"],
                    "aut": {"purpose": "AddCard"},
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
        }, response.status_code

    def pay_with_card(
        self,
        amount: float,
        description: str,
        token: str,
        currency: str = "AZN",
        language: str = "az",
    ) -> tuple[dict, int]:
        # Step 1: Create an order.
        order_payload = json.dumps(
            {
                "order": {
                    "typeRid": "Order_REC",
                    "amount": str(amount),
                    "currency": currency,
                    "language": language,
                    "description": description,
                }
            }
        )
        headers = self._build_headers()

        order = requests.post(
            f"{self.base_url}/order", headers=headers, data=order_payload
        )
        if order.status_code != 200:
            raise Exception(f"Failed to create order: {order.text}")

        order_data = order.json()

        order_id = order_data["order"]["id"]
        order_password = order_data["order"]["password"]

        # Step 2: Set the stored token for the order.
        set_src_token_url = f"{self.base_url}/order/{order_id}/set-src-token?password={order_password}"  # noqa: E501
        set_token_payload = json.dumps(
            {
                "order": {"initiationEnvKind": "Server"},
                "token": {"storedId": token},
            }
        )
        set_token = requests.post(
            set_src_token_url, headers=headers, data=set_token_payload
        )

        if set_token.status_code != 200:
            raise Exception(f"Failed to set token: {set_token.text}")

        # Step 3: Pay the order.
        exec_tran_url = f"{self.base_url}/order/{order_id}/exec-tran?password={order_password}"  # noqa: E501
        exec_tran_payload = json.dumps(
            {
                "tran": {
                    "phase": "Single",
                    "amount": str(amount),
                    "conditions": {"cofUsage": "Cit"},
                }
            }
        )

        exec_tran = requests.post(
            exec_tran_url, headers=headers, data=exec_tran_payload
        )

        if exec_tran.status_code != 200:
            raise Exception(f"Failed to execute transaction: {exec_tran.text}")

        return self.fetch_order_summary(order_id), exec_tran.status_code

    def reverse(
        self,
        order_id: str,
    ) -> tuple[dict, int]:
        payload = json.dumps({"tran": {"phase": "Auth", "voidKind": "Full"}})
        headers = self._build_headers()
        response = requests.post(
            f"{self.base_url}/order/{order_id}/exec-tran",
            headers=headers,
            data=payload,
        )

        if response.status_code == 400:
            error_response = response.json()

            if error_response.get("errorCode") == "InvalidOrderState":
                return {
                    "error": "Reversal not allowed. Order is already completed.",  # noqa: E501
                    "order_id": order_id,
                    "order_status": "Voided",
                }
            else:
                raise Exception(
                    f"Failed to reverse transaction: {response.text}"
                )

        return self.fetch_order_summary(order_id), response.status_code

    def refund(
        self,
        order_id: str,
        amount: int,
    ) -> tuple[dict, int]:
        payload = json.dumps(
            {"tran": {"phase": "Single", "amount": amount, "type": "Refund"}}
        )
        headers = self._build_headers()
        response = requests.post(
            f"{self.base_url}/order/{order_id}/exec-tran",
            headers=headers,
            data=payload,
        )

        if response.status_code == 400:
            error_response = response.json()

            if error_response.get("errorCode") == "InvalidAmt":
                return {
                    "error": "Refund not allowed. Refunded more than charged.",
                    "order_id": order_id,
                    "order_status": "PartPaid",
                }, response.status_code
            else:
                raise Exception(
                    f"Failed to refund transaction: {response.text}"
                )

        return self.fetch_order_summary(order_id), response.status_code

    def get_order_details(self, order_id: str) -> tuple[dict, int]:
        """Get order details."""

        headers = self._build_headers()
        response = requests.get(
            f"{self.base_url}/order/{order_id}?&tranDetailLevel=2&tokenDetailLevel=2&orderDetailLevel=2",  # noqa: E501
            headers=headers,
        )

        return response.json(), response.status_code

    def fetch_order_summary(self, order_id: str) -> tuple[dict, int]:
        """Extracts important data from the order details."""

        order_details, status_code = self.get_order_details(order_id)

        order = order_details.get("order", {})
        transaction = order.get("trans", [{}])[0]
        srcToken = order.get("srcToken", {})

        return {
            "order_id": order.get("id"),
            "status": order.get("status"),
            "amount": order.get("amount"),
            "currency": order.get("currency"),
            "creation_time": order.get("createTime"),
            "description": order.get("description"),
            "language": order.get("language"),
            "approval_code": transaction.get("approvalCode"),
            "transaction_id": transaction.get("actionId"),
            "transaction_type": transaction.get("type"),
            "payment_method": srcToken.get("paymentMethod"),
            "card_brand": srcToken.get("card").get("brand"),
            "masked_card_number": srcToken.get("displayName"),
        }, status_code
