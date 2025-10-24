import reflex as rx
from typing import TypedDict, Any
import logging
import httpx
from app.api_client import get_api_client
from app.models import Patient


class SidebarItem(TypedDict):
    name: str
    icon: str
    route: str


class AdminState(rx.State):
    sidebar_items: list[SidebarItem] = [
        {"name": "Dashboard", "icon": "layout-dashboard", "route": "/admin/dashboard"},
        {"name": "Departments", "icon": "building", "route": "/admin/departments"},
        {"name": "Doctors", "icon": "stethoscope", "route": "/admin/doctors"},
        {"name": "Patients", "icon": "user", "route": "/admin/patients"},
        {"name": "Appointments", "icon": "calendar", "route": "/admin/appointments"},
    ]
    patients: list[dict[str, dict]] = []
    is_loading: bool = False
    is_saving: bool = False
    is_deleting: bool = False

    @rx.event
    async def get_patients(self):
        self.is_loading = True
        try:
            api_client = get_api_client()
            response = await api_client.client.get("/api/patients")
            response.raise_for_status()
            self.patients = response.json()
        except httpx.HTTPError as e:
            logging.exception(f"Failed to fetch patients: {e}")
            return rx.toast.error("Could not load patients.")
        finally:
            self.is_loading = False