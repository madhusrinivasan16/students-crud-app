
from contextlib import asynccontextmanager
from datetime import date
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


DATABASE = "students.db"


# ---------- DATABASE ----------

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Students Database CRUD API",
    description="EWB internship project using FastAPI and SQLite",
    version="1.0.0",
    lifespan=lifespan
)
@app.get("/")
def home():
    return {
        "message": "Students Database CRUD API is running!",
        "docs": "/docs"
    }


# ---------- DATA VALIDATION ----------

class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None


# ---------- HELPER ----------

def student_dict(row):
    return dict(row)


def find_student(student_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student_dict(row)


# ---------- CREATE ----------

@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    data = student.model_dump()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO students
            (name, date_of_birth, email, phone, course,
             address, enrollment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"].strip(),
                data["date_of_birth"].isoformat(),
                data["email"],
                data["phone"],
                data["course"],
                data["address"],
                data["enrollment_date"].isoformat()
                if data["enrollment_date"] else None
            )
        )
        new_id = cursor.lastrowid

    return find_student(new_id)


# ---------- READ ALL / FILTER ----------

@app.get("/students")
def get_students(
    name: Optional[str] = None,
    course: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500)
):
    query = "SELECT * FROM students WHERE 1=1"
    parameters = []

    if name:
        query += " AND name LIKE ?"
        parameters.append(f"%{name}%")

    if course:
        query += " AND course LIKE ?"
        parameters.append(f"%{course}%")

    query += " ORDER BY student_id LIMIT ?"
    parameters.append(limit)

    with get_connection() as connection:
        rows = connection.execute(
            query, parameters
        ).fetchall()

    return [student_dict(row) for row in rows]


# ---------- READ ONE ----------

@app.get("/students/{student_id}")
def get_student(student_id: int):
    return find_student(student_id)


# ---------- UPDATE ----------

@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    existing = find_student(student_id)
    data = student.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update"
        )

    for key, value in data.items():
        if key == "name" and value is not None:
            value = value.strip()

        if isinstance(value, date):
            value = value.isoformat()

        data[key] = value

    # Do not allow required fields to become empty or null.
    for required_field in ("name", "date_of_birth"):
        if required_field in data:
            if data[required_field] is None or (
                required_field == "name" and not data[required_field]
            ):
                raise HTTPException(
                    status_code=422,
                    detail=f"{required_field} cannot be empty"
                )

    if "name" in data and data["name"] is None:
        data["name"] = existing["name"]

    if "date_of_birth" in data and data["date_of_birth"] is None:
        data["date_of_birth"] = existing["date_of_birth"]

    assignments = ", ".join(
        f"{field} = ?" for field in data
    )
    values = list(data.values())
    values.append(student_id)

    with get_connection() as connection:
        connection.execute(
            f"UPDATE students SET {assignments} WHERE student_id = ?",
            values
        )

    return find_student(student_id)


# ---------- DELETE ----------

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    find_student(student_id)

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM students WHERE student_id = ?",
            (student_id,)
        )

    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }
