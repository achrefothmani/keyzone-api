import json
import pytest

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

@pytest.mark.asyncio
async def test_filter_by_individual_parameters(authed_client):
    await _make_property(authed_client, city="Tunis", rooms=3, price=300000)
    await _make_property(authed_client, city="Sousse", rooms=4, price=400000)
    
    r = await authed_client.get("/api/v1/properties", params={"city": "Tunis", "rooms": 3})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["city"] == "Tunis"
    assert data["items"][0]["rooms"] == 3

@pytest.mark.asyncio
async def test_filter_by_furnished(authed_client):
    await _make_property(authed_client, furnished=True)
    await _make_property(authed_client, furnished=False)
    
    r = await authed_client.get("/api/v1/properties", params={"furnished": "true"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["furnished"] is True

@pytest.mark.asyncio
async def test_filter_by_json_blob(authed_client):
    await _make_property(authed_client, city="Tunis", rooms=3, price=300000)
    await _make_property(authed_client, city="Sousse", rooms=4, price=400000)
    
    filters = {"city": "Tunis", "rooms": 3}
    r = await authed_client.get("/api/v1/properties", params={"filter": json.dumps(filters)})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["city"] == "Tunis"
    assert data["items"][0]["rooms"] == 3

@pytest.mark.asyncio
async def test_filter_by_range(authed_client):
    await _make_property(authed_client, price=100000)
    await _make_property(authed_client, price=300000)
    await _make_property(authed_client, price=600000)
    
    r = await authed_client.get("/api/v1/properties", params={"min_price": 200000, "max_price": 500000})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["price"] == 300000

@pytest.mark.asyncio
async def test_filter_by_partial_reference(authed_client):
    p1 = await _make_property(authed_client, reference="P9001")
    await _make_property(authed_client, reference="OTHER-001")
    
    r = await authed_client.get("/api/v1/properties", params={"reference": "P90"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["reference"] == "P9001"

@pytest.mark.asyncio
async def test_filter_by_partial_city_neighborhood(authed_client):
    await _make_property(authed_client, city="Tunis", neighborhood="Carthage")
    await _make_property(authed_client, city="Sousse", neighborhood="Kantaoui")
    
    # Partial city
    r = await authed_client.get("/api/v1/properties", params={"city": "Tun"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert "Tunis" in data["items"][0]["city"]
    
    # Partial neighborhood
    r = await authed_client.get("/api/v1/properties", params={"neighborhood": "Carth"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert "Carthage" in data["items"][0]["neighborhood"]

@pytest.mark.asyncio
async def test_filter_by_search(authed_client):
    await _make_property(authed_client, title="Magnifique villa luxueuse", description="Une villa de luxe", city="Tunis", neighborhood="Carthage")
    await _make_property(authed_client, title="Appartement simple", description="Un petit appartement", city="Sousse", neighborhood="Kantaoui")
    
    # Search in title
    r = await authed_client.get("/api/v1/properties", params={"search": "luxueuse"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    
    # Search in city
    r = await authed_client.get("/api/v1/properties", params={"search": "Tunis"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    
    # Search in neighborhood
    r = await authed_client.get("/api/v1/properties", params={"search": "Carthage"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1

@pytest.mark.asyncio
async def test_filter_combination_json_and_params(authed_client):
    await _make_property(authed_client, city="Tunis", rooms=3, price=300000)
    await _make_property(authed_client, city="Tunis", rooms=5, price=500000)
    
    # city from JSON, rooms from query param
    r = await authed_client.get(
        "/api/v1/properties", 
        params={
            "filter": json.dumps({"city": "Tunis"}),
            "rooms": 3
        }
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["city"] == "Tunis"
    assert data["items"][0]["rooms"] == 3
