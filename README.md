# Students Database CRUD Application

## Project Overview
This project is a Python backend application for managing student records using FastAPI and SQLite.

## Features
- Create student records
- View all student records
- Retrieve a student by ID
- Search students by name or course
- Update student details
- Delete student records
- Input validation and error handling

## Technologies Used
- Python
- FastAPI
- SQLite
- Uvicorn
- Pydantic

## Requirements
Python 3.10 or newer.

## Installation
1. Clone or download this repository.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   `python -m venv .venv`

4. Activate the environment in Windows PowerShell:

   `.\.venv\Scripts\Activate.ps1`

5. Install dependencies:

   `python -m pip install -r requirements.txt`

## Run the Application

Run this command in the terminal:

`python -m uvicorn main:app --reload`

## API Documentation
Open `http://127.0.0.1:8000/docs` in your browser.

## Database
SQLite creates the `students.db` database automatically when the application starts. Student records are stored in the database.

## Security
Use sample data for testing. Do not upload real student personal information or secret credentials.

## Internship
EWB Edu Tech Pvt. Ltd. — Python Backend Development
