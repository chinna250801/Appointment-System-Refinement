import reflex as rx
from typing import TypedDict
import logging
import httpx
from app.api_client import APIClient, Patient
from app.auth import AuthState


class SidebarItem(TypedDict):
    name: str
    icon: str
    route: str


class AdminState(rx.State):
    sidebar_items: list[SidebarItem] = [
        {"name": "Dashboard", "icon": "layout-dashboard", "route": "/admin/dashboard"},
        {"name": "Calendar", "icon": "calendar-days", "route": "/admin/calendar"},
        {
            "name": "Appointments",
            "icon": "calendar-check",
            "route": "/admin/appointments",
        },
        {"name": "Departments", "icon": "building", "route": "/admin/departments"},
        {"name": "Doctors", "icon": "stethoscope", "route": "/admin/doctors"},
        {"name": "Patients", "icon": "user", "route": "/admin/patients"},
    ]
    patients: list[Patient] = []
    is_loading: bool = False
    is_saving: bool = False
    is_deleting: bool = False

    @rx.event
    async def get_patients(self):
        self.is_loading = True
        try:
            auth_state = await self.get_state(AuthState)
            api_client = APIClient(token=auth_state.token)
            self.patients = await api_client.get_patients()
        except (httpx.HTTPError, ValueError) as e:
            logging.exception(f"Failed to fetch patients: {e}")
            return rx.toast.error("Could not load patients.")
        finally:
            self.is_loading = False