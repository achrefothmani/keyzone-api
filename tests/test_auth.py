async def test_register_then_login(client):
    payload = {
        "nom": "Bahri",
        "prenom": "Sami",
        "password": "supersecret",
        "role": "CHEF_AGENCE",
    }
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201, r.text
    user = r.json()
    assert user["email"] == "sami.bahri@keyzonestates.tn"
    assert user["role"] == "CHEF_AGENCE"

    r = await client.post(
        "/api/v1/auth/login",
        json={"email": user["email"], "password": "supersecret"},
    )
    assert r.status_code == 200
    token = r.json()
    assert token["access_token"]
    assert token["token_type"] == "bearer"


async def test_login_with_bad_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"nom": "Karoui", "prenom": "Yasmine", "password": "supersecret"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "yasmine.karoui@keyzonestates.tn", "password": "wrong"},
    )
    assert r.status_code == 401


async def test_email_collision_appends_suffix(client):
    payload1 = {"nom": "Trabelsi", "prenom": "Mehdi", "password": "password1"}
    payload2 = {"nom": "Trabelsi", "prenom": "Mehdi", "password": "password2"}

    r1 = await client.post("/api/v1/auth/register", json=payload1)
    r2 = await client.post("/api/v1/auth/register", json=payload2)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["email"] != r2.json()["email"]
