async def test_create_and_list_users(authed_client):
    r = await authed_client.post(
        "/api/v1/users",
        json={
            "nom": "Ben Salah",
            "prenom": "Leïla",
            "password": "password!",
            "role": "AGENT",
            "telephone": "+216 22 000 000",
            "zone": "Tunis",
        },
    )
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["email"] == "leila.ben-salah@keyzonestates.tn"

    r = await authed_client.get("/api/v1/users", params={"role": "AGENT"})
    assert r.status_code == 200
    page = r.json()
    assert page["total"] >= 1
    assert any(u["id"] == created["id"] for u in page["items"])


async def test_update_user_regenerates_email(authed_client):
    r = await authed_client.post(
        "/api/v1/users",
        json={"nom": "Old", "prenom": "Name", "password": "password!"},
    )
    user = r.json()
    assert user["email"] == "name.old@keyzonestates.tn"

    r = await authed_client.put(
        f"/api/v1/users/{user['id']}",
        json={"prenom": "Renamed"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == "renamed.old@keyzonestates.tn"
