import reflex as rx
import httpx
import logging
from app.config import BACKEND_API_URL
from typing import TypedDict
import datetime


class Patient(TypedDict):
    id: int
    name: str
    phone: str | None
    email: str
    created_at: str
    user_id: int


class UserInfo(TypedDict):
    id: int
    username: str
    role: str


class LoginResponse(TypedDict):
    access_token: str
    token_type: str
    user: UserInfo


class APIClient:
    """A stateless API client for backend communication."""

    def __init__(self, token: str | None = None):
        """
        Initializes the API client.
        Args:
            token: The authentication token, if available.
        """
        self.token = token
        self.client = httpx.AsyncClient(base_url=BACKEND_API_URL)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Internal request method to handle authentication and error logging.
        """
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
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

    async def login(self, username: str, password: str) -> LoginResponse:
        """Performs login and returns token and user info."""
        response = await self.client.post(
            "/api/auth/login", data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()

    async def register(self, form_data: dict) -> LoginResponse:
        """Registers a new patient."""
        response = await self._request("post", "/api/auth/register", json=form_data)
        return response.json()

    async def get_current_user(self) -> UserInfo:
        """Fetches the current user's information using the stored token."""
        if not self.token:
            raise ValueError("Authentication token not provided.")
        response = await self._request("get", "/api/auth/me")
        return response.json()

    async def get_patients(self) -> list[Patient]:
        """Fetches a list of all patients."""
        response = await self._request("get", "/api/patients")
        return response.json()