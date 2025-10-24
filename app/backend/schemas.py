from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date, time
from app.models import Role, AppointmentStatus


class UserBase(BaseModel):
    username: str
    role: Role


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role = Role.PATIENT


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None


class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class DoctorBase(BaseModel):
    name: str
    specialization: str
    contact_info: Optional[str] = None
    department_id: Optional[int] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    contact_info: Optional[str] = None
    department_id: Optional[int] = None


class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    department: Optional[DepartmentResponse] = None

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    doctor_id: int
    patient_id: int


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[AppointmentStatus] = None


class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    doctor: Optional[DoctorResponse] = None
    patient: Optional[PatientResponse] = None

    class Config:
        from_attributes = True


class AvailabilityBase(BaseModel):
    weekday: int
    start_time: time
    end_time: time
    slot_duration: int


class AvailabilityCreate(AvailabilityBase):
    doctor_id: int


class AvailabilityUpdate(BaseModel):
    weekday: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration: Optional[int] = None


class AvailabilityResponse(AvailabilityBase):
    id: int
    doctor_id: int

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_patients: int
    total_doctors: int
    total_appointments: int
    pending_appointments: int
    completed_appointments: int
    cancelled_appointments: int