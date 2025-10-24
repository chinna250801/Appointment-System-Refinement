# Appointment System - FastAPI Backend

This is a standalone, reusable FastAPI backend for a comprehensive appointment management system. It provides a complete REST API for managing users, patients, doctors, departments, and appointments, with built-in authentication and role-based access control.

---

## ✨ Features

- **Authentication**: JWT-based authentication (Bearer tokens).
- **Role-Based Access Control (RBAC)**: `ADMIN`, `DOCTOR`, `PATIENT` roles with protected endpoints.
- **Database**: Asynchronous database operations with `SQLModel` and `SQLAlchemy`.
- **API Documentation**: Automatic, interactive API documentation with Swagger UI (`/docs`) and ReDoc (`/redoc`).
- **Data Validation**: Pydantic schemas for request and response validation.
- **CORS**: Configurable Cross-Origin Resource Sharing (CORS).
- **Async Support**: Fully asynchronous architecture for high performance.
- **Modularity**: Endpoints are organized into modular routers.

## ⚙️ Architecture

- **Framework**: **FastAPI**
- **ORM**: **SQLModel** (on top of SQLAlchemy and Pydantic)
- **Database**: PostgreSQL (recommended), compatible with SQLite for development.
- **Authentication**: `python-jose` for JWT and `bcrypt` for password hashing.
- **Server**: `Uvicorn` ASGI server.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL server (recommended for production)
- `pip` for package management

### 1. Installation

1.  **Clone the repository**.
2.  **Navigate to the project directory**.
3.  **Install dependencies**:
    bash
    pip install -r requirements.txt
    

### 2. Environment Variables

Create a `.env` file in the root directory of the project. You can copy the `.env.example` file to start.

bash
cp .env.example .env


**Fill in the `.env` file with your configuration:**

-   `DATABASE_URL`: Your database connection string.
    -   **PostgreSQL (Production):** `postgresql+asyncpg://user:password@host:port/dbname`
    -   **SQLite (Development):** `sqlite+aiosqlite:///./appointment_system.db`
-   `SECRET_KEY`: A secret key for JWT signing. Generate one with:
    bash
    openssl rand -hex 32
    
-   `CORS_ORIGINS`: Comma-separated list of allowed origins.
    -   Example: `http://localhost:3000,http://127.0.0.1:3000`

### 3. Database Setup

1.  **Create a PostgreSQL database** if you are using it.
2.  The backend will automatically create the necessary tables on its first run, based on the models in `app/models.py`.

### 4. Create an Admin User

Run the interactive script to create your first administrative user. This user is necessary to manage departments, doctors, etc.

bash
python -m app.backend.create_admin


Follow the prompts to set the username, email, name, and password.

### 5. Running the Backend

Start the development server using Uvicorn:

bash
cd app  # Navigate into the 'app' directory first
uvicorn backend.main:app --reload --port 8000


-   `--reload`: Automatically reloads the server on code changes.
-   `--port 8000`: Runs the server on port 8000.

## 📝 API Documentation

Once the server is running, you can access the interactive API documentation:

-   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
-   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Available Endpoints

-   **Authentication**: `/api/auth/` (`login`, `register`, `me`, `logout`)
-   **Admin**: `/api/admin/` (`dashboard/stats`, `users`)
-   **Patients**: `/api/patients/` (CRUD)
-   **Doctors**: `/api/doctors/` (CRUD)
-   **Departments**: `/api/departments/` (CRUD)
-   **Appointments**: `/api/appointments/` (CRUD)

## 🔒 Authentication Flow

1.  A user sends their credentials to `/api/auth/login`.
2.  The server validates the credentials and returns a JWT `access_token`.
3.  The frontend client stores this token (e.g., in a cookie or local storage).
4.  For all subsequent requests to protected endpoints, the client must include the token in the `Authorization` header:
    `Authorization: Bearer <your_token>`

## 🛡️ Role-Based Access Control (RBAC)

Access to certain endpoints is restricted by user role:

-   **`ADMIN`**: Full access to all endpoints, including user management and system-wide statistics.
-   **`DOCTOR`**: Can view their own appointments and patient information related to those appointments.
-   **`PATIENT`**: Can only view and manage their own appointments and personal information.

## 📈 Development Workflow

1.  Ensure the Uvicorn server is running with `--reload`.
2.  Modify the backend code in `app/backend/`.
3.  The server will automatically restart to apply changes.
4.  Test endpoint changes using the Swagger UI at `http://localhost:8000/docs`.

## 🚀 Production Deployment

For production, it is recommended to use a robust setup. See `DEPLOYMENT.md` for a detailed guide on deploying the backend.

## 🔧 Troubleshooting

-   **`sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server ... failed`**:
    -   Check if your `DATABASE_URL` is correct.
    -   Ensure your PostgreSQL server is running and accessible.
    -   Verify firewall rules are not blocking the connection.
-   **`401 Unauthorized`**: Your JWT is either missing, invalid, or expired. Try logging in again.
-   **`403 Forbidden`**: You are authenticated but do not have the required role to access the endpoint.
-   **`500 Internal Server Error`**: Check the Uvicorn server logs for a full Python traceback. This indicates a bug in the backend code.
