from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import engine, get_db
from schemas import UserCreate, UserResponse, UserLogin, Token, TodoCreate, TodoResponse
from models import User, Todo
from auth import hash_password, verify_password, create_access_token, verify_token
from models import Base
import uvicorn
from fastapi.middleware.cors import CORSMiddleware # For GUI

# Create all tables
Base.metadata.create_all(bind=engine)

# Create instance
app = FastAPI()

app.add_middleware( # For GUI
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

# Define a path opperation for the root URL that responds to get requests 
@app.get("/")
def root():
    return {"message": "Hello world"}

# Endpoint to register
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_pw = hash_password(user.password)

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
    
# Endpoint to login
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)): # Receives email and password
    db_user = db.query(User).filter(User.email == user.email).first() # Finds user by email in database
    if not db_user or not verify_password(user.password, db_user.password): # If user not found OR password doesn't match -> Reject
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": str(db_user.id)}) # Create token with user's ID inside and return it to the user
    return {"token": token}

# Read the Authorization: Bearer <token> header and extracts/verifies the token and returns loggedin user
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Create todo
@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_todo = Todo(title=todo.title, description=todo.description, user_id=user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# Read all todos for user
@app.get("/todos")
def get_todos(
    page: int = 1, # Query parameter, defaults to page 1
    limit: int = 10, # How many items per page, defaults to 10
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # Count total todos for this user
    total = db.query(Todo).filter(Todo.user_id == user.id).count()

    # Calculate how many to skip
    skip = (page - 1) * limit # Page 1 skips 0, page 2 skips 10 etc
    
    # Get only the todos for this page
    todos = db.query(Todo).filter(Todo.user_id == user.id).offset(skip).limit(limit).all() # offset(skip)... SQL magic, skip rows, take y rows

    return {
        "data": todos,
        "page": page,
        "limit": limit,
        "total": total # Total count so front end knows how many pages exist
    }

# Update todo
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if db_todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Delete todo
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if db_todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(db_todo)
    db.commit()

# Starts server make it accessable on http
if __name__ == '__main__':
    uvicorn.run(app, host="0:0:0:0", port=8000)


# db.add(new_todo) - Stages the new item to be saved (like adding to a shopping cart)
# db.commit() - Actually saves it to the database (like clicking "checkout")
# db.refresh(new_todo) - Reloads the data from database (to get the auto-generated id)
# db.query(Todo).filter(...).first() - Search the database for matching records
# db.delete() - Remove from database
# Depends(get_db) - "Before running this function, first run get_db and give me the result"
#   - It's dependency injection - FastAPI automatically creates a database session for each request

# Depends(get_current_user) - "First verify the token and get the user, then run this function"
#   - This is how we protect routes - if token is invalid, it stops before your code runs

# Header(...) - Reads a value from the HTTP headers (like Authorization: Bearer token123)