import asyncio
import logging

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_admin() -> None:
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        admin_email = settings.FIRST_SUPERUSER_EMAIL
        
        user = await repo.get_by_email(admin_email)
        if not user:
            logger.info(f"Creating admin user {admin_email}")
            user = User(
                nom="Admin",
                prenom="Keyzone",
                email=admin_email.lower(),
                hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
                role=UserRole.CHEF_AGENCE,
                is_active=True,
            )
            await repo.add(user)
            await session.commit()
            logger.info("Admin user created successfully")
        else:
            logger.info(f"Admin user {admin_email} already exists")

if __name__ == "__main__":
    asyncio.run(seed_admin())
