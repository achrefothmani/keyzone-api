# Sequential Property Reference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement auto-incrementing property references in the format `P1xxx` starting from 1000.

**Architecture:** Use a "Max + 1" approach in the repository layer. Service layer handles incrementing and formatting.

---

### Task 1: Update Reference Utility [COMPLETED]
- [x] Step 1: Write tests for reference formatting.
- [x] Step 2: Implement `format_reference` with validation and `PREFIX` constant.
- [x] Step 3: Update `generate_reference` as fallback.

### Task 2: Add Repository Method for Max Reference [COMPLETED]
- [x] Step 1: Write integration test for `get_max_reference_number`.
- [x] Step 2: Implement `get_max_reference_number` with regex support for Postgres and SQLite.
- [x] Step 3: Update `tests/conftest.py` for SQLite regex support.

### Task 3: Refactor Service Layer Logic
**Files:**
- Modify: `app/services/property_service.py`
- Create: `tests/test_sequential_reference.py`

- [ ] **Step 1: Write integration test for sequential creation**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_sequential_reference_generation(client: AsyncClient, admin_token_headers):
    # Create first property
    data = {
        "title": "Prop 1", "type": "Appartement", "vocation": "Vente",
        "price": 100000, "city": "Tunis", "images": []
    }
    r1 = await client.post("/api/v1/properties/", json=data, headers=admin_token_headers)
    assert r1.status_code == 201
    assert r1.json()["reference"] == "P1000"

    # Create second property
    r2 = await client.post("/api/v1/properties/", json=data, headers=admin_token_headers)
    assert r2.status_code == 201
    assert r2.json()["reference"] == "P1001"
```

- [ ] **Step 2: Refactor `_ensure_unique_reference` in `app/services/property_service.py`**
Use `repo.get_max_reference_number()` and `format_reference()`.

- [ ] **Step 3: Run tests to verify it passes**
Run: `pytest tests/test_sequential_reference.py -v`

### Task 4: Final Validation and Cleanup
- [ ] **Step 1: Run all property tests**
- [ ] **Step 2: Check for any regressions**
