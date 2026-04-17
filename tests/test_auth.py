def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "fullname": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login(client):
    # First signup
    client.post(
        "/auth/signup",
        json={
            "username": "testlog",
            "email": "testlog@example.com",
            "password": "Password123!",
            "fullname": "Test Log"
        }
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={
            "username": "testlog",
            "password": "Password123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401
