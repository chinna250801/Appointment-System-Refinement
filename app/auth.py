import reflex as rx
from typing import Any
import time
import jwt
import bcrypt
import logging
from app.models import Role, User, Patient
from sqlmodel import select

SECRET_KEY = "YOUR_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, str | int] | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        logging.exception("Token verification failed")
        return None


class AuthState(rx.State):
    token: str = rx.Cookie("")
    user_info: dict[str, str | int] = {}

    @rx.var
    def is_authenticated(self) -> bool:
        return self.token != "" and self.user_info != {}

    @rx.var
    def user_role(self) -> Role | None:
        role = self.user_info.get("role")
        return Role(role) if role else None

    async def _update_user_info_from_token(self):
        if self.token:
            payload = verify_token(self.token)
            if payload and payload.get("sub"):
                async with rx.asession() as session:
                    result = await session.exec(
                        select(User).where(User.username == payload["sub"])
                    )
                    user = result.one_or_none()
                    if user:
                        self.user_info = {
                            "id": user.id,
                            "username": user.username,
                            "role": user.role.value,
                        }
                        return
        self.logout()

    @rx.event
    def logout(self):
        self.token = ""
        self.user_info = {}
        return rx.redirect("/")

    @rx.event
    async def check_auth(self):
        if not self.is_authenticated and self.token:
            await self._update_user_info_from_token()
        current_path = self.router.page.path
        public_paths = ["/", "/staff/login", "/patient/login", "/patient/register"]
        auth_pages = ["/staff/login", "/patient/login", "/patient/register"]
        if not self.is_authenticated and current_path not in public_paths:
            if current_path.startswith("/admin") or current_path.startswith("/doctor"):
                return rx.redirect("/staff/login")
            if current_path.startswith("/patient"):
                return rx.redirect("/patient/login")
            return rx.redirect("/")
        if self.is_authenticated:
            role = self.user_role
            if current_path == "/" or current_path in auth_pages:
                if role == Role.ADMIN:
                    return rx.redirect("/admin/dashboard")
                elif role == Role.DOCTOR:
                    return rx.redirect("/doctor/dashboard")
                elif role == Role.PATIENT:
                    return rx.redirect("/patient/dashboard")
            if role == Role.ADMIN and (not current_path.startswith("/admin")):
                return rx.redirect("/admin/dashboard")
            elif role == Role.DOCTOR and (not current_path.startswith("/doctor")):
                return rx.redirect("/doctor/dashboard")
            elif role == Role.PATIENT and (not current_path.startswith("/patient")):
                return rx.redirect("/patient/dashboard")

    @rx.event
    async def staff_login(self, form_data: dict):
        username = form_data.get("username")
        password = form_data.get("password")
        if not username or not password:
            return rx.toast.error("Username and password are required.")
        async with rx.asession() as session:
            result = await session.exec(select(User).where(User.username == username))
            user = result.one_or_none()
            if (
                user
                and verify_password(password, user.password)
                and (user.role in [Role.ADMIN, Role.DOCTOR])
            ):
                self.token = create_access_token(
                    {"sub": user.username, "role": user.role.value}
                )
                self.user_info = {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                }
                if user.role == Role.ADMIN:
                    return rx.redirect("/admin/dashboard")
                return rx.redirect("/doctor/dashboard")
            return rx.toast.error("Invalid credentials or not authorized.")

    @rx.event
    async def patient_login(self, form_data: dict):
        username = form_data.get("username")
        password = form_data.get("password")
        if not username or not password:
            return rx.toast.error("Username and password are required.")
        async with rx.asession() as session:
            result = await session.exec(select(User).where(User.username == username))
            user = result.one_or_none()
            if (
                user
                and verify_password(password, user.password)
                and (user.role == Role.PATIENT)
            ):
                self.token = create_access_token(
                    {"sub": user.username, "role": user.role.value}
                )
                self.user_info = {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                }
                return rx.redirect("/patient/dashboard")
            return rx.toast.error("Invalid credentials or not a patient account.")

    @rx.event
    async def patient_register(self, form_data: dict):
        username = form_data.get("username")
        email = form_data.get("email")
        phone = form_data.get("phone")
        password = form_data.get("password")
        if not all([username, email, password]):
            return rx.toast.error("Username, email, and password are required.")
        async with rx.asession() as session:
            user_exists = (
                await session.exec(select(User).where(User.username == username))
            ).one_or_none()
            if user_exists:
                return rx.toast.error("Username already taken.")
            email_exists = (
                await session.exec(select(Patient).where(Patient.email == email))
            ).one_or_none()
            if email_exists:
                return rx.toast.error("Email already registered.")
            hashed_pass = hash_password(password)
            new_user = User(username=username, password=hashed_pass, role=Role.PATIENT)
            session.add(new_user)
            await session.flush()
            new_patient = Patient(
                name=username, email=email, phone=phone, user_id=new_user.id
            )
            session.add(new_patient)
            await session.commit()
            self.token = create_access_token(
                {"sub": new_user.username, "role": new_user.role.value}
            )
            self.user_info = {
                "id": new_user.id,
                "username": new_user.username,
                "role": new_user.role.value,
            }
            return rx.redirect("/patient/dashboard")