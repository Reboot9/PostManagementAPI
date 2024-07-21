# Post Management API

## Overview
The Post Management API provides endpoints for creating, retrieving, updating, and deleting posts and comments. It includes functionalities for user registration and authentication, as well as analytics for comments. The API uses Django Ninja for routing and JWT for authentication.

## Installation
### Requirements
1. Python 3.10+
2. Docker and Docker Compose (for containerized deployment)

# Setup
1. Clone the Repository
``` bash
git clone https://github.com/yourusername/post-management-api.git
cd post-management-api
```
2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```
3. Copy content of .env.example file and fill new .env file with your information

4. Run the docker
```bash
docker-compose up -d --build
 ```

5. Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

6. Run tests
```bash
docker-compose exec web python manage.py test apps
```

7. You can also access api documentation with [this](http://127.0.0.1/api/docs) link
or get access to admin panel with [this one](http://127.0.0.1/admin)