from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from app.models import Doctor, Department, User, Role
from ..database import get_async_session
from ..auth import get_current_user, get_staff_user, get_admin_user
from ..schemas import DoctorResponse, DoctorCreate, DoctorUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[DoctorResponse])
async def get_doctors(db: AsyncSession = Depends(get_async_session)):
    """Get all doctors"""
    try:
        result = await db.execute(
            select(Doctor).options(selectinload(Doctor.department))
        )
        doctors = result.scalars().all()
        return [DoctorResponse.model_validate(doc) for doc in doctors]
    except Exception as e:
        logging.exception(f"Error fetching doctors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch doctors",
        )


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_data: DoctorCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new doctor (admin only)"""
    try:
        doctor = Doctor.model_validate(doctor_data)
        db.add(doctor)
        await db.commit()
        await db.refresh(doctor, ["department"])
        return DoctorResponse.model_validate(doctor)
    except Exception as e:
        logging.exception(f"Error creating doctor: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create doctor",
        )


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: AsyncSession = Depends(get_async_session)):
    """Get a specific doctor by ID"""
    try:
        result = await db.execute(
            select(Doctor)
            .options(selectinload(Doctor.department))
            .where(Doctor.id == doctor_id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
            )
        return DoctorResponse.model_validate(doctor)
    except Exception as e:
        logging.exception(f"Error fetching doctor {doctor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch doctor",
        )


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_update: DoctorUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a doctor's information (admin only)"""
    try:
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
            )
        update_data = doctor_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(doctor, field, value)
        await db.commit()
        await db.refresh(doctor, ["department"])
        return DoctorResponse.model_validate(doctor)
    except Exception as e:
        logging.exception(f"Error updating doctor {doctor_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update doctor",
        )


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a doctor (admin only)"""
    try:
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
            )
        await db.delete(doctor)
        await db.commit()
    except Exception as e:
        logging.exception(f"Error deleting doctor {doctor_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete doctor",
        )