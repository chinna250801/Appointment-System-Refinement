from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.models import Department
from ..database import get_async_session
from ..auth import get_admin_user
from ..schemas import DepartmentResponse, DepartmentCreate, DepartmentUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[DepartmentResponse])
async def get_departments(db: AsyncSession = Depends(get_async_session)):
    """Get all departments"""
    try:
        result = await db.execute(select(Department))
        departments = result.scalars().all()
        return [DepartmentResponse.model_validate(dep) for dep in departments]
    except Exception as e:
        logging.exception(f"Error fetching departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch departments",
        )


@router.post(
    "/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(
    department_data: DepartmentCreate,
    current_user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new department (admin only)"""
    try:
        department = Department.model_validate(department_data)
        db.add(department)
        await db.commit()
        await db.refresh(department)
        return DepartmentResponse.model_validate(department)
    except Exception as e:
        logging.exception(f"Error creating department: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create department",
        )


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get a specific department by ID"""
    try:
        result = await db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )
        return DepartmentResponse.model_validate(department)
    except HTTPException as e:
        logging.exception(f"HTTP exception in get_department: {e}")
        raise
    except Exception as e:
        logging.exception(f"Error fetching department {department_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch department",
        )


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_update: DepartmentUpdate,
    current_user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a department (admin only)"""
    try:
        result = await db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )
        update_data = department_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        await db.commit()
        await db.refresh(department)
        return DepartmentResponse.model_validate(department)
    except Exception as e:
        logging.exception(f"Error updating department {department_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update department",
        )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    current_user=Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a department (admin only)"""
    try:
        result = await db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )
        await db.delete(department)
        await db.commit()
    except Exception as e:
        logging.exception(f"Error deleting department {department_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete department",
        )