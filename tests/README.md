# Vault — Сервис управления пользователями и OAuth-клиентами

Бэкенд-сервис на Python с GraphQL API и минимальной админ-панелью. 
Разработан в рамках Лабораторной работы №2.

## 🛠 Стек технологий
* **FastAPI** — асинхронный веб-фреймворк.
* **Ariadne** — schema-first GraphQL.
* **SQLAlchemy 2.x** + **Alembic** — ORM и миграции (SQLite).
* **Argon2id** + **zxcvbn** — хэширование паролей и оценка стойкости.
* **JWT (HS256)** — аутентификация.
* **Vanilla JS** — минималистичный SPA-интерфейс администратора.

## 🚀 Установка и запуск

1. **Клонируйте репозиторий и создайте виртуальное окружение:**
   ```bash
   git clone https://github.com/<ваш_ник>/lab2_vault.git
   cd lab2_vault
   python -m venv .venv
   # Активация: .venv\Scripts\activate (Windows) или source .venv/bin/activate (Linux/Mac)