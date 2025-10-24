
# Quick Start Guide - Appointment System Backend

This guide will get your appointment system up and running in 5 minutes.

## 🚀 Prerequisites

- Python 3.10+
- PostgreSQL (or SQLite for development)
- Git

## ⚡ Quick Setup

### 1. Environment Setup

bash
# Copy environment template
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32

# Edit .env file and set:
# - DATABASE_URL (PostgreSQL recommended)
# - SECRET_KEY (use the generated key above)
# - CORS_ORIGINS (add your frontend URL)


### 2. Start Backend Server

bash
# Navigate to app directory
cd app

# Start the FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000


The backend will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Create Admin User

In a new terminal:

bash
# Create your first admin user
python -m app.backend.create_admin


Follow the prompts to create an admin account.

### 4. Start Frontend

In a new terminal (from root directory):

bash
# Start the Reflex frontend
reflex run


Frontend will be available at: **http://localhost:3000**

## 🎯 Test Your Setup

1. Open http://localhost:3000
2. Click "Staff Portal"
3. Login with your admin credentials
4. You should see the admin dashboard!

## 📡 API Endpoints

Your backend now provides these endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Patient registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Admin Management
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/users` - List all users

### Patient Management
- `GET /api/patients` - List patients (ADMIN/DOCTOR)
- `GET /api/patients/{id}` - Get patient details
- `PUT /api/patients/{id}` - Update patient
- `DELETE /api/patients/{id}` - Delete patient

### Doctor Management
- `GET /api/doctors` - List doctors
- `POST /api/doctors` - Create doctor (ADMIN)
- `GET /api/doctors/{id}` - Get doctor details
- `PUT /api/doctors/{id}` - Update doctor (ADMIN)
- `DELETE /api/doctors/{id}` - Delete doctor (ADMIN)

### Department Management
- `GET /api/departments` - List departments
- `POST /api/departments` - Create department (ADMIN)
- `GET /api/departments/{id}` - Get department details
- `PUT /api/departments/{id}` - Update department (ADMIN)
- `DELETE /api/departments/{id}` - Delete department (ADMIN)

### Appointment Management
- `GET /api/appointments` - List appointments (role-filtered)
- `POST /api/appointments` - Create appointment
- `GET /api/appointments/{id}` - Get appointment details
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

## 🔐 Role-Based Access

- **ADMIN**: Full access to all endpoints
- **DOCTOR**: Access to patients and appointments
- **PATIENT**: Access to own appointments and profile

## 🛠️ Development

- **Hot Reload**: Backend auto-reloads on code changes
- **API Docs**: Available at http://localhost:8000/docs
- **Database**: Automatically creates tables on startup
- **Logging**: Built-in request/error logging

## 🐛 Troubleshooting

**Backend won't start?**
- Check your DATABASE_URL in .env
- Ensure PostgreSQL is running
- Verify SECRET_KEY is set

**Can't create admin?**
- Make sure backend is running first
- Check database connection
- Verify you're in the correct directory

**Frontend can't connect?**
- Confirm BACKEND_API_URL in .env
- Check CORS_ORIGINS includes frontend URL
- Verify both servers are running

## 📚 Next Steps

- Read `app/backend/README.md` for detailed documentation
- Check `app/backend/DEPLOYMENT.md` for production setup
- Explore the API at http://localhost:8000/docs

---

**🎉 Your appointment system backend is now running!**

