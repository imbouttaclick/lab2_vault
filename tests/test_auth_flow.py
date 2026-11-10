def test_register_login_me(client):
    # 1. Регистрация
    email = "test@example.com"
    password = "SuperSecretPassword123!"
    
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # 2. Логин
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 3. Получение данных о себе
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["is_admin"] is False # По умолчанию не админ

def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "test2@example.com", "password": "SuperSecretPassword123!"})
    response = client.post("/auth/login", json={"email": "test2@example.com", "password": "WrongPassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401