async def _make_property(client, **overrides):
    payload = {
        "title": "Villa S+4 avec piscine",
        "type": "Villa",
        "vocation": "Vente",
        "status": "Disponible",
        "price": 1850000,
        "city": "La Marsa",
        "neighborhood": "Marsa Plage",
        "rooms": 6,
        "bedrooms": 4,
        "bathrooms": 3,
        "surface": 320,
        "furnished": False,
    }
    payload.update(overrides)
    r = await client.post("/api/v1/properties", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


async def test_create_property_assigns_reference(authed_client):
    prop = await _make_property(authed_client)
    assert prop["reference"].startswith("P")
    assert prop["reference"][1:].isdigit()
    assert prop["currency"] == "TND"
    assert prop["validation"] == "Brouillon"


async def test_filter_by_city_and_price(authed_client):
    await _make_property(authed_client, city="Tunis", price=4200, vocation="Location")
    await _make_property(authed_client, city="La Marsa", price=1850000)

    r = await authed_client.get(
        "/api/v1/properties",
        params={"city": "Tunis", "max_price": 5000},
    )
    assert r.status_code == 200
    page = r.json()
    assert page["total"] == 1
    assert page["items"][0]["city"] == "Tunis"


async def test_update_and_soft_delete(authed_client):
    prop = await _make_property(authed_client)
    pid = prop["id"]

    r = await authed_client.put(
        f"/api/v1/properties/{pid}",
        json={"status": "Réservé", "validation": "Validée"},
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["status"] == "Réservé"
    assert updated["validation"] == "Validée"

    r = await authed_client.delete(f"/api/v1/properties/{pid}")
    assert r.status_code == 204

    r = await authed_client.get(f"/api/v1/properties/{pid}")
    assert r.status_code == 404


async def test_validation_restriction_for_agents(agent_client):
    # 1. Create property
    prop = await _make_property(agent_client)
    pid = prop["id"]

    # 2. Agent tries to update validation (forbidden)
    r = await agent_client.put(
        f"/api/v1/properties/{pid}",
        json={"validation": "Validée"},
    )
    assert r.status_code == 403
    assert "Seuls les coordinateurs ou chefs d'agence" in r.json()["detail"]


async def test_agent_can_update_other_fields(agent_client):
    prop = await _make_property(agent_client)
    pid = prop["id"]

    r = await agent_client.put(
        f"/api/v1/properties/{pid}",
        json={"title": "Updated Title"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"


async def test_chef_can_update_validation(authed_client):
    prop = await _make_property(authed_client)
    pid = prop["id"]

    r = await authed_client.put(
        f"/api/v1/properties/{pid}",
        json={"validation": "Validée"},
    )
    assert r.status_code == 200
    assert r.json()["validation"] == "Validée"


async def test_coordinator_can_update_validation(coordinator_client):
    prop = await _make_property(coordinator_client)
    pid = prop["id"]

    r = await coordinator_client.put(
        f"/api/v1/properties/{pid}",
        json={"validation": "Validée"},
    )
    assert r.status_code == 200
    assert r.json()["validation"] == "Validée"


async def test_property_images(authed_client):
    prop = await _make_property(authed_client)
    pid = prop["id"]

    r = await authed_client.post(
        f"/api/v1/properties/{pid}/images",
        json={"url": "https://cdn.example.com/a.jpg", "is_cover": True},
    )
    assert r.status_code == 201
    image = r.json()

    r = await authed_client.get(f"/api/v1/properties/{pid}/images")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = await authed_client.delete(f"/api/v1/images/{image['id']}")
    assert r.status_code == 204

    r = await authed_client.get(f"/api/v1/properties/{pid}/images")
    assert r.json() == []


