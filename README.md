# Quick Habit

Quick Habit is a simple habit tracker backend inspired by the book *Atomic Habits* by James Clear. It helps users build and maintain healthy routines with the support of Telegram reminders.

## 🚀 Features

- Track both helpful and pleasant habits
- Link pleasant habits as rewards for completing helpful ones
- Daily/weekly habit scheduling
- Telegram integration for habit reminders
- JWT authentication
- Pagination, access control, validation rules
- Background task handling via Celery & Redis
- Scheduling tasks via Celery Beat
- Dockerized for easy deployment

## 🧱 Tech Stack

- Python 3.13
- Django 5+
- Django REST Framework
- PostgreSQL
- Redis
- Celery + Celery Beat
- Docker & Docker Compose

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/quick-habit.git
cd quick-habit
````

### 2. Create `.env` file

Copy `.env.example` to `.env` and configure your variables:

```bash
cp .env.example .env
```

### 3. Build and run with Docker

```bash
docker-compose up --build
```

App will be available at `http://localhost:8000`

## 🧪 Running Tests

```bash
docker-compose run web python manage.py test
```

## 📬 Telegram Integration

The app sends habit reminders via Telegram. To enable:

1. Create a Telegram bot via BotFather
2. Save the bot token in your `.env`
3. Link your user with a `chat_id`
4. Celery will handle sending reminders on schedule


## 📚 API Documentation

Auto-generated Swagger/Redoc API documentation available at:

```
http://localhost:8000/api/docs/
http://localhost:8000/api/redoc/
```
