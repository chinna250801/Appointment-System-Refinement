
# Deployment Checklist & Guide

This checklist ensures that all requirements are met before and during the deployment of the appointment system application.

---

### 1. Pre-Deployment Configuration

#### A. Environment Variables

The application relies on environment variables for security and configuration. Ensure these are set in your deployment environment (e.g., GitHub Secrets for CI/CD, Fly.io secrets, `.env` file).

-   `SECRET_KEY`: **(Required)** A long, random, and secret string used for signing JWT tokens. This MUST be set for production. You can generate one using `openssl rand -hex 32`.
-   `DATABASE_URL`: **(Required for Production)** The connection string for your production database (e.g., PostgreSQL).
    -   Example: `postgresql://user:password@host:port/dbname`
    -   For local development, this can be left unset to default to `sqlite:///reflex.db`.

#### B. `rxconfig.py`

-   **`app_name`**: Ensure the app name is set correctly.
-   **Plugins**: Verify that `rx.plugins.TailwindV3Plugin()` is included, as the entire UI depends on it.

#### C. `requirements.txt`

-   Ensure all necessary packages are listed.
-   For PostgreSQL, make sure `psycopg` or `psycopg-binary` is included.

---

### 2. Database Setup (Production)

A local SQLite database is not suitable for production. A PostgreSQL database is recommended.

#### A. Database Initialization

The database tables are defined by the SQLModel classes in `app/models.py`. However, the tables will not be created automatically on first run. You must use a migration tool like **Alembic**.

1.  **Initialize Alembic (one-time setup):**
    bash
    alembic init alembic
    
2.  **Configure Alembic:**
    -   Edit `alembic.ini` to point to your production `DATABASE_URL`.
    -   Edit `alembic/env.py` to import your SQLModel `metadata` object.
3.  **Create a Migration:**
    -   After any change to `app/models.py`, generate a new migration script:
    bash
    alembic revision --autogenerate -m "Create initial tables"
    
4.  **Apply the Migration:**
    -   Run the migration against the production database. This command should be part of your deployment script/pipeline.
    bash
    alembic upgrade head
    

**IMPORTANT:** Without running migrations, you will get an `(sqlite3.OperationalError) no such table: user` or similar error at runtime.

---

### 3. Deployment Process (Example with `reflex deploy`)

Reflex Hosting simplifies deployment.

1.  **Login to Reflex Hosting:**
    bash
    reflex login
    
2.  **Initialize Hosting (one-time):**
    bash
    reflex hosting init
    
3.  **Set Backend Secrets:**
    -   Use the Reflex Hosting dashboard or CLI to set the `SECRET_KEY` and `DATABASE_URL` for the backend.
4.  **Deploy:**
    bash
    reflex deploy
    
5.  **Check Logs:**
    -   After deployment, monitor the logs for any startup errors related to database connections or environment variables. Use the hosting provider's dashboard to view logs.

---

### 4. Post-Deployment Checks

1.  **Public Pages:**
    -   Can you access the landing page (`/`)?
    -   Can you access the login/register pages?
2.  **Registration and Login:**
    -   Can you create a new patient account?
    -   Can you log in with an existing account?
3.  **Protected Routes:**
    -   Are you correctly redirected to your dashboard after login?
    -   Are you blocked from accessing pages not associated with your role?
4.  **API Functionality:**
    -   Test a core feature, like an admin viewing the list of patients. Does the data load? This confirms the database connection is working.

