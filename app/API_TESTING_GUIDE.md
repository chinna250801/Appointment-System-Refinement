
# API Testing and Troubleshooting Guide

This guide provides instructions for testing the backend API endpoints and troubleshooting common issues. Since Reflex integrates the backend and frontend, testing is done through frontend interactions that trigger backend event handlers.

---

### 1. Backend API URL

The backend API is served on the same domain as the frontend. All API calls are routed through `/api`. **Do not use hardcoded URLs like `http://127.0.0.1:8000`**. Reflex handles the routing automatically.

-   **Endpoint Example:** A call to an event handler `my_event` in `MyState` is made to `/api/events/MyState.my_event`.

---

### 2. Testing Authentication Endpoints

Authentication is the most critical API feature. Use the application's UI to test it.

#### A. Patient Registration (`/patient/register`)

1.  **Navigate** to `/patient/register`.
2.  **Test Success Case:**
    -   Enter a unique username, a valid email, and a password.
    -   Click "Create Account".
    -   **Expected Result:** You should be redirected to `/patient/dashboard`, and a success toast may appear. The browser's cookies should now contain a `token`.
3.  **Test Failure Case (User Exists):**
    -   Use the same username or email from the previous test.
    -   Click "Create Account".
    -   **Expected Result:** An error toast `Username already taken` or `Email already registered` should appear. You should remain on the registration page.
4.  **Test Failure Case (Missing Fields):**
    -   Leave a required field (username, email, password) blank.
    -   Click "Create Account".
    -   **Expected Result:** An error toast `Username, email, and password are required` should appear.

#### B. Patient/Staff Login (`/patient/login`, `/staff/login`)

1.  **Navigate** to the appropriate login page.
2.  **Test Success Case:**
    -   Enter the credentials of a valid, existing user with the correct role.
    -   Click "Login".
    -   **Expected Result:** You should be redirected to the corresponding dashboard (`/patient/dashboard`, `/admin/dashboard`, or `/doctor/dashboard`).
3.  **Test Failure Case (Invalid Credentials):**
    -   Enter an incorrect username or password.
    -   Click "Login".
    -   **Expected Result:** An error toast `Invalid credentials...` should appear.
4.  **Test Failure Case (Wrong Role):**
    -   Try to log in as a `PATIENT` on the `/staff/login` page.
    -   **Expected Result:** An error toast `Invalid credentials or not authorized` should appear.

---

### 3. Testing Protected Routes

Once logged in, the application's routing should be restricted based on role.

1.  **Log in** as an `ADMIN`.
2.  **Try to access** a patient-specific page, e.g., `/patient/dashboard`.
    -   **Expected Result:** You should be automatically redirected back to `/admin/dashboard`.
3.  **Log out.**
4.  **Try to access** a protected admin page, e.g., `/admin/dashboard`.
    -   **Expected Result:** You should be automatically redirected to the staff login page (`/staff/login`).

---

### 4. Troubleshooting Common API Issues

#### Issue: API Calls Not Responding / Timeouts

-   **Symptom:** Clicking a button does nothing, and no toast messages appear. The browser's network tab shows a pending or failed request to an `/api/events/...` endpoint.
-   **Possible Causes & Solutions:**
    1.  **Backend Server is Down:** Ensure the Reflex application is running. If deployed, check the hosting provider's logs (e.g., Fly.io, Reflex Hosting) for crashes.
    2.  **Database Connection Error:** The backend may have failed to connect to the database. Check the server logs for `sqlalchemy.exc.OperationalError` or similar database errors. See `DEPLOYMENT_CHECKLIST.md` for database setup.
    3.  **Error in Event Handler:** An unhandled exception might be occurring in the backend Python code. Check the server logs for a full Python traceback.

#### Issue: `422 Unprocessable Entity` Error

-   **Symptom:** The browser's network tab shows a `422` error for an API request.
-   **Possible Causes & Solutions:**
    1.  **Data Validation Failed:** The data sent from the frontend does not match the type hints in the event handler. For example, sending a string where an integer is expected.
    2.  **Incorrect Form Data:** Ensure `name` attributes on `rx.el.input` components match the keys expected in the `form_data` dictionary.

#### Issue: `500 Internal Server Error`

-   **Symptom:** The application shows a generic error, and the network tab confirms a `500` status code.
-   **Cause:** A critical, unhandled error occurred on the backend.
-   **Solution:** **ALWAYS check the server-side logs.** The logs will contain the full Python traceback, which points directly to the line of code causing the error.

