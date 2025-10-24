from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging
from app.models import User, Patient, Doctor, Appointment, AppointmentStatus, Role
from ..database import get_async_session
from ..auth import get_admin_user
from ..schemas import DashboardStats, UserResponse
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get dashboard statistics (admin only)"""
    try:
        total_patients = await db.scalar(select(func.count(Patient.id)))
        total_doctors = await db.scalar(select(func.count(Doctor.id)))
        total_appointments = await db.scalar(select(func.count(Appointment.id)))
        pending_appointments = await db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.BOOKED
            )
        )
        completed_appointments = await db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.COMPLETED
            )
        )
        cancelled_appointments = await db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.CANCELLED
            )
        )
        return DashboardStats(
            total_patients=total_patients,
            total_doctors=total_doctors,
            total_appointments=total_appointments,
            pending_appointments=pending_appointments,
            completed_appointments=completed_appointments,
            cancelled_appointments=cancelled_appointments,
        )
    except Exception as e:
        logging.exception(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch dashboard stats",
        )


@router.get("/users", response_model=list[UserResponse])
async def get_users(
    role: Optional[Role] = None,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """List all users with optional role filtering (admin only)"""
    try:
        query = select(User)
        if role:
            query = query.where(User.role == role)
        result = await db.execute(query)
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]
    except Exception as e:
        logging.exception(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch users",
        )