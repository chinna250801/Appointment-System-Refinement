import reflex as rx
from app.states.calendar_state import CalendarState
from datetime import datetime


def calendar_controls() -> rx.Component:
    """Controls for the calendar page: provider selector, date picker, view toggle."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span("Provider", class_name="text-sm font-medium text-gray-600"),
                rx.el.select(
                    rx.el.option("Select Provider", value="0"),
                    rx.el.option("Dr. Smith", value="1"),
                    rx.el.option("Dr. Jones", value="2"),
                    on_change=CalendarState.set_selected_provider_id,
                    default_value=CalendarState.selected_provider_id.to(str),
                    class_name="w-48 p-2 border rounded-md text-sm",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("chevron-left"),
                    on_click=lambda: CalendarState.change_month(-1),
                    class_name="p-2 rounded-md hover:bg-gray-100",
                ),
                rx.el.span(
                    CalendarState.selected_month_str,
                    class_name="text-lg font-semibold w-32 text-center",
                ),
                rx.el.button(
                    rx.icon("chevron-right"),
                    on_click=lambda: CalendarState.change_month(1),
                    class_name="p-2 rounded-md hover:bg-gray-100",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center gap-6",
        ),
        rx.el.div(
            rx.el.button(
                "Generate Calendar",
                on_click=CalendarState.prompt_for_template_and_generate,
                class_name="px-4 py-2 bg-violet-600 text-white text-sm font-semibold rounded-lg hover:bg-violet-700 transition",
            )
        ),
        class_name="sticky top-0 z-10 flex items-center justify-between p-4 bg-white border-b",
    )


def month_view() -> rx.Component:
    """Renders the calendar in a month view."""
    return rx.el.div(
        rx.el.div(
            rx.foreach(
                ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                lambda day: rx.el.div(
                    day, class_name="text-center text-sm font-medium text-gray-500 py-2"
                ),
            ),
            class_name="grid grid-cols-7 border-b border-t",
        ),
        rx.el.div(
            rx.foreach(
                CalendarState.calendar_grid,
                lambda day: rx.el.div(
                    rx.el.span(day["date_num"], class_name="p-1 text-sm"),
                    rx.foreach(
                        day["slots"],
                        lambda slot: rx.el.div(
                            f"{slot['start_datetime'].split('T')[1][:5]}",
                            class_name=rx.cond(
                                slot["is_booked"],
                                "bg-gray-100 text-gray-500 border-gray-300 text-xs px-2 py-1 rounded-md border m-1",
                                "bg-green-100 text-green-700 border-green-300 text-xs px-2 py-1 rounded-md border m-1 cursor-pointer hover:bg-green-200",
                            ),
                            on_click=lambda: CalendarState.select_slot(slot),
                        ),
                    ),
                    class_name=rx.cond(
                        day["is_current_month"],
                        "h-36 border-l border-b p-1 overflow-y-auto",
                        "h-36 border-l border-b p-1 overflow-y-auto bg-gray-50 text-gray-400",
                    ),
                ),
            ),
            class_name="grid grid-cols-7 h-full",
        ),
        class_name="flex-1 overflow-hidden",
    )


def _availability_modal() -> rx.Component:
    return rx.cond(
        CalendarState.show_availability_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Create Calendar for Month", class_name="text-lg font-bold"
                    ),
                    rx.el.p(
                        "Define the working hours and breaks to generate time slots.",
                        class_name="text-sm text-gray-500",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=CalendarState.toggle_availability_modal,
                        class_name="absolute top-3 right-3 p-1 rounded-full hover:bg-gray-100",
                    ),
                    class_name="relative p-6 border-b",
                ),
                rx.el.div(
                    rx.el.h4("Days of the Week", class_name="font-semibold mb-2"),
                    rx.el.div(
                        rx.foreach(
                            CalendarState.template_weekdays,
                            lambda day_tuple: rx.el.label(
                                rx.el.input(
                                    type="checkbox",
                                    on_change=lambda checked: CalendarState.toggle_template_weekday(
                                        day_tuple[0]
                                    ),
                                    checked=day_tuple[1],
                                    class_name="mr-2",
                                ),
                                day_tuple[2],
                                class_name="flex items-center text-sm",
                            ),
                        ),
                        class_name="grid grid-cols-4 gap-2 mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label("Start Time", class_name="text-sm font-medium"),
                            rx.el.input(
                                name="start_time",
                                type="time",
                                default_value=CalendarState.availability_template[
                                    "start_time"
                                ],
                                on_change=lambda v: CalendarState.set_template_value(
                                    "start_time", v
                                ),
                                class_name="w-full p-2 border rounded-md mt-1",
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.div(
                            rx.el.label("End Time", class_name="text-sm font-medium"),
                            rx.el.input(
                                name="end_time",
                                type="time",
                                default_value=CalendarState.availability_template[
                                    "end_time"
                                ],
                                on_change=lambda v: CalendarState.set_template_value(
                                    "end_time", v
                                ),
                                class_name="w-full p-2 border rounded-md mt-1",
                            ),
                            class_name="flex-1",
                        ),
                        class_name="flex gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Slot Duration (minutes)", class_name="text-sm font-medium"
                        ),
                        rx.el.select(
                            rx.foreach(
                                [15, 30, 45, 60], lambda d: rx.el.option(d, value=d)
                            ),
                            default_value=CalendarState.availability_template[
                                "slot_duration"
                            ].to(str),
                            on_change=lambda v: CalendarState.set_template_value(
                                "slot_duration", v
                            ),
                            class_name="w-full p-2 border rounded-md mt-1",
                        ),
                        class_name="mb-4",
                    ),
                    class_name="p-6",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=CalendarState.toggle_availability_modal,
                        class_name="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300",
                    ),
                    rx.el.button(
                        "Generate Slots",
                        on_click=CalendarState.generate_slots_from_template,
                        is_loading=CalendarState.is_loading,
                        class_name="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700",
                    ),
                    class_name="flex justify-end gap-4 p-6 bg-gray-50 border-t",
                ),
                class_name="bg-white rounded-xl shadow-2xl w-full max-w-lg",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/50",
        ),
        None,
    )


def _slot_detail_modal() -> rx.Component:
    return rx.cond(
        CalendarState.selected_slot.keys().length() > 0,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3("Slot Details", class_name="text-lg font-bold"),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=lambda: CalendarState.select_slot({}),
                        class_name="absolute top-3 right-3 p-1 rounded-full hover:bg-gray-100",
                    ),
                    class_name="relative p-6 border-b",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p("Date:", class_name="font-semibold"),
                        rx.el.p(CalendarState.selected_slot_date_str),
                        class_name="flex justify-between",
                    ),
                    rx.el.div(
                        rx.el.p("Time:", class_name="font-semibold"),
                        rx.el.p(CalendarState.selected_slot_time_str),
                        class_name="flex justify-between",
                    ),
                    rx.el.div(
                        rx.el.p("Status:", class_name="font-semibold"),
                        rx.el.span(
                            rx.cond(
                                CalendarState.selected_slot["is_booked"],
                                "Booked",
                                "Available",
                            ),
                            class_name=rx.cond(
                                CalendarState.selected_slot["is_booked"],
                                "px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full",
                                "px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full",
                            ),
                        ),
                        class_name="flex justify-between items-center",
                    ),
                    class_name="p-6 space-y-3",
                ),
                rx.el.div(
                    rx.el.button(
                        "Close",
                        on_click=lambda: CalendarState.select_slot({}),
                        class_name="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300",
                    ),
                    rx.cond(
                        ~CalendarState.selected_slot["is_booked"],
                        rx.el.button(
                            "Book Slot",
                            class_name="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700",
                        ),
                        rx.el.div(),
                    ),
                    class_name="flex justify-end gap-4 p-6 bg-gray-50 border-t",
                ),
                class_name="bg-white rounded-xl shadow-2xl w-full max-w-sm",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/50",
        ),
        None,
    )


def calendar_view() -> rx.Component:
    """The main calendar view component."""
    return rx.el.div(
        calendar_controls(),
        rx.cond(
            CalendarState.is_loading,
            rx.el.div(
                rx.spinner(size="3"),
                class_name="flex-1 flex items-center justify-center",
            ),
            month_view(),
        ),
        _availability_modal(),
        _slot_detail_modal(),
        on_mount=CalendarState.on_load,
        class_name="flex flex-col h-[calc(100vh-65px)] border rounded-lg bg-white shadow-sm overflow-hidden",
    )