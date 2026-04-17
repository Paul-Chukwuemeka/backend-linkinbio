def test_create_and_fetch_card(client):
    # 1. Signup to get token
    res = client.post(
        "/auth/signup",
        json={
            "username": "carduser",
            "email": "card@example.com",
            "password": "Password123!",
            "fullname": "Card User"
        }
    )
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add a new card
    card_res = client.post(
        "/cards",
        json={"name": "My New Context"},
        headers=headers
    )
    assert card_res.status_code == 201
    card_data = card_res.json()
    assert card_data["name"] == "My New Context"
    assert "id" in card_data

    # 3. Fetch all my cards
    list_res = client.get("/cards/me", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1
    assert any(c["id"] == card_data["id"] for c in items)
