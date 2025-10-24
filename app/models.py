import reflex as rx
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
import datetime
import enum


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"


class AppointmentStatus(str, enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str
    role: Role
    doctor: Optional["Doctor"] = Relationship(back_populates="user")
    patient: Optional["Patient"] = Relationship(back_populates="user")


class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    doctors: list["Doctor"] = Relationship(back_populates="department")


class Doctor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    specialization: str
    contact_info: Optional[str] = None
    google_calendar_id: Optional[str] = None
    department_id: int = Field(foreign_key="department.id")
    department: "Department" = Relationship(back_populates="doctors")
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="doctor")
    appointments: list["Appointment"] = Relationship(back_populates="doctor")
    availabilities: list["Availability"] = Relationship(back_populates="doctor")


class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: Optional[str] = None
    email: str = Field(unique=True, index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="patient")
    appointments: list["Appointment"] = Relationship(back_populates="appointments")


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    status: AppointmentStatus = Field(default=AppointmentStatus.BOOKED)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    doctor_id: int = Field(foreign_key="doctor.id")
    doctor: "Doctor" = Relationship(back_populates="appointments")
    patient_id: int = Field(foreign_key="patient.id")
    patient: "Patient" = Relationship(back_populates="appointments")


class Availability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    weekday: int
    start_time: datetime.time
    end_time: datetime.time
    slot_duration: int
    doctor_id: int = Field(foreign_key="doctor.id")
    doctor: "Doctor" = Relationship(back_populates="availabilities")