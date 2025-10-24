from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import logging
from app.models import User, Role, Patient
from ..database import get_async_session
from ..auth import hash_password, verify_password, create_access_token, get_current_user
from ..schemas import LoginResponse, RegisterRequest, UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    """Authenticate user and return access token"""
    try:
        result = await db.execute(
            select(User).where(User.username == form_data.username)
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        access_token_expires = timedelta(minutes=1440)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=access_token_expires,
        )
        return LoginResponse(
            access_token=access_token, user=UserResponse.model_validate(user)
        )
    except HTTPException as e:
        logging.exception(f"HTTP Exception in login: {e}")
        raise
    except Exception as e:
        logging.exception(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest, db: AsyncSession = Depends(get_async_session)
):
    """Register new patient account"""
    try:
        result = await db.execute(select(User).where(User.username == request.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )
        result = await db.execute(select(Patient).where(Patient.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed_password = hash_password(request.password)
        user = User(
            username=request.username, password=hashed_password, role=Role.PATIENT
        )
        db.add(user)
        await db.flush()
        patient = Patient(
            name=request.name, email=request.email, phone=request.phone, user_id=user.id
        )
        db.add(patient)
        await db.commit()
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value}
        )
        return LoginResponse(
            access_token=access_token, user=UserResponse.model_validate(user)
        )
    except HTTPException as e:
        logging.exception(f"HTTP Exception in register: {e}")
        raise
    except Exception as e:
        logging.exception(f"Registration error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Successfully logged out"}