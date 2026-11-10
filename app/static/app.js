const API_URL = '/auth';
const GQL_URL = '/graphql';

// Получить токен из localStorage
function getToken() {
    return localStorage.getItem('vault_token');
}

// Сохранить токен
function setToken(token) {
    localStorage.setItem('vault_token', token);
}

// Удалить токен
function clearToken() {
    localStorage.removeItem('vault_token');
}

// Универсальный REST-запрос
async function api(path, body) {
    const res = await fetch(API_URL + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Ошибка REST');
    return data;
}

// Универсальный GraphQL-запрос
async function gql(query, variables = {}) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(GQL_URL, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ query, variables })
    });
    const data = await res.json();
    if (data.errors) throw new Error(data.errors[0].message);
    return data.data;
}

// Обработчик логина
async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    errorDiv.textContent = '';

    try {
        const data = await api('/login', { email, password });
        setToken(data.access_token);
        showAdmin();
    } catch (err) {
        errorDiv.textContent = err.message;
    }
}

// Показать админку
async function showAdmin() {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('admin-section').classList.remove('hidden');
    await loadClients();
}

// Выйти
function handleLogout() {
    clearToken();
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('admin-section').classList.add('hidden');
}

// Загрузить клиентов
async function loadClients() {
    const tbody = document.getElementById('clients-table-body');
    tbody.innerHTML = '<tr><td colspan="4">Загрузка...</td></tr>';
    
    try {
        const data = await gql(`query { clients { id clientId name createdAt } }`);
        tbody.innerHTML = '';
        
        if (data.clients.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">Клиентов пока нет</td></tr>';
            return;
        }

        for (const client of data.clients) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${client.id}</td>
                <td>${client.clientId}</td>
                <td>${client.name}</td>
                <td>${new Date(client.createdAt).toLocaleString()}</td>
            `;
            tbody.appendChild(tr);
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" style="color:red">${err.message}</td></tr>`;
    }
}

// Создать клиента
async function createClient() {
    const name = document.getElementById('client-name').value.trim();
    const errorDiv = document.getElementById('admin-error');
    errorDiv.textContent = '';
    if (!name) return;

    try {
        await gql(`mutation { createClient(name: "${name}", isConfidential: true) { id } }`);
        document.getElementById('client-name').value = '';
        await loadClients();
    } catch (err) {
        errorDiv.textContent = err.message;
    }
}

// Автозапуск при загрузке страницы
window.addEventListener('DOMContentLoaded', () => {
    if (getToken()) {
        showAdmin();
    }
});