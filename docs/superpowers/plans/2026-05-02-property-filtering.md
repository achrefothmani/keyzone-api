# Dynamic Property Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a robust filtering system to `/properties` supporting both JSON and individual query parameters for all fields.

**Architecture:** 
1. Expand `PropertyFilter` schema.
2. Create a `get_property_filters` dependency to merge JSON and individual parameters.
3. Refactor `PropertyRepository.list` to build queries dynamically from the filter model.
4. Update route to use the new dependency.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy 2 (async).

---

### Task 1: Expand PropertyFilter Schema

**Files:**
- Modify: `app/schemas/property.py`

- [ ] **Step 1: Update PropertyFilter class**

```python
class PropertyFilter(BaseModel):
    reference: str | None = None
    title: str | None = None
    type: str | None = None
    vocation: str | None = None
    status: str | None = None
    validation: str | None = None
    currency: str | None = None
    city: str | None = None
    neighborhood: str | None = None
    postal_code: str | None = None
    furnished: bool | None = None
    
    # Ranges
    min_price: float | None = None
    max_price: float | None = None
    min_surface: float | None = None
    max_surface: float | None = None
    min_rooms: int | None = None
    max_rooms: int | None = None
    min_bedrooms: int | None = None
    max_bedrooms: int | None = None
    min_bathrooms: int | None = None
    max_bathrooms: int | None = None
    min_floor: int | None = None
    max_floor: int | None = None
    
    # Other
    responsible_id: UUID | None = None
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_email: str | None = None
    search: str | None = None
    sort_by: str = Field(default="created_at", pattern="^(price|created_at|updated_at)$")
    sort_dir: str = Field(default="desc", pattern="^(asc|desc)$")
```

- [ ] **Step 2: Commit**

```bash
git add app/schemas/property.py
git commit -m "feat(schemas): expand PropertyFilter with all fields and ranges"
```

---

### Task 2: Create Filter Dependency

**Files:**
- Modify: `app/api/deps.py`

- [ ] **Step 1: Implement get_property_filters**

```python
import json
from fastapi import Request, Query
from app.schemas.property import PropertyFilter

async def get_property_filters(
    request: Request,
    filter: str | None = Query(default=None, description="JSON string of filters")
) -> PropertyFilter:
    # 1. Parse JSON if present
    data = {}
    if filter:
        try:
            data = json.loads(filter)
        except json.JSONDecodeError:
            pass # Or raise HTTPException if you prefer strictness
            
    # 2. Merge with individual query params
    # We skip 'filter', 'limit', 'offset' as they are handled elsewhere
    skip_params = {"filter", "limit", "offset"}
    for key, value in request.query_params.items():
        if key not in skip_params and hasattr(PropertyFilter, key):
            data[key] = value
            
    return PropertyFilter.model_validate(data)
```

- [ ] **Step 2: Commit**

```bash
git add app/api/deps.py
git commit -m "feat(deps): add get_property_filters dependency for dual-style filtering"
```

---

### Task 3: Refactor Repository for Dynamic Filtering

**Files:**
- Modify: `app/repositories/property_repository.py`

- [ ] **Step 1: Refactor list method**

```python
    async def list(
        self,
        filters: PropertyFilter,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Property], int]:
        stmt = select(Property).where(Property.is_deleted.is_(False))
        count_stmt = select(func.count(Property.id)).where(Property.is_deleted.is_(False))

        # Dynamic mapping for filters
        # Exact match fields
        exact_fields = {
            "type": Property.type,
            "vocation": Property.vocation,
            "status": Property.status,
            "validation": Property.validation,
            "currency": Property.currency,
            "furnished": Property.furnished,
            "responsible_id": Property.responsible_id,
        }
        
        # String partial match fields
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

        # Range fields mapping (filter_attr -> (model_attr, operator))
        from sqlalchemy import gte, lte
        range_fields = {
            "min_price": (Property.price, gte),
            "max_price": (Property.price, lte),
            "min_surface": (Property.surface, gte),
            "max_surface": (Property.surface, lte),
            "min_rooms": (Property.rooms, gte),
            "max_rooms": (Property.rooms, lte),
            "min_bedrooms": (Property.bedrooms, gte),
            "max_bedrooms": (Property.bedrooms, lte),
            "min_bathrooms": (Property.bathrooms, gte),
            "max_bathrooms": (Property.bathrooms, lte),
            "min_floor": (Property.floor, gte),
            "max_floor": (Property.floor, lte),
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
                func.lower(Property.title).like(pattern),
                func.lower(Property.description).like(pattern),
                func.lower(Property.address).like(pattern),
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
```

- [ ] **Step 2: Commit**

```bash
git add app/repositories/property_repository.py
git commit -m "refactor(repo): implement dynamic query building in PropertyRepository.list"
```

---

### Task 4: Update Service and Route

**Files:**
- Modify: `app/services/property_service.py`
- Modify: `app/api/v1/routes/properties.py`

- [ ] **Step 1: Simplify PropertyService.list**

```python
    async def list(
        self, filters: PropertyFilter, limit: int, offset: int
    ) -> tuple[list[Property], int]:
        return await self.repo.list(filters, limit, offset)
```

- [ ] **Step 2: Simplify Route**

```python
@router.get("", response_model=Page[PropertyOut])
async def list_properties(
    db: DBSession,
    _: CurrentUser,
    filters: PropertyFilter = Depends(get_property_filters),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Page[PropertyOut]:
    items, total = await PropertyService(db).list(filters, limit, offset)
    return Page[PropertyOut](
        items=[PropertyOut.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )
```

- [ ] **Step 3: Commit**

```bash
git add app/services/property_service.py app/api/v1/routes/properties.py
git commit -m "feat(api): simplify property list route using dynamic filter dependency"
```

---

### Task 5: Verification

**Files:**
- Create: `tests/test_property_filters.py`

- [ ] **Step 1: Write integration tests**
Create tests verifying:
1. Individual params work.
2. JSON `filter` param works.
3. Ranges work (min/max).
4. Partial string matches work.

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_property_filters.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_property_filters.py
git commit -m "test: add integration tests for dynamic property filtering"
```
