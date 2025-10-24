from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from app.models import Appointment, Patient, Doctor, User, Role
from ..database import get_async_session
from ..auth import get_current_user, get_staff_user
from ..schemas import AppointmentResponse, AppointmentCreate, AppointmentUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[AppointmentResponse])
async def get_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get appointments based on user role"""
    try:
        query = select(Appointment).options(
            selectinload(Appointment.doctor), selectinload(Appointment.patient)
        )
        if current_user.role == Role.PATIENT:
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == current_user.id)
            )
            patient = patient_result.scalar_one_or_none()
            if patient:
                query = query.where(Appointment.patient_id == patient.id)
            else:
                return []
        elif current_user.role == Role.DOCTOR:
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == current_user.id)
            )
            doctor = doctor_result.scalar_one_or_none()
            if doctor:
                query = query.where(Appointment.doctor_id == doctor.id)
            else:
                return []
        result = await db.execute(query)
        appointments = result.scalars().all()
        return [
            AppointmentResponse.model_validate(appointment)
            for appointment in appointments
        ]
    except Exception as e:
        logging.exception(f"Error fetching appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch appointments",
        )


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Create new appointment"""
    try:
        doctor_result = await db.execute(
            select(Doctor).where(Doctor.id == appointment_data.doctor_id)
        )
        doctor = doctor_result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found"
            )
        if current_user.role == Role.PATIENT:
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == current_user.id)
            )
            patient = patient_result.scalar_one_or_none()
            if not patient or patient.id != appointment_data.patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Can only book appointments for yourself",
                )
        patient_result = await db.execute(
            select(Patient).where(Patient.id == appointment_data.patient_id)
        )
        patient = patient_result.scalar_one_or_none()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )
        appointment = Appointment(**appointment_data.model_dump())
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment, ["doctor", "patient"])
        return AppointmentResponse.model_validate(appointment)
    except HTTPException as e:
        logging.exception(f"HTTP Exception in create_appointment: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error creating appointment: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create appointment",
        )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get appointment by ID"""
    try:
        result = await db.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.doctor), selectinload(Appointment.patient)
            )
            .where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
            )
        if current_user.role == Role.PATIENT:
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == current_user.id)
            )
            patient = patient_result.scalar_one_or_none()
            if not patient or appointment.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
        elif current_user.role == Role.DOCTOR:
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == current_user.id)
            )
            doctor = doctor_result.scalar_one_or_none()
            if not doctor or appointment.doctor_id != doctor.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
        return AppointmentResponse.model_validate(appointment)
    except HTTPException as e:
        logging.exception(f"HTTP Exception in get_appointment: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error fetching appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch appointment",
        )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update appointment"""
    try:
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
            )
        if current_user.role == Role.PATIENT:
            patient_result = await db.execute(
                select(Patient).where(Patient.user_id == current_user.id)
            )
            patient = patient_result.scalar_one_or_none()
            if not patient or appointment.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
        elif current_user.role == Role.DOCTOR:
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == current_user.id)
            )
            doctor = doctor_result.scalar_one_or_none()
            if not doctor or appointment.doctor_id != doctor.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
        update_data = appointment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)
        await db.commit()
        await db.refresh(appointment, ["doctor", "patient"])
        return AppointmentResponse.model_validate(appointment)
    except HTTPException as e:
        logging.exception(f"HTTP Exception in update_appointment: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error updating appointment {appointment_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update appointment",
        )


@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    current_user: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete appointment (staff only)"""
    try:
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found"
            )
        await db.delete(appointment)
        await db.commit()
        return {"message": "Appointment deleted successfully"}
    except HTTPException as e:
        logging.exception(f"HTTP Exception in delete_appointment: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error deleting appointment {appointment_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete appointment",
        )