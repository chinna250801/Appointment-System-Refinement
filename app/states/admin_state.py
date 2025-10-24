import reflex as rx
from typing import TypedDict


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