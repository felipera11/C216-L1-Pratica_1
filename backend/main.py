from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from data import students, AVAILABLE_COURSES
from utils import generate_enrollment_id, validate_email

app = FastAPI(title="Sistema de Gerenciamento de Alunos")


# ── Schemas ──────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str
    email: str
    course_code: str  # ex: "1" a "7"

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    course_code: Optional[str] = None


# ── Helper ───────────────────────────────────────────────────────────────────

def validate_student_input(name: str | None, email: str | None, course_code: str | None, current_enrollment: str | None = None):
    if name is not None and len(name) < 3:
        raise HTTPException(status_code=400, detail="Nome deve ter pelo menos 3 caracteres.")

    if email is not None:
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="E-mail inválido.")
        existing_emails = [
            s["email"] for eid, s in students.items() if eid != current_enrollment
        ]
        if email in existing_emails:
            raise HTTPException(status_code=400, detail="Já existe um aluno com esse e-mail.")

    if course_code is not None and course_code not in AVAILABLE_COURSES:
        raise HTTPException(
            status_code=400,
            detail=f"Curso inválido. Opções: {list(AVAILABLE_COURSES.keys())}"
        )


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "API de Gerenciamento de Alunos 🎓"}


# GET - listar todos os alunos
@app.get("/api/v1/students")
def list_students():
    return {"total": len(students), "students": list(students.values())}


# GET - buscar aluno por matrícula (path parameter)
@app.get("/api/v1/students/{enrollment_id}")
def get_student(enrollment_id: str):
    enrollment_id = enrollment_id.upper()
    if enrollment_id not in students:
        raise HTTPException(status_code=404, detail=f"Matrícula '{enrollment_id}' não encontrada.")
    return students[enrollment_id]


# GET - buscar aluno por e-mail (query parameter)
@app.get("/api/v1/students/search/by-email")
def get_student_by_email(email: str):
    for student in students.values():
        if student["email"] == email.lower():
            return student
    raise HTTPException(status_code=404, detail="Nenhum aluno encontrado com esse e-mail.")


# GET - listar cursos disponíveis
@app.get("/api/v1/courses")
def list_courses():
    return {
        code: {"abbreviation": abbr, "name": name}
        for code, (abbr, name) in AVAILABLE_COURSES.items()
    }


# POST - criar aluno
@app.post("/api/v1/students", status_code=201)
def create_student(student: StudentCreate):
    validate_student_input(student.name, student.email, student.course_code)

    abbr, course_name = AVAILABLE_COURSES[student.course_code]
    enrollment_id = generate_enrollment_id(abbr)

    new_student = {
        "enrollment_id": enrollment_id,
        "name": student.name.strip(),
        "email": student.email.strip().lower(),
        "course_code": abbr,
        "course_name": course_name,
    }
    students[enrollment_id] = new_student
    return {"message": "Aluno cadastrado com sucesso!", "student": new_student}


# PUT - atualizar aluno completo
@app.put("/api/v1/students/{enrollment_id}")
def update_student(enrollment_id: str, student: StudentCreate):
    enrollment_id = enrollment_id.upper()
    if enrollment_id not in students:
        raise HTTPException(status_code=404, detail=f"Matrícula '{enrollment_id}' não encontrada.")

    validate_student_input(student.name, student.email, student.course_code, enrollment_id)

    abbr, course_name = AVAILABLE_COURSES[student.course_code]
    students[enrollment_id].update({
        "name": student.name.strip(),
        "email": student.email.strip().lower(),
        "course_code": abbr,
        "course_name": course_name,
    })
    return {"message": "Aluno atualizado com sucesso!", "student": students[enrollment_id]}


# PATCH - atualizar aluno parcialmente
@app.patch("/api/v1/students/{enrollment_id}")
def patch_student(enrollment_id: str, student: StudentUpdate):
    enrollment_id = enrollment_id.upper()
    if enrollment_id not in students:
        raise HTTPException(status_code=404, detail=f"Matrícula '{enrollment_id}' não encontrada.")

    validate_student_input(student.name, student.email, student.course_code, enrollment_id)

    if student.name:
        students[enrollment_id]["name"] = student.name.strip()
    if student.email:
        students[enrollment_id]["email"] = student.email.strip().lower()
    if student.course_code:
        abbr, course_name = AVAILABLE_COURSES[student.course_code]
        students[enrollment_id]["course_code"] = abbr
        students[enrollment_id]["course_name"] = course_name

    return {"message": "Aluno atualizado parcialmente!", "student": students[enrollment_id]}


# DELETE - remover aluno
@app.delete("/api/v1/students/{enrollment_id}")
def delete_student(enrollment_id: str):
    enrollment_id = enrollment_id.upper()
    if enrollment_id not in students:
        raise HTTPException(status_code=404, detail=f"Matrícula '{enrollment_id}' não encontrada.")

    removed = students.pop(enrollment_id)
    return {"message": f"Aluno '{removed['name']}' removido com sucesso."}