from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.models import Patient, User, Role
from ..database import get_async_session
from ..auth import get_current_user, get_staff_user, get_admin_user
from ..schemas import PatientResponse, PatientCreate, PatientUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[PatientResponse])
async def get_patients(
    current_user: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get all patients (staff only)"""
    try:
        result = await db.execute(select(Patient))
        patients = result.scalars().all()
        return [PatientResponse.model_validate(patient) for patient in patients]
    except Exception as e:
        logging.exception(f"Error fetching patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch patients",
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get patient by ID"""
    try:
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )
        if current_user.role == Role.PATIENT:
            if patient.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
        return PatientResponse.model_validate(patient)
    except HTTPException as e:
        logging.exception(f"HTTP Exception in get_patient: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error fetching patient {patient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch patient",
        )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update patient information"""
    try:
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )
        if current_user.role == Role.PATIENT:
            if patient.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
        update_data = patient_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        await db.commit()
        await db.refresh(patient)
        return PatientResponse.model_validate(patient)
    except HTTPException as e:
        logging.exception(f"HTTP Exception in update_patient: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error updating patient {patient_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update patient",
        )


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete patient (admin only)"""
    try:
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
            )
        await db.delete(patient)
        await db.commit()
        return {"message": "Patient deleted successfully"}
    except HTTPException as e:
        logging.exception(f"HTTP Exception in delete_patient: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error deleting patient {patient_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete patient",
        )