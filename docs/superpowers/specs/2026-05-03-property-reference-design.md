# Design Spec - Sequential Property Reference (P1xxx)

This specification outlines the implementation of a sequential property reference system using the format `P<number>`, starting from `P1000`.

## 1. Purpose
Replace the current random hex-based property references (`KZ-XXXXXX`) with a sequential numbering system that is more human-readable and follows a specific business format.

## 2. Requirements
- Format: `P` followed by an auto-incrementing number.
- Start value: 1000 (first reference: `P1000`).
- Handle growth: Must support 4, 5, or 6+ digits (e.g., `P9999` -> `P10000`).
- Uniqueness: References must remain unique in the database.

## 3. Architecture & Implementation

### 3.1 Utility Layer (`app/utils/reference.py`)
- Centralize the prefix in a constant `PREFIX = "P"`.
- Provide `format_reference(number: int) -> str` with runtime validation (must be positive integer).
- Provide `generate_reference() -> str` as a fallback return `P-{hex}`.

### 3.2 Repository Layer (`PropertyRepository`)
- Add `get_max_reference_number() -> int | None` to retrieve the highest existing numeric suffix for references starting with "P".
- **Query logic:**
  - Use regex `^P[0-9]+$` to filter sequential references.
  - Use substring and cast to extract the integer.
  - Support PostgreSQL (`~`) and SQLite (`REGEXP`) for test compatibility.

### 3.3 Service Layer (`PropertyService`)
- Update `_ensure_unique_reference` to implement the sequential logic.
- **New algorithm:**
  1. Fetch `max_num` from repository.
  2. If `max_num` is `None`, use `1000`.
  3. Else, use `max_num + 1`.
  4. Format as `P<number>`.
  5. Check for existence (safety check).
  6. Return the reference.
- Maintain the 10-attempt retry loop to handle concurrency collisions.

## 4. Testing Strategy
- **Unit Tests:** Verify formatting and validation in `tests/test_reference_utils.py`.
- **Repository Tests:** Verify `get_max_reference_number` handles empty DB, mixed formats, and gaps in `tests/test_property_repo_max_ref.py`.
- **Integration Tests:** Verify end-to-end creation flow in `tests/test_sequential_reference.py`.
