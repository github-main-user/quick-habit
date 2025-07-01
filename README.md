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

## 🧪 Running Tests

```bash
docker compose run web python manage.py test
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
http://localhost/api/docs/
http://localhost/api/redoc/
```

## Local Usage

In case you want to run this project manually on your machine:

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
docker compose up --build
```

App will be available at `http://localhost:80`

To stop started containers use `docker compose down`, add `-v` to clean up all volumes.

## Automatic CICD

In case you want to use automatic CICD via github actions:

1. Set up your server:
    - Install Docker
    - Set up SSH
    - Set up firewall for 22(ssh) and 80(http) ports *(recommended but optional)*
    - Create a non-root user and add it to the `docker` group *(recommended but optional)*.
    - Generate a pair of keys using `ssh-keygen` and add the public one to `/home/<your_user>/.ssh/authorized_keys` on your server.
2. Fork this repo
3. Setup github secrets:
    - `ENV_FILE` - file with all important variables *(see `.env.example` file)*.
    - `SERVER_IP` - IP address of your server.
    - `SSH_USER` - user name.
    - `SSH_SECRET_KEY` - private ssh key.

Every push/PR will trigger these github actions:
1. lint (flake8)
2. test
3. deploy

App will be available at `http://<SERVER_IP>:80`

To stop started application - `cd` to `/home/<SSH_USER>/learning-management/`,
and run `docker compose down` (add `-v` to clean up all volumes).
