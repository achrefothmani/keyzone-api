from __future__ import annotations

from uuid import UUID

from sqlalchemy import cast, func, Integer, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.property import (
    Property,
    PropertyHistory,
    PropertyImage,
)
from app.schemas.property import PropertyFilter
from app.utils.reference import PREFIX


class PropertyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, property_id: UUID | str, include_history: bool = False) -> Property | None:
        if isinstance(property_id, str):
            try:
                property_id = UUID(property_id)
            except ValueError:
                return None
        stmt = (
            select(Property)
            .where(Property.id == property_id, Property.is_deleted.is_(False))
            .options(selectinload(Property.images))
        )
        if include_history:
            stmt = stmt.options(selectinload(Property.history).selectinload(PropertyHistory.user))
        
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_history(self, property_id: UUID) -> list[PropertyHistory]:
        stmt = (
            select(PropertyHistory)
            .where(PropertyHistory.property_id == property_id)
            .options(selectinload(PropertyHistory.user))
            .order_by(PropertyHistory.created_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def add_history(self, history: PropertyHistory) -> PropertyHistory:
        self.db.add(history)
        await self.db.flush()
        return history

    async def reference_exists(self, reference: str) -> bool:
        stmt = select(Property.id).where(Property.reference == reference)
        return (await self.db.execute(stmt)).first() is not None

    async def get_max_reference_number(self) -> int | None:
        """
        Retrieves the maximum numeric part of references that match the 'PREFIX[0-9]+' pattern.
        Used to generate the next reference number.
        """
        # PostgreSQL uses '~' for POSIX regex. SQLite needs 'REGEXP' which is often not enabled.
        # For cross-compatibility in tests, we could use a different approach, 
        # but here we follow the spec for PostgreSQL.
        op = "~"
        if self.db.bind.dialect.name == "sqlite":
            op = "REGEXP"

        # SQL substring is 1-based. If PREFIX is "P" (len 1), start at index 2.
        start_index = len(PREFIX) + 1
        regex_pattern = f"^{PREFIX}[0-9]+$"

        stmt = (
            select(func.max(cast(func.substring(Property.reference, start_index), Integer)))
            .where(Property.reference.op(op)(regex_pattern))
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def list(
        self,
        filters: PropertyFilter,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Property], int]:
        stmt = select(Property).where(Property.is_deleted.is_(False))
        count_stmt = select(func.count(Property.id)).where(Property.is_deleted.is_(False))

        # Dynamic mapping for filters
        exact_fields = {
            "type": Property.type,
            "vocation": Property.vocation,
            "status": Property.status,
            "validation": Property.validation,
            "currency": Property.currency,
            "furnished": Property.furnished,
            "rooms": Property.rooms,
            "bedrooms": Property.bedrooms,
            "bathrooms": Property.bathrooms,
            "floor": Property.floor,
            "responsible_id": Property.responsible_id,
        }
        
        string_fields = {
            "reference": Property.reference,
            "title": Property.title,
            "city": Property.city,
            "neighborhood": Property.neighborhood,
            "postal_code": Property.postal_code,
            "owner_name": Property.owner_name,
            "owner_phone": Property.owner_phone,
            "owner_email": Property.owner_email,
        }

        range_fields = {
            "min_price": (Property.price, lambda attr, val: attr >= val),
            "max_price": (Property.price, lambda attr, val: attr <= val),
            "min_surface": (Property.surface, lambda attr, val: attr >= val),
            "max_surface": (Property.surface, lambda attr, val: attr <= val),
            "min_rooms": (Property.rooms, lambda attr, val: attr >= val),
            "max_rooms": (Property.rooms, lambda attr, val: attr <= val),
            "min_bedrooms": (Property.bedrooms, lambda attr, val: attr >= val),
            "max_bedrooms": (Property.bedrooms, lambda attr, val: attr <= val),
            "min_bathrooms": (Property.bathrooms, lambda attr, val: attr >= val),
            "max_bathrooms": (Property.bathrooms, lambda attr, val: attr <= val),
            "min_floor": (Property.floor, lambda attr, val: attr >= val),
            "max_floor": (Property.floor, lambda attr, val: attr <= val),
        }

        filter_dict = filters.model_dump(exclude_unset=True)

        for field, value in filter_dict.items():
            if value is None:
                continue
            
            cond = None
            if field in exact_fields:
                cond = exact_fields[field] == value
            elif field in string_fields:
                cond = func.lower(string_fields[field]).like(f"%{str(value).lower()}%")
            elif field in range_fields:
                attr, op = range_fields[field]
                cond = op(attr, value)
            
            if cond is not None:
                stmt = stmt.where(cond)
                count_stmt = count_stmt.where(cond)

        if filters.search:
            pattern = f"%{filters.search.lower()}%"
            search_cond = or_(
                func.lower(Property.reference).like(pattern),
                func.lower(Property.title).like(pattern),
                func.lower(Property.description).like(pattern),
                func.lower(Property.address).like(pattern),
                func.lower(Property.city).like(pattern),
                func.lower(Property.neighborhood).like(pattern),
            )
            stmt = stmt.where(search_cond)
            count_stmt = count_stmt.where(search_cond)

        sort_col = {
            "price": Property.price,
            "created_at": Property.created_at,
            "updated_at": Property.updated_at,
        }.get(filters.sort_by, Property.created_at)
        sort_col = sort_col.desc() if filters.sort_dir == "desc" else sort_col.asc()

        stmt = (
            stmt.options(selectinload(Property.images))
            .order_by(sort_col)
            .limit(limit)
            .offset(offset)
        )
        items = (await self.db.execute(stmt)).unique().scalars().all()
        total = (await self.db.execute(count_stmt)).scalar_one()
        return list(items), int(total)

    async def add(self, prop: Property) -> Property:
        self.db.add(prop)
        await self.db.flush()
        return prop

    async def soft_delete(self, prop: Property) -> None:
        prop.is_deleted = True
        await self.db.flush()


class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, image_id: UUID | str) -> PropertyImage | None:
        if isinstance(image_id, str):
            try:
                image_id = UUID(image_id)
            except ValueError:
                return None
        return await self.db.get(PropertyImage, image_id)

    async def list_for_property(self, property_id: UUID) -> list[PropertyImage]:
        stmt = (
            select(PropertyImage)
            .where(PropertyImage.property_id == property_id)
            .order_by(PropertyImage.created_at.asc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def add(self, image: PropertyImage) -> PropertyImage:
        self.db.add(image)
        await self.db.flush()
        return image

    async def delete(self, image: PropertyImage) -> None:
        await self.db.delete(image)

    async def set_cover(self, property_id: UUID, image_id: UUID) -> None:
        # Unset existing cover(s) for this property
        await self.db.execute(
            update(PropertyImage)
            .where(PropertyImage.property_id == property_id)
            .values(is_cover=False)
        )
        # Set the new cover
        await self.db.execute(
            update(PropertyImage)
            .where(PropertyImage.id == image_id, PropertyImage.property_id == property_id)
            .values(is_cover=True)
        )
        await self.db.flush()
