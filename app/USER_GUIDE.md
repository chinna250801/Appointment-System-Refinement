# Appointment Booking System - User Guide

This guide provides comprehensive instructions for setting up, using, and troubleshooting the Enterprise Appointment Booking System.

---

## 1. Getting Started

Follow these steps to get the system running on your local machine.

### System Requirements
- Python 3.10+
- PostgreSQL (Recommended for production) or SQLite (for development)
- A modern web browser (Chrome, Firefox, Safari)

### Installation
1.  **Clone the Repository**: Get the source code from the repository.
2.  **Install Dependencies**: Open your terminal in the project's root directory and run:
    bash
    pip install -r requirements.txt
    

### First-Time Setup

1.  **Configure Environment Variables**:
    -   Create a `.env` file in the root directory (you can copy `.env.example`).
    -   Set `DATABASE_URL`, `SECRET_KEY`, and `BACKEND_API_URL`.

2.  **Start the Backend Server**:
    -   The backend must be running before you can create an admin or start the frontend.
    -   Navigate to the `app` directory and run:
        bash
        uvicorn backend.main:app --reload --port 8000
        

3.  **Create an Admin User**:
    -   This step is crucial for managing the system.
    -   In a new terminal, from the root directory, run:
        bash
        python -m app.backend.create_admin
        
    -   Follow the on-screen prompts to set up your administrator account.

4.  **Start the Frontend Application**:
    -   In a new terminal, from the root directory, run:
        bash
        reflex run
        
    -   The application will be available at `http://localhost:3000`.

## 2. User Roles Overview

The system has three distinct user roles:

-   **Admin**: Has full access to the system. Admins can manage departments, doctors, patients, and view all appointments. They are responsible for generating calendars and configuring system settings.
-   **Doctor**: Can view their own schedule, manage their appointments, and access information for patients assigned to them.
-   **Patient**: Can register for an account, view provider availability, book new appointments, and manage their own upcoming appointments.

## 3. Authentication

-   **Staff Login (`/staff/login`)**: For Admins and Doctors. Use the credentials created during the admin setup or as created by an admin.
-   **Patient Login (`/patient/login`)**: For registered patients.
-   **Patient Registration (`/patient/register`)**: Allows new patients to create an account.
-   **Logout**: The logout button is available in the user sidebar/menu and will securely end the session.

## 4. Admin Features

After logging in as an Admin, you will be redirected to the `/admin/dashboard`.

### Calendar Management (`/admin/calendar`)
This is the core of the scheduling system.

1.  **Select a Provider**: Use the dropdown to choose which doctor's calendar you want to manage.
2.  **Navigate Months**: Use the `<` and `>` buttons to move between months.
3.  **Generate Availability**: Click the **"Generate Calendar"** button. A modal will appear where you can define the provider's weekly availability:
    -   Select the days of the week they work.
    -   Set their start and end times.
    -   Choose the duration for each appointment slot (e.g., 30 minutes).
4.  **Create Time Slots**: Click **"Generate Slots"** in the modal. The system will populate the calendar for the selected month with green "Available" slots based on your template.

### Other Admin Pages
-   **Patients**: View, add, edit, and delete patient records.
-   **Doctors**: Manage doctor profiles and system access.
-   **Departments**: Create and manage clinical or service departments.
-   **Appointments**: View a log of all appointments in the system.

## 5. Patient Features

1.  **Register**: Go to `/patient/register` and fill out the form to create an account.
2.  **Login**: Use your credentials at `/patient/login`.
3.  **Book an Appointment**: (Work in Progress) Patients will be able to browse providers, view their available slots on the calendar, and book an appointment.
4.  **Manage Appointments**: (Work in Progress) A patient dashboard will show upcoming and past appointments with options to cancel or reschedule.

## 6. Troubleshooting

#### "Could not load patients" Error

-   **Symptom**: You are on the staff login page, and a red toast notification appears saying "Could not load patients."
-   **Cause**: This happens because you are trying to access a protected page (like `/admin/dashboard` or `/admin/calendar`) without being logged in. The application tries to load data for that page, fails the authorization check, and redirects you to the login screen while the error message from the failed data fetch is briefly displayed.
-   **Solution**: This is expected behavior. Simply log in with your staff credentials, and you will be redirected to the correct page, which will then load its data successfully.

#### Login Issues
-   Ensure the backend server is running.
-   Double-check your username and password.
-   Make sure you are using the correct portal (Staff vs. Patient).

#### Backend Connection Errors
-   Make sure the backend is running on `http://localhost:8000`.
-   Verify the `BACKEND_API_URL` in your configuration is correct.

#### Port Already in Use
-   If you get an error that port `8000` or `3000` is in use, make sure you don't have another instance of the app running. You may need to stop the existing process before starting a new one.

## 7. Best Practices

-   **Startup Order**: Always start the backend server before the frontend.
-   **Admin First**: Always create an admin user on a fresh database setup.
-   **Environment Variables**: Do not hardcode sensitive information like `SECRET_KEY` or `DATABASE_URL`. Use environment variables.
