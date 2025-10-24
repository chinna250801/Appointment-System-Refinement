import reflex as rx
from app.states.admin_state import AdminState, SidebarItem
from app.auth import AuthState


def _sidebar_item(item: SidebarItem) -> rx.Component:
    is_active = AdminState.router.page.path == item["route"]
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5 shrink-0"),
        rx.el.span(item["name"]),
        href=item["route"],
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 rounded-lg bg-violet-100 px-3 py-2 text-violet-700 transition-all hover:text-violet-700 font-semibold",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
        ),
    )


def admin_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("activity", class_name="h-8 w-8 text-violet-600"),
                    rx.el.span("Admin Panel", class_name="sr-only"),
                    href="/admin/dashboard",
                    class_name="flex items-center gap-2 text-lg font-semibold md:text-base",
                ),
                rx.el.nav(
                    rx.foreach(AdminState.sidebar_items, _sidebar_item),
                    class_name="flex flex-col gap-1 px-2 text-sm font-medium",
                ),
                class_name="flex-1 py-4",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("log-out", class_name="h-5 w-5 mr-2"),
                    "Logout",
                    on_click=AuthState.logout,
                    class_name="flex items-center w-full gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
                ),
                class_name="mt-auto p-4 border-t",
            ),
            class_name="flex h-full max-h-screen flex-col gap-2",
        ),
        class_name="hidden border-r bg-gray-100/40 md:block w-64",
    )