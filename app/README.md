
# Enterprise Appointment Booking System

A full-stack, enterprise-grade appointment booking system built entirely in Python, featuring a **Reflex** frontend and a **FastAPI** backend. This application provides a robust, multi-role platform for managing medical or service-based appointments, designed for administrators, doctors, and patients.

[![Project Status](https://img.shields.io/badge/status-65%25%20Complete-yellowgreen)](PROJECT_STATUS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features Overview

-   **Authentication & Authorization**: Secure JWT-based authentication with role-based access control (Admin, Doctor, Patient).
-   **Advanced Calendar Management**: Dynamically generate monthly appointment slots from weekly availability templates.
-   **Appointment Lifecycle**: Full support for booking, confirming, canceling, and completing appointments.
-   **Provider Availability**: Admins can configure provider schedules, including working days, hours, and slot durations.
-   **Department Organization**: Group providers into departments for better management.
-   **Audit Trail**: Track all significant actions with a detailed history log (coming soon).

## 🔧 Technology Stack

-   **Frontend**: [Reflex](https://reflex.dev/) `0.8.17` (Pure Python)
-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Async)
-   **Database**: PostgreSQL (Production) / SQLite (Development)
-   **Authentication**: JWT with `bcrypt` password hashing
-   **Styling**: [Tailwind CSS](https://tailwindcss.com/)

## 📊 Project Status

The project is approximately **65% complete**. The core backend API, frontend shell, state management, and calendar generation logic are fully functional.

-   **Phase 1-4 (App Shell, Backend, State, Calendar):** ✅ Complete
-   **Phase 5-7 (Booking Flow, Profiles, Admin CRUD):** 🚧 In Progress

For a detailed breakdown of completed features, remaining work, and project milestones, please see the **[Project Status Document](PROJECT_STATUS.md)**.

## 🚀 Quick Start

Follow these steps to get the application running locally.

bash
# 1. Install dependencies from the root directory
pip install -r requirements.txt

# 2. Start the backend server
# (Ensure you are in the root directory, then run the create_admin script)
python -m app.backend.create_admin
# Follow the prompts to create your admin user.
# Now, start the server:
uvicorn app.backend.main:app --reload --port 8000

# 3. Start the frontend application (in a new terminal)
reflex run


The frontend will be available at `http://localhost:3000`, and the backend API docs will be at `http://localhost:8000/docs`.

## 📚 Documentation

This project is extensively documented to help developers and users get started quickly.

| Document                                                | Description                                                   |
| ------------------------------------------------------- | ------------------------------------------------------------- |
| 📋 **[Project Plan](plan.md)**                          | The detailed, phased implementation plan for the entire system. |
| 📊 **[Project Status](PROJECT_STATUS.md)**               | A comprehensive report on current progress and achievements.    |
| 📖 **[User Guide](USER_GUIDE.md)**                      | Step-by-step instructions on how to use the system.           |
| 🏗️ **[Architecture Overview](ARCHITECTURE.md)**         | A deep dive into the system's technical design and decisions. |
| 📝 **[Executive Summary](SUMMARY.md)**                  | A concise, high-level overview of the project.                |
| 🔧 **[Backend README](app/backend/README.md)**          | Complete documentation for the FastAPI backend and its API.   |
| ⚡ **[Backend Quick Start](app/backend/QUICK_START.md)** | A 5-minute guide to setting up and running the backend.       |

## ✅ Key Features (Currently Working)

-   **User Authentication**: Patients can register, and all users can log in and out securely.
-   **Role-Based Access**: The app correctly redirects users to their respective dashboards (Admin, Doctor, Patient) and protects routes.
-   **Calendar Generation**: Admins can go to `/admin/calendar`, select a provider, and generate a full month of appointment slots from an availability template.
-   **Admin Dashboard**: A functional admin area with a sidebar for navigation.

## 🎯 Next Steps

The next priorities are to build out the remaining user-facing features:

1.  **Customer Booking Flow**: Implement the UI for patients to browse providers and book available slots.
2.  **Appointment Management**: Create pages for users to view and manage their upcoming and past appointments.
3.  **Profile Pages**: Build out detailed profile pages for customers and providers.
4.  **Admin CRUD Interfaces**: Complete the UI for managing departments, doctors, and patients.

## ⚙️ Environment Setup

The application requires the following environment variables to be set in a `.env` file in the root directory.

-   `DATABASE_URL`: The connection string for your database.
-   `SECRET_KEY`: A long, random string for signing JWT tokens.
-   `CORS_ORIGINS`: Comma-separated list of allowed frontend URLs (e.g., `http://localhost:3000`).
-   `BACKEND_API_URL`: The URL of the running backend (e.g., `http://localhost:8000`).

See `.env.example` for a template.

## 🤝 Contributing

Contributions are welcome! Please adhere to the following guidelines:

-   **Code Organization**: Follow the existing file structure and separation of concerns.
-   **Testing**: Ensure any new features are accompanied by appropriate tests.
-   **Documentation**: Update relevant documentation files with any changes.

Please open an issue to discuss any significant changes before starting work.

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## 💬 Support

If you encounter any issues or have questions, please open an issue on the project's GitHub repository. Be sure to check the existing documentation first.

