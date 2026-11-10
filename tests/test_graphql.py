def test_graphql_users_without_admin(client):
    # 1. Регистрируем обычного пользователя
    client.post("/auth/register", json={"email": "user@example.com", "password": "SuperSecretPassword123!"})
    
    # 2. Логинимся, чтобы получить токен
    login = client.post("/auth/login", json={"email": "user@example.com", "password": "SuperSecretPassword123!"})
    token = login.json()["access_token"]
    
    # 3. Отправляем GraphQL-запрос С ТОКЕНОМ
    headers = {"Authorization": f"Bearer {token}"}
    query = {"query": "{ users { id email } }"}
    
    response = client.post("/graphql", json=query, headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # 4. Проверяем, что ошибка именно про права админа
    assert "errors" in data
    assert data["errors"][0]["message"] == "Admin only"