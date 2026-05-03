from __future__ import annotations

import os
import uuid
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.property import Property, PropertyHistory, PropertyImage
from app.models.user import User, UserRole
from app.repositories.property_repository import ImageRepository, PropertyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.property import (
    PropertyCreate,
    PropertyFilter,
    PropertyImageCreate,
    PropertyUpdate,
)
from app.utils.reference import STARTING_REFERENCE_NUMBER, format_reference


class PropertyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PropertyRepository(db)
        self.user_repo = UserRepository(db)
        self.image_repo = ImageRepository(db)

    async def _validate_responsible(self, responsible_id: UUID | None) -> None:
        if responsible_id is None:
            return
        if not await self.user_repo.get(responsible_id):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Responsible user does not exist"
            )

    async def _add_history(
        self,
        property_id: UUID,
        user_id: UUID | None,
        action: str,
        changes: dict | None = None,
    ) -> None:
        history = PropertyHistory(
            property_id=property_id,
            user_id=user_id,
            action=action,
            changes=changes,
        )
        await self.repo.add_history(history)

    async def create(self, payload: PropertyCreate, current_user: User) -> Property:
        await self._validate_responsible(payload.responsible_id)

        if payload.validation != "Brouillon":
            if current_user.role not in [UserRole.CHEF_AGENCE, UserRole.COORDINATEUR]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Seuls les coordinateurs ou chefs d'agence peuvent modifier le champ Validation.",
                )

        data = payload.model_dump(exclude={"images", "reference"})
        
        # Determine initial candidates
        if payload.reference:
            # Short-circuit logic for provided reference
            if await self.repo.reference_exists(payload.reference):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Property reference already exists"
                )
            candidates = [payload.reference]
        else:
            # Dynamic candidate generation utilizing STARTING_REFERENCE_NUMBER
            max_num = await self.repo.get_max_reference_number()
            next_num = STARTING_REFERENCE_NUMBER if max_num is None else max_num + 1
            candidates = [format_reference(next_num + i) for i in range(10)]

        for ref in candidates:
            prop = Property(reference=ref, **data)
            for img in payload.images:
                prop.images.append(PropertyImage(url=img.url, is_cover=img.is_cover))

            await self.repo.add(prop)
            await self._add_history(prop.id, current_user.id, "CREATED")
            
            try:
                # TOCTOU mitigation: commit inside the loop and catch IntegrityError
                await self.db.commit()
                return await self._get_or_404(prop.id)
            except IntegrityError:
                await self.db.rollback()
                # Do not retry if the user explicitly provided a reference
                if payload.reference:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Property reference already exists"
                    )
                # Otherwise, continue loop to next candidate
                # This handles cases where another process took the same 'next_num'

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not allocate property reference"
        )

    async def list(
        self, filters: PropertyFilter, limit: int, offset: int
    ) -> tuple[list[Property], int]:
        return await self.repo.list(filters, limit, offset)

    async def get(self, property_id: UUID | str) -> Property:
        return await self._get_or_404(property_id)

    async def list_history(self, property_id: UUID) -> list[PropertyHistory]:
        await self._get_or_404(property_id)
        return await self.repo.list_history(property_id)

    async def update(
        self,
        property_id: UUID | str,
        payload: PropertyUpdate,
        current_user: User,
    ) -> Property:
        prop = await self._get_or_404(property_id)
        await self._validate_responsible(payload.responsible_id)

        update_data = payload.model_dump(exclude_unset=True)

        if "validation" in update_data and update_data["validation"] != prop.validation:
            if current_user.role not in [UserRole.CHEF_AGENCE, UserRole.COORDINATEUR]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Seuls les coordinateurs ou chefs d'agence peuvent modifier le champ Validation.",
                )

        changes = {}
        for field, value in update_data.items():
            old_value = getattr(prop, field)
            if old_value != value:
                # Basic normalization for JSON storage
                ser_old = str(old_value) if isinstance(old_value, (UUID, datetime)) else old_value
                ser_new = str(value) if isinstance(value, (UUID, datetime)) else value
                changes[field] = {"old": ser_old, "new": ser_new}
                setattr(prop, field, value)

        if changes:
            await self._add_history(prop.id, current_user.id, "UPDATED", changes)
            await self.db.commit()
        
        return await self._get_or_404(prop.id)

    async def delete(self, property_id: UUID | str, current_user: User) -> None:
        prop = await self._get_or_404(property_id)
        await self.repo.soft_delete(prop)
        await self._add_history(prop.id, current_user.id, "DELETED")
        await self.db.commit()

    async def add_image(
        self, property_id: UUID | str, payload: PropertyImageCreate, current_user: User
    ) -> PropertyImage:
        prop = await self._get_or_404(property_id)
        image = PropertyImage(
            property_id=prop.id, url=payload.url, is_cover=payload.is_cover
        )
        await self.image_repo.add(image)
        await self._add_history(prop.id, current_user.id, "IMAGE_ADDED", {"url": payload.url})
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def list_images(self, property_id: UUID | str) -> list[PropertyImage]:
        prop = await self._get_or_404(property_id)
        return await self.image_repo.list_for_property(prop.id)

    async def delete_image(self, image_id: UUID | str, current_user: User) -> None:
        image = await self.image_repo.get(image_id)
        if not image:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found")
        
        property_id = image.property_id
        await self.image_repo.delete(image)
        await self._add_history(property_id, current_user.id, "IMAGE_DELETED", {"url": image.url})
        await self.db.commit()

    async def upload_image(
        self, property_id: UUID | str, file: UploadFile, current_user: User, is_cover: bool = False
    ) -> PropertyImage:
        prop = await self._get_or_404(property_id)

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "File must be an image"
            )

        ext = os.path.splitext(file.filename or "")[1]
        if not ext:
            # Fallback for some browsers/files
            ext = ".jpg" if "jpeg" in file.content_type else f".{file.content_type.split('/')[-1]}"
        
        filename = f"{uuid.uuid4()}{ext}"
        relative_path = os.path.join("properties", filename)
        file_path = os.path.join(settings.UPLOAD_DIR, relative_path)

        try:
            with open(file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    f.write(chunk)
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Could not save file: {str(e)}"
            )

        public_url = f"{settings.BASE_URL}/uploads/{relative_path.replace(os.sep, '/')}"
        
        image = PropertyImage(
            property_id=prop.id,
            url=public_url,
            is_cover=is_cover
        )
        await self.image_repo.add(image)
        await self._add_history(prop.id, current_user.id, "IMAGE_ADDED", {"url": public_url})
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def set_image_as_cover(
        self, property_id: UUID | str, image_id: UUID | str, current_user: User
    ) -> PropertyImage:
        prop = await self._get_or_404(property_id)
        image = await self.image_repo.get(image_id)
        
        if not image or image.property_id != prop.id:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Image not found for this property"
            )
        
        await self.image_repo.set_cover(prop.id, image.id)
        
        await self._add_history(
            prop.id, 
            current_user.id, 
            "IMAGE_SET_AS_COVER", 
            {"url": image.url, "image_id": str(image.id)}
        )
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def _get_or_404(self, property_id: UUID | str) -> Property:
        prop = await self.repo.get(property_id)
        if not prop:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Property not found")
        return prop
