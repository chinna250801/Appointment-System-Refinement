
# Backend Connection and API Guide

This document explains how the Reflex frontend communicates with the backend and provides best practices for handling API calls.

---

### 1. How Frontend-Backend Communication Works in Reflex

In Reflex, you do not need to write traditional REST API endpoints (like in FastAPI or Flask) for most operations. Instead, the framework automates the connection between frontend components and backend state logic.

-   **Frontend:** UI components (e.g., `rx.el.button`) have event triggers like `on_click`.
-   **Backend:** `rx.State` classes contain event handlers (`@rx.event`) that hold the business logic.
-   **Connection:** When a user interacts with a component (e.g., clicks a button), the event trigger calls the associated event handler on the backend. Reflex automatically creates an API endpoint for this handler and manages the request/response cycle.

**Example:**


# Frontend Component
rx.el.button("Login", on_click=AuthState.staff_login)

# Backend State in app/auth.py
class AuthState(rx.State):
    @rx.event
    async def staff_login(self, form_data: dict):
        # ... logic to process login ...


When the button is clicked, Reflex sends the form data to the `/api/events/AuthState.staff_login` endpoint, executes the `staff_login` method, and updates the frontend with any state changes.

---

### 2. Best Practices for API (Event Handler) Calls

#### A. Data Transfer

-   **Forms:** For submitting forms, use `rx.el.form` with an `on_submit` handler. The form data is automatically collected into a dictionary.
    
    rx.el.form(
        rx.el.input(name="username"),
        rx.el.button("Submit", type="submit"),
        on_submit=MyState.handle_form
    )
    
-   **Simple Arguments:** For passing single values, use a `lambda` function.
    
    rx.el.button("Delete", on_click=lambda: MyState.delete_item(item_id))
    

#### B. Handling Loading States

API calls can take time. Always provide visual feedback to the user.

-   **Use a Loading Var:** Add a boolean `is_loading` variable to your state.
-   **Toggle Loading State:** Set `is_loading = True` at the start of your event handler and `is_loading = False` at the end. Use a `try...finally` block to ensure it's always reset.

**Example:**


class AdminState(rx.State):
    patients: list[Patient] = []
    is_loading: bool = False

    @rx.event
    async def get_patients(self):
        self.is_loading = True
        try:
            async with rx.asession() as session:
                # ... fetch patients ...
                self.patients = result
        finally:
            self.is_loading = False # Ensure this always runs

# In the UI
rx.cond(
    AdminState.is_loading,
    rx.spinner(),
    patient_table(AdminState.patients)
)


#### C. Error Handling and User Feedback

Never let an API call fail silently.

-   **Use `try...except`:** Wrap your logic in a `try...except` block to catch potential errors (e.g., database errors, external API failures).
-   **Provide Toast Notifications:** Use `rx.toast.error()` to show a user-friendly error message. Log the full exception for debugging.
-   **Logging:** Use Python's `logging` module to log the full traceback on the server. This is crucial for debugging production issues.

**Example:**


import logging

class AuthState(rx.State):
    @rx.event
    async def patient_register(self, form_data: dict):
        try:
            # ... registration logic ...
            if user_exists:
                return rx.toast.error("Username already taken.")
            # ...
            return rx.redirect("/patient/dashboard")
        except Exception as e:
            logging.error(f"Registration failed: {e}")
            return rx.toast.error("An unexpected error occurred. Please try again.")


By following these practices, you ensure that the connection between your frontend and backend is robust, user-friendly, and easy to debug.

