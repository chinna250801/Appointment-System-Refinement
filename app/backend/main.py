from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
import logging
from .database import init_db
from .routers import auth, patients, appointments, doctors, departments, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Appointment System API",
    description="A comprehensive appointment management system",
    version="1.0.0",
    lifespan=lifespan,
)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(
    appointments.router, prefix="/api/appointments", tags=["appointments"]
)
app.include_router(doctors.router, prefix="/api/doctors", tags=["doctors"])
app.include_router(departments.router, prefix="/api/departments", tags=["departments"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Appointment System API is running"}


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Appointment System API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }