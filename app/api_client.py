import reflex as rx
import httpx
import logging
from app.config import BACKEND_API_URL
from typing import Any


class APIClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(APIClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, token_provider: callable):
        if not hasattr(self, "_initialized"):
            self.client = httpx.AsyncClient(base_url=BACKEND_API_URL)
            self.token_provider = token_provider
            self._initialized = True

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        token = self.token_provider()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            response = await self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logging.exception(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logging.exception(f"Request error occurred: {e}")
            raise

    async def login(self, username: str, password: str) -> dict[str, dict]:
        response = await self._request(
            "post", "/api/auth/login", data={"username": username, "password": password}
        )
        return response.json()

    async def register(self, form_data: dict) -> dict[str, dict]:
        response = await self._request("post", "/api/auth/register", json=form_data)
        return response.json()

    async def get_current_user(self) -> dict[str, dict]:
        response = await self._request("get", "/api/auth/me")
        return response.json()

    async def logout(self):
        await self._request("post", "/api/auth/logout")


def get_api_client() -> APIClient:
    from app.auth import AuthState

    return APIClient(token_provider=rx.State.get_state(AuthState).token)