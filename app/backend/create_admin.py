import asyncio
import getpass
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, Doctor, Role
from app.backend.database import AsyncSessionLocal, engine
from app.backend.auth import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Creates an admin user and an associated doctor profile."""
    async with AsyncSessionLocal() as session:
        try:
            logger.info("--- Create Admin User ---")
            username = input("Enter admin username: ")
            result = await session.execute(
                select(User).where(User.username == username)
            )
            if result.scalar_one_or_none():
                logger.warning(f"User '{username}' already exists. Aborting.")
                return
            email = input("Enter admin email: ")
            name = input("Enter admin's full name: ")
            password = getpass.getpass("Enter password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                logger.error("Passwords do not match. Aborting.")
                return
            hashed_pass = hash_password(password)
            admin_user = User(username=username, password=hashed_pass, role=Role.ADMIN)
            session.add(admin_user)
            await session.flush()
            admin_doctor = Doctor(
                name=name,
                specialization="Administration",
                contact_info=email,
                user_id=admin_user.id,
            )
            session.add(admin_doctor)
            await session.commit()
            logger.info(f"\n✅ Admin user '{username}' created successfully!")
            logger.info(f"   - Name: {name}")
            logger.info(f"   - Email: {email}")
            logger.info(f"   - Role: {admin_user.role.value}")
        except Exception as e:
            await session.rollback()
            logger.exception(f"An error occurred during admin creation: {e}")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())