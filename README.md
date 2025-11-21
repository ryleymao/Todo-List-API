# Todo List API

A RESTful API for managing todo lists with user authentication.

## Features

- User registration and login with JWT authentication
- Create, read, update, and delete todos
- Pagination support
- Password hashing with bcrypt
- PostgreSQL database

## Tech Stack

- Python 3
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT (python-jose)
- Passlib (bcrypt)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Todo-List-API.git
cd Todo-List-API
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Make sure PostgreSQL is installed and running, then create the database:

```bash
psql postgres
CREATE DATABASE todo_api;
\q
```

### 5. Configure database connection

In `database.py`, update the connection string with your credentials:

```python
SQLALCHEMY_DATABASE_URL = "postgresql://YOUR_USERNAME@localhost/todo_api"
```

### 6. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Authentication

#### Register
```
POST /register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "yourpassword"
}
```

#### Login
```
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "yourpassword"
}
```

Returns a JWT token to use for authenticated requests.

### Todos (requires authentication)

Include the token in the Authorization header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

#### Create Todo
```
POST /todos
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

#### Get All Todos (with pagination)
```
GET /todos?page=1&limit=10
```

#### Update Todo
```
PUT /todos/{id}
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description"
}
```

#### Delete Todo
```
DELETE /todos/{id}
```

## Testing with curl

Register a user:
```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'
```

Login:
```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Create a todo (replace YOUR_TOKEN):
```bash
curl -X POST "http://127.0.0.1:8000/todos" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first todo", "description": "This is a test"}'
```

Get todos:
```bash
curl -X GET "http://127.0.0.1:8000/todos" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## GUI

Open `index.html` in your browser to use the web interface. Make sure the server is running first.

## API Documentation

FastAPI provides automatic documentation at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Project Structure

```
Todo-List-API/
├── main.py          # API endpoints
├── models.py        # Database models
├── schemas.py       # Pydantic schemas
├── database.py      # Database connection
├── auth.py          # Authentication utilities
├── index.html       # Web interface
├── requirements.txt # Dependencies
└── README.md        # This file
```

## Architecture

### How Components Connect

```
Client (Browser/curl)
        |
        v
   [FastAPI]  ←── main.py (handles HTTP requests)
        |
        v
   [Schemas] ←── schemas.py (validates request/response data)
        |
        v
  [SQLAlchemy] ←── models.py (Python objects that map to database tables)
        |
        v
  [PostgreSQL] ←── database.py (actual data storage)
```

### Authentication Flow

```
1. REGISTER
   User sends name, email, password
        |
        v
   Password gets hashed (bcrypt)
        |
        v
   User stored in database
        |
        v
   Returns user info


2. LOGIN
   User sends email, password
        |
        v
   Find user by email
        |
        v
   Verify password against hash
        |
        v
   Generate JWT token (contains user ID + expiration)
        |
        v
   Return token to user


3. PROTECTED REQUEST (create/read/update/delete todos)
   User sends request with "Authorization: Bearer <token>"
        |
        v
   Server decodes token, extracts user ID
        |
        v
   Server finds user in database
        |
        v
   Request proceeds (user can only access their own todos)
```

### Database Schema

```
USERS TABLE
+----+--------+-------------------+------------------+
| id | name   | email             | password (hash)  |
+----+--------+-------------------+------------------+
| 1  | John   | john@example.com  | $2b$12$xyz...   |
| 2  | Jane   | jane@example.com  | $2b$12$abc...   |
+----+--------+-------------------+------------------+

TODOS TABLE
+----+---------+----------------+---------------------+
| id | user_id | title          | description         |
+----+---------+----------------+---------------------+
| 1  | 1       | Buy groceries  | Milk, eggs, bread   |
| 2  | 1       | Pay bills      | Electric bill       |
| 3  | 2       | Call mom       | Birthday wishes     |
+----+---------+----------------+---------------------+

user_id is a FOREIGN KEY linking to users.id
```

### Key Design Decisions

1. **JWT for authentication** - Stateless tokens mean the server does not need to store session data. The token itself contains the user ID.

2. **Password hashing with bcrypt** - Passwords are never stored as plain text. Even if the database is compromised, passwords cannot be reversed.

3. **Foreign key relationship** - Each todo belongs to a user. This allows filtering todos by user and prevents users from accessing each other's data.

4. **Pydantic schemas** - Separate schemas for input (UserCreate) and output (UserResponse) ensure passwords are never returned in API responses.

## Limitations

### Security
- SECRET_KEY is hardcoded (should use environment variables)
- No HTTPS (handled by deployment platform in production)
- No rate limiting (API can be spammed)
- No password strength requirements
- No email verification

### Features
- No refresh tokens (user must login again when token expires)
- No "forgot password" functionality
- No todo status (completed/incomplete)
- No due dates for todos
- No sorting or filtering options

### Database
- No indexes on user_id in todos table (queries slow down with large data)
- No soft delete (deleted todos are gone forever)

## Future Improvements

- Add environment variables for configuration
- Implement refresh tokens
- Add todo status and due dates
- Add filtering and sorting
- Add rate limiting
- Add unit tests
- Deploy to cloud platform

https://roadmap.sh/projects/todo-list-api
