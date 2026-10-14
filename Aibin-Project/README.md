# TrafficVision AI Backend - Beginner's Guide

Welcome to the **TrafficVision AI Backend** project! If you are new to backend development, **FastAPI**, or the concept of an **API Gateway**, you are in the right place. This document is written specifically for beginners to help you understand exactly what this codebase is doing, file by file.

---

## 1. Important Concepts to Know

### What is FastAPI?
FastAPI is a modern, fast, and highly popular framework for building APIs (Application Programming Interfaces) in Python. 
Think of an API as a waiter in a restaurant. You (the client/frontend) tell the waiter what you want, the waiter takes your order to the kitchen (the backend server/database), and then brings your food (data) back to you. FastAPI makes building this "waiter" extremely quick and provides automatic, interactive documentation right out of the box.

### What is an API Gateway?
Imagine you run a massive restaurant with different specialized kitchens: one for pizza, one for sushi, and one for drinks. Instead of a customer having to go to three different kitchens, they go to a **front desk**. The front desk checks their ID (authentication) and then routes their order to the correct kitchen. 
In modern application architecture (called microservices), an **API Gateway** acts as this front desk. It sits in front of all your other services (like a traffic monitoring service and a prediction service) and handles central tasks like user login, security, and routing requests to the correct place.

### What have we created here?
We have built an **API Gateway** for "TrafficVision AI" using **FastAPI**. 
This gateway does three main things:
1. **User Management (Auth):** Handles user registration, secure login, and issuing digital tokens.
2. **Security (RBAC):** Ensures only certain users (like admins) can access specific areas. This is called Role-Based Access Control.
3. **Routing (Proxy):** Takes requests for "traffic" or "prediction" data and silently forwards them to other backend services.

---

## 2. Codebase Structure: Folder by Folder

Here is a comprehensive breakdown of every folder and file in this project and what it does.

### The Root Folder
This is the main folder (`trafficvision-backend/`). It holds the overarching configurations for the project.

- **`.env.example`**: This is a template for environment variables. Environment variables are secret keys and settings (like database passwords or API keys) that you don't want to write directly into your Python code. You usually copy this to a file named `.env` and fill in your actual secrets.
- **`requirements.txt`**: This file lists all the third-party Python packages this project needs to run (like `fastapi`, `sqlalchemy` for databases, `uvicorn` to run the server, etc.). You install them using `pip install -r requirements.txt`.
- **`README.md`**: The file you are reading right now! It explains the project.
- **`Dockerfile`**: A set of instructions for "Docker". Docker packages this entire application into an isolated container so it can run smoothly on any computer in the world without setup issues.
- **`test_auth.db` & `test_rbac.db`**: These are small, local SQLite databases created automatically when running our automated tests. You can usually ignore them.

---

### The `app/` Folder
This is where the actual heart of the application code lives.

- **`app/main.py`**: This is the **Starting Point** of the app. When you start the server, this is the file that runs first. It creates the FastAPI application object and glues all the different routes (URLs) together.
- **`app/config.py`**: This file reads your `.env` file and loads your secret configurations into Python variables so the rest of the application can access them securely.
- **`app/database.py`**: This file is responsible for talking to your database (like SQLite or PostgreSQL). It sets up the "Engine" (the connection line) and the "Session" (the active conversation with the database).
- **`app/models.py`**: This file defines your **Database Tables**. Using a tool called SQLAlchemy, we write normal Python classes (like a `User` class), and SQLAlchemy automatically translates that into an actual database table with columns like `email` and `password`.
- **`app/schemas.py`**: This file defines the **Data Shapes**. When a user sends data to us (like filling out a registration form), we use a tool called "Pydantic" in this file to validate that the email is a real email format and the password isn't empty. It ensures bad data never reaches our database.

---

### The `app/auth/` Folder
This folder manages everything related to Authentication (logging in) and Authorization (checking permissions).

- **`app/auth/router.py`**: This file defines the actual URLs (endpoints) for authentication. For example, it contains the code that executes when a user visits `POST /api/v1/auth/login` or `POST /api/v1/auth/register`.
- **`app/auth/security.py`**: The toolkit for security. It contains functions to securely "hash" (scramble) passwords before saving them to the database. It also contains functions to create JWTs (JSON Web Tokens). A JWT is like a digital VIP wristband we give users after they log in, proving who they are for future requests.
- **`app/auth/dependencies.py`**: FastAPI uses "dependencies" to share and reuse logic. This file has functions that run *before* a route does. For example, a function here will intercept a user's request, look at their VIP wristband (JWT token), figure out who they are, and block them if they aren't an "Admin".
- **`app/auth/__init__.py`**: An empty file that simply tells Python, "Treat this folder as a module you can import from."

---

### The `app/gateway/` Folder
This folder contains the logic that makes this application an "API Gateway" (the front desk).

- **`app/gateway/traffic_proxy.py`**: When a user asks our gateway for traffic data, this file intercepts the request. It then acts as a middleman, sending a *new* request to the actual backend Traffic Service (which might be running on a different port or a totally different computer), gets the response, and sends it back to the user.
- **`app/gateway/prediction_proxy.py`**: Works exactly the same as the traffic proxy, but it forwards requests to the AI Prediction Service instead.
- **`app/gateway/__init__.py`**: Tells Python this folder is a module.

---

### The `tests/` Folder
This folder contains automated scripts to test our code and ensure it works without having to click around manually.

- **`tests/test_auth.py`**: A Python script that acts like a fake user. It automatically tries to register, log in, and access secure pages to ensure our authentication logic is working perfectly.
- **`tests/test_rbac.py`**: A script that tests Role-Based Access Control (RBAC). It ensures that a normal "public" user gets blocked (Error 403 Forbidden) if they try to access an Admin-only page.

---

## 3. How to Run This Project Locally

If you want to run this code on your own machine and play around with it, follow these steps in your terminal:

1. **Create a Virtual Environment:**
   A virtual environment is a clean, isolated bubble for this project's Python packages so they don't mess with your system's global Python.
   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment:**
   ```bash
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install the Requirements:**
   Download all the tools this project needs to function.
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Environment File:**
   Copy the example settings to create your local settings file.
   ```bash
   cp .env.example .env
   ```

5. **Start the FastAPI Server:**
   This command uses `uvicorn` (a lightning-fast server program) to run our `app/main.py` file. The `--reload` flag is awesome—it means the server will automatically restart and update if you edit any code!
   ```bash
   uvicorn app.main:app --reload
   ```

6. **View the Magic (Interactive Documentation):**
   FastAPI automatically generates beautiful documentation. Once the server is running, open your web browser and go to:
   
   👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   
   You will see an interactive webpage where you can test all the endpoints directly. You can click on `/api/v1/auth/register`, click "Try it out", enter some test data, and see the response!
