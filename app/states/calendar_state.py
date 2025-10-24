import reflex as rx
from typing import TypedDict, Any
import logging
from datetime import datetime, timedelta, date


class Slot(TypedDict):
    id: int
    provider_id: int
    start_datetime: str
    end_datetime: str
    price_cents: int
    is_booked: bool
    calendar_month: str


class AvailabilityTemplate(TypedDict):
    weekdays: list[int]
    start_time: str
    end_time: str
    slot_duration: int


class CalendarDay(TypedDict):
    date_str: str
    date_num: str
    is_current_month: bool
    slots: list[Slot]


class CalendarState(rx.State):
    slots: list[Slot] = []
    availability_configs: dict[int, dict[str, AvailabilityTemplate]] = {}
    selected_provider_id: int = 1
    selected_month: datetime = datetime.now().replace(day=1)
    show_availability_modal: bool = False
    availability_template: AvailabilityTemplate = {
        "weekdays": [0, 1, 2, 3, 4],
        "start_time": "09:00",
        "end_time": "17:00",
        "slot_duration": 30,
    }
    selected_slot: dict = {}
    is_loading: bool = False
    error_message: str = ""
    _slot_counter: int = 0

    @rx.event
    def on_load(self):
        self.selected_month = datetime.now().replace(day=1)

    def _validate_month_limit(self, month_dt: datetime) -> bool:
        limit_date = (datetime.now().replace(day=1) + timedelta(days=31 * 6)).replace(
            day=1
        )
        return month_dt < limit_date

    def _slot_exists(self, provider_id: int, start_datetime: datetime) -> bool:
        return any(
            (
                s["provider_id"] == provider_id
                and s["start_datetime"] == start_datetime.isoformat()
                for s in self.slots
            )
        )

    def _generate_time_slots(
        self, date_obj: date, template: AvailabilityTemplate, provider_id: int
    ) -> list[Slot]:
        generated_slots = []
        try:
            start_time_obj = datetime.strptime(template["start_time"], "%H:%M").time()
            end_time_obj = datetime.strptime(template["end_time"], "%H:%M").time()
            duration = timedelta(minutes=int(template["slot_duration"]))
            current_time = datetime.combine(date_obj, start_time_obj)
            end_of_day = datetime.combine(date_obj, end_time_obj)
        except (ValueError, TypeError) as e:
            logging.exception(f"Invalid template format: {e}")
            self.error_message = "Invalid time or duration format in template."
            return []
        while current_time + duration <= end_of_day:
            if not self._slot_exists(provider_id, current_time):
                self._slot_counter += 1
                generated_slots.append(
                    {
                        "id": self._slot_counter,
                        "provider_id": provider_id,
                        "start_datetime": current_time.isoformat(),
                        "end_datetime": (current_time + duration).isoformat(),
                        "price_cents": 5000,
                        "is_booked": False,
                        "calendar_month": date_obj.strftime("%Y-%m"),
                    }
                )
            current_time += duration
        return generated_slots

    @rx.event
    def generate_monthly_slots(
        self, provider_id: int, month_dt: datetime, template: AvailabilityTemplate
    ):
        self.is_loading = True
        self.error_message = ""
        yield
        if not self._validate_month_limit(month_dt):
            self.error_message = "Cannot create calendar beyond 6 months from today"
            self.is_loading = False
            return rx.toast.error(self.error_message)
        month_str = month_dt.strftime("%Y-%m")
        self.slots = [
            s
            for s in self.slots
            if not (
                s["provider_id"] == provider_id and s["calendar_month"] == month_str
            )
        ]
        new_slots = []
        current_date = month_dt
        while current_date.month == month_dt.month:
            if current_date.weekday() in template.get("weekdays", []):
                day_slots = self._generate_time_slots(
                    current_date.date(), template, provider_id
                )
                new_slots.extend(day_slots)
            current_date += timedelta(days=1)
        self.slots.extend(new_slots)
        self.update_availability_template(provider_id, month_str, template)
        self.is_loading = False
        self.show_availability_modal = False

    @rx.event
    def change_month(self, delta: int):
        new_month = self.selected_month + timedelta(days=31 * delta)
        self.selected_month = new_month.replace(day=1)

    @rx.event
    def toggle_availability_modal(self):
        self.show_availability_modal = not self.show_availability_modal

    @rx.event
    def prompt_for_template_and_generate(self):
        self.show_availability_modal = True

    @rx.event
    def set_template_value(self, key: str, value: Any):
        self.availability_template[key] = value

    @rx.event
    def toggle_template_weekday(self, day_index: int):
        if day_index in self.availability_template["weekdays"]:
            self.availability_template["weekdays"].remove(day_index)
        else:
            self.availability_template["weekdays"].append(day_index)
            self.availability_template["weekdays"].sort()

    @rx.event
    def generate_slots_from_template(self):
        return CalendarState.generate_monthly_slots(
            self.selected_provider_id, self.selected_month, self.availability_template
        )

    @rx.event
    def update_availability_template(
        self, provider_id: int, month: str, template: AvailabilityTemplate
    ):
        if provider_id not in self.availability_configs:
            self.availability_configs[provider_id] = {}
        self.availability_configs[provider_id][month] = template

    @rx.event
    def set_selected_provider_id(self, provider_id_str: str):
        try:
            self.selected_provider_id = int(provider_id_str)
        except ValueError as e:
            logging.exception(
                f"Could not convert provider_id '{provider_id_str}' to int: {e}"
            )

    @rx.event
    def select_slot(self, slot: dict):
        self.selected_slot = slot

    @rx.var
    def selected_month_str(self) -> str:
        return self.selected_month.strftime("%B %Y")

    @rx.var
    def calendar_grid(self) -> list[CalendarDay]:
        first_day_of_month = self.selected_month.replace(day=1)
        start_day = first_day_of_month - timedelta(
            days=(first_day_of_month.weekday() + 1) % 7
        )
        grid = []
        current_day = start_day
        for _ in range(42):
            day_slots = [
                s
                for s in self.slots
                if s["provider_id"] == self.selected_provider_id
                and s["start_datetime"].startswith(current_day.strftime("%Y-%m-%d"))
            ]
            grid.append(
                {
                    "date_str": current_day.strftime("%Y-%m-%d"),
                    "date_num": current_day.strftime("%d"),
                    "is_current_month": current_day.month == self.selected_month.month,
                    "slots": sorted(day_slots, key=lambda x: x["start_datetime"]),
                }
            )
            current_day += timedelta(days=1)
        return grid

    @rx.var
    def template_weekdays(self) -> list[tuple[int, bool, str]]:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return [
            (i, i in self.availability_template["weekdays"], days[i]) for i in range(7)
        ]

    @rx.var
    def selected_slot_date_str(self) -> str:
        if not self.selected_slot:
            return ""
        try:
            dt = datetime.fromisoformat(self.selected_slot["start_datetime"])
            return dt.strftime("%A, %B %d, %Y")
        except (ValueError, KeyError) as e:
            logging.exception(f"Error formatting selected_slot_date_str: {e}")
            return ""

    @rx.var
    def selected_slot_time_str(self) -> str:
        if not self.selected_slot:
            return ""
        try:
            start_dt = datetime.fromisoformat(self.selected_slot["start_datetime"])
            end_dt = datetime.fromisoformat(self.selected_slot["end_datetime"])
            return f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
        except (ValueError, KeyError) as e:
            logging.exception(f"Error formatting selected_slot_time_str: {e}")
            return ""