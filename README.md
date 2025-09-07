# Campus Event Management Platform - Prototype

This is a Django-based Campus Event Management Platform.
It provides an **admin portal** to manage events and a backend API for **student registrations, attendance, and feedback**. It also includes reporting endpoints to analyze event popularity and student participation.

## Features

### Core Functionality

* **Register students to an event** (`POST /api/register`)
* **Mark attendance** (`POST /api/checkin`)
* **Collect feedback** (`POST /api/feedback`)


## Tech Stack

* **Backend**: Django 5.0
* **REST APIs**: Django REST Framework
* **Database**: PostgreSQL (or SQLite/MySQL)
* **Authentication**: Optional JWT (via `djangorestframework-simplejwt`)

---

## Setup Instructions

### 1. Clone the repository


git clone <repository-url>
cd campus_events


### 2. Create and activate virtual environment

python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

### 3. Install dependencies

pip install "Django>=5.0,<6.0" djangorestframework djangorestframework-simplejwt psycopg2-binary


### 5. Run migrations

python manage.py makemigrations
python manage.py migrate

### 6. Create superuser (for admin portal)

python manage.py createsuperuser

### 7. Run server

python manage.py runserver

* Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)
* API endpoints: [http://localhost:8000/api/](http://localhost:8000/api/)
