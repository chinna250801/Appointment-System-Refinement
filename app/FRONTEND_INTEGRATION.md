# Frontend Integration Guide

This document explains how the Reflex frontend is structured to communicate with the standalone FastAPI backend.

---

### 1. API Client Architecture (`app/api_client.py`)

All communication with the backend is centralized in the `APIClient` class. This approach provides a single, organized place for all HTTP requests.

**Key Features:**
-   **`httpx.AsyncClient`**: Used for making asynchronous HTTP requests, which is essential for a non-blocking UI.
-   **Centralized Base URL**: The backend URL is configured once from an environment variable (`BACKEND_API_URL`).
-   **Automatic Token Injection**: The client automatically retrieves the JWT from the `AuthState`'s cookie and adds it to the `Authorization` header for every request.
-   **Error Handling**: It wraps requests in `try...except` blocks and raises `httpx.HTTPStatusError` on failure, which can be caught in the state event handlers.

**Example Method:**

# In app/api_client.py
class APIClient:
    async def get_patients(self) -> list[dict]:
        # The _request method handles headers and errors
        response = await self._request("get", "/api/patients")
        return response.json()


---

### 2. State Management Patterns

With a separated backend, the role of `rx.State` classes changes. They no longer perform business logic but instead orchestrate API calls and manage UI state.

#### A. Loading State Pattern

Every event handler that makes an API call must manage a loading state to provide user feedback.


# In app/states/admin_state.py
class AdminState(rx.State):
    patients: list[dict] = []
    is_loading: bool = False

    @rx.event
    async def get_patients(self):
        self.is_loading = True
        try:
            api_client = get_api_client()
            self.patients = await api_client.get_patients()
        except Exception as e:
            # Error handling discussed below
            pass
        finally:
            # This ensures the loading spinner always disappears
            self.is_loading = False


In the UI, you use `rx.cond` to show a spinner:

rx.cond(
    AdminState.is_loading,
    rx.spinner(),
    patient_table(AdminState.patients)
)


#### B. Error Handling Pattern

API calls can fail. The UI must handle these errors gracefully using `try...except` and `rx.toast`.


# In app/states/admin_state.py
@rx.event
async def get_patients(self):
    self.is_loading = True
    try:
        api_client = get_api_client()
        self.patients = await api_client.get_patients()
    except httpx.HTTPStatusError as e:
        # API returned an error (e.g., 401, 403, 404)
        error_message = e.response.json().get("detail", "An unknown API error occurred.")
        return rx.toast.error(error_message)
    except httpx.RequestError:
        # Network error (e.g., backend is down)
        return rx.toast.error("Cannot connect to the server.")
    finally:
        self.is_loading = False


---

### 3. Authentication State (`app/auth.py`)

The `AuthState` is the source of truth for the user's authentication status on the client side.

-   **`token: str = rx.Cookie("")`**: The JWT is stored in a browser cookie for persistence across page loads.
-   **`user_info: dict`**: Holds the current user's data (username, role, etc.), fetched from the `/api/auth/me` endpoint.
-   **Login/Register Handlers**: These event handlers now call the `api_client`, and upon a successful response, they update the `token` and `user_info` state variables.
-   **`check_auth`**: This `on_load` handler is critical. It validates the token with the backend, fetches user info, and enforces routing rules (e.g., redirecting unauthenticated users from protected pages).

---

### 4. Adding a New Feature (Example)

Let's say you want to add a feature to fetch a list of departments.

1.  **Backend First**: Create the `/api/departments` endpoint in your FastAPI backend.

2.  **Add to API Client** (`app/api_client.py`):
    
    async def get_departments(self) -> list[dict]:
        response = await self._request("get", "/api/departments")
        return response.json()
    

3.  **Add to State** (`app/states/admin_state.py`):
    
    class AdminState(rx.State):
        # ... other vars
        departments: list[dict] = []
        is_departments_loading: bool = False

        @rx.event
        async def load_departments(self):
            self.is_departments_loading = True
            try:
                api_client = get_api_client()
                self.departments = await api_client.get_departments()
            except Exception:
                return rx.toast.error("Failed to load departments.")
            finally:
                self.is_departments_loading = False
    

4.  **Use in UI**:
    -   Call `AdminState.load_departments` in an `on_mount` or `on_click` event.
    -   Use `rx.cond(AdminState.is_departments_loading, ...)` to show a spinner.
    -   Use `rx.foreach(AdminState.departments, ...)` to display the data.
