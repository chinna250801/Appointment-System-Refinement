import reflex as rx
from typing import Any
import logging
import httpx
from app.models import Role
from app.api_client import get_api_client


class AuthState(rx.State):
    token: str = rx.Cookie("")
    user_info: dict[str, str | int] = {}
    is_loading: bool = False

    @rx.var
    def is_authenticated(self) -> bool:
        return self.token != "" and bool(self.user_info)

    @rx.var
    def user_role(self) -> Role | None:
        role = self.user_info.get("role")
        return Role(role) if role else None

    async def _update_user_info_from_token(self):
        if not self.token:
            self.logout()
            return
        try:
            api_client = get_api_client()
            user_data = await api_client.get_current_user()
            self.user_info = user_data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logging.warning("Token is invalid or expired, logging out.")
                self.logout()
            else:
                logging.exception(f"Failed to update user info: {e}")
                self.logout()

    @rx.event
    def logout(self):
        self.token = ""
        self.user_info = {}
        return rx.redirect("/")

    @rx.event
    async def check_auth(self):
        if not self.is_authenticated and self.token:
            await self._update_user_info_from_token()
        current_path = self.router.page.path
        public_paths = ["/", "/staff/login", "/patient/login", "/patient/register"]
        auth_pages = ["/staff/login", "/patient/login", "/patient/register"]
        if not self.is_authenticated and current_path not in public_paths:
            if current_path.startswith(("/admin", "/doctor")):
                return rx.redirect("/staff/login")
            if current_path.startswith("/patient"):
                return rx.redirect("/patient/login")
            return rx.redirect("/")
        if self.is_authenticated:
            role = self.user_role
            if current_path in auth_pages or current_path == "/":
                if role == Role.ADMIN:
                    return rx.redirect("/admin/dashboard")
                elif role == Role.DOCTOR:
                    return rx.redirect("/doctor/dashboard")
                elif role == Role.PATIENT:
                    return rx.redirect("/patient/dashboard")
            if role == Role.ADMIN and (not current_path.startswith("/admin")):
                return rx.redirect("/admin/dashboard")
            elif role == Role.DOCTOR and (not current_path.startswith("/doctor")):
                return rx.redirect("/doctor/dashboard")
            elif role == Role.PATIENT and (not current_path.startswith("/patient")):
                return rx.redirect("/patient/dashboard")

    async def _login(self, form_data: dict, is_staff: bool):
        username = form_data.get("username")
        password = form_data.get("password")
        if not username or not password:
            return rx.toast.error("Username and password are required.")
        self.is_loading = True
        try:
            api_client = get_api_client()
            response = await api_client.client.post(
                f"{api_client.client.base_url}/api/auth/login",
                data={"username": username, "password": password},
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            self.user_info = data["user"]
            role = Role(self.user_info["role"])
            if is_staff and role not in [Role.ADMIN, Role.DOCTOR]:
                raise ValueError("Not an authorized staff member.")
            if not is_staff and role != Role.PATIENT:
                raise ValueError("Not a patient account.")
            if role == Role.ADMIN:
                return rx.redirect("/admin/dashboard")
            elif role == Role.DOCTOR:
                return rx.redirect("/doctor/dashboard")
            else:
                return rx.redirect("/patient/dashboard")
        except (httpx.HTTPStatusError, ValueError) as e:
            logging.exception(f"Login failed: {e}")
            return rx.toast.error("Invalid credentials or not authorized.")
        finally:
            self.is_loading = False

    @rx.event
    async def staff_login(self, form_data: dict):
        return await self._login(form_data, is_staff=True)

    @rx.event
    async def patient_login(self, form_data: dict):
        return await self._login(form_data, is_staff=False)

    @rx.event
    async def patient_register(self, form_data: dict):
        username = form_data.get("username")
        email = form_data.get("email")
        password = form_data.get("password")
        if not all([username, email, password]):
            return rx.toast.error("Username, email, and password are required.")
        self.is_loading = True
        try:
            api_client = get_api_client()
            data = await api_client.register(form_data)
            self.token = data["access_token"]
            self.user_info = data["user"]
            return rx.redirect("/patient/dashboard")
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", "Registration failed.")
            logging.exception(f"Registration failed: {error_detail}")
            return rx.toast.error(error_detail)
        finally:
            self.is_loading = False