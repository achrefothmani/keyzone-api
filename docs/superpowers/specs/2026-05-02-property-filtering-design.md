# Design Spec: Dynamic Property Filtering

## Overview
Add a robust and flexible filtering system to the `/properties` endpoint. The system will support both a single `filter` query parameter (JSON) and individual query parameters for all relevant fields in the `Property` model.

## User Requirements
- Filter by "all fields" in the property model.
- Support both a single query parameter (JSON) or multiple individual parameters.
- Handle ranges for numerical fields (price, surface, rooms, etc.).

## Proposed Changes

### 1. Schema: `PropertyFilter` expansion
Expand `app/schemas/property.py` to include:
- **String Filters (Partial Match):** `title`, `neighborhood`, `postal_code`, `owner_name`, `owner_phone`, `owner_email`.
- **Exact Match:** `validation`, `currency`, `furnished`.
- **Range Filters:** 
    - `min_price` / `max_price`
    - `min_surface` / `max_surface`
    - `min_rooms` / `max_rooms`
    - `min_bedrooms` / `max_bedrooms`
    - `min_bathrooms` / `max_bathrooms`
    - `min_floor` / `max_floor`
- **Existing:** `reference`, `type`, `vocation`, `status`, `city`, `responsible_id`, `search`, `sort_by`, `sort_dir`.

### 2. Dependency: `get_property_filters`
Create a dependency in `app/api/deps.py` to:
1. Parse the optional `filter` JSON string.
2. Extract individual query parameters that match `PropertyFilter` fields.
3. Merge them, with individual parameters taking precedence over the JSON blob.
4. Return a validated `PropertyFilter` object.

### 3. Repository: Dynamic Query Building
Refactor `PropertyRepository.list` in `app/repositories/property_repository.py`:
- Iterate through the `PropertyFilter` fields.
- Dynamically apply SQLAlchemy filters based on field type (exact, like, range).
- Ensure the count query remains synchronized with the item query.

### 4. Route: Clean Interface
Simplify `@router.get("")` in `app/api/v1/routes/properties.py` to use the new dependency, removing the long list of explicit parameters.

## Verification Plan
### Automated Tests
- **Unit Tests:** Test the filter parsing logic in `deps.py` with various combinations of JSON and individual params.
- **Integration Tests:** 
    - Verify filtering by a single JSON blob.
    - Verify filtering by individual params.
    - Verify range filters (e.g., `min_rooms=2&max_rooms=4`).
    - Verify string search filters.
    - Verify sorting and pagination with filters.

### Manual Verification
- Use Swagger UI (`/docs`) to test the new dynamic filters.
- Verify through logs that the SQL queries are generated correctly.
