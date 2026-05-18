from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
import psycopg2.extras
import os
from utils import validate_email, generate_enrollment_id

app = FastAPI(title="Gerenciador de Alunos")

AVAILABLE_COURSES = {
    "GES": "Engenharia de Software",
    "GEC": "Engenharia da Computação",
    "GET": "Engenharia de Telecomunicações",
    "GEP": "Engenharia de Produção",
    "GEA": "Engenharia de Automação",
    "GEL": "Engenharia Elétrica",
    "GEB": "Engenharia Biomédica",
}


# ── Conexão com o banco ───────────────────────────────────────────────────────

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "alunos_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


# ── Inicialização das tabelas ─────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    import time
    for _ in range(10):
        try:
            conn = get_conn()
            break
        except Exception:
            time.sleep(2)

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id VARCHAR(20) PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            curso VARCHAR(10) NOT NULL,
            curso_nome VARCHAR(100) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollment_counters (
            curso VARCHAR(10) PRIMARY KEY,
            contador INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AlunoCreate(BaseModel):
    nome: str
    email: str
    curso: str

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    curso: Optional[str] = None


# ── Helper ────────────────────────────────────────────────────────────────────

def validate_input(nome=None, email=None, curso=None, current_id=None):
    if nome is not None and len(nome.strip()) < 3:
        raise HTTPException(status_code=400, detail="Nome deve ter pelo menos 3 caracteres.")

    if email is not None:
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="E-mail inválido.")
        conn = get_conn()
        cur = conn.cursor()
        if current_id:
            cur.execute("SELECT id FROM alunos WHERE email = %s AND id != %s", (email.lower(), current_id))
        else:
            cur.execute("SELECT id FROM alunos WHERE email = %s", (email.lower(),))
        existing = cur.fetchone()
        cur.close()
        conn.close()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um aluno com esse e-mail.")

    if curso is not None and curso.upper() not in AVAILABLE_COURSES:
        raise HTTPException(
            status_code=400,
            detail=f"Curso inválido. Opções: {list(AVAILABLE_COURSES.keys())}"
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Gerenciador de Alunos 🎓"}


# POST - cadastrar novo aluno
@app.post("/api/v1/alunos/", status_code=201)
def cadastrar_aluno(aluno: AlunoCreate):
    validate_input(aluno.nome, aluno.email, aluno.curso)

    curso = aluno.curso.upper()
    curso_nome = AVAILABLE_COURSES[curso]

    conn = get_conn()
    cur = conn.cursor()
    aluno_id = generate_enrollment_id(curso, cur)

    cur.execute(
        "INSERT INTO alunos (id, nome, email, curso, curso_nome) VALUES (%s, %s, %s, %s, %s)",
        (aluno_id, aluno.nome.strip(), aluno.email.strip().lower(), curso, curso_nome)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Aluno cadastrado com sucesso!", "aluno": {
        "id": aluno_id,
        "nome": aluno.nome.strip(),
        "email": aluno.email.strip().lower(),
        "curso": curso,
        "curso_nome": curso_nome,
    }}


# GET - listar todos os alunos
@app.get("/api/v1/alunos/")
def listar_alunos():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alunos ORDER BY id")
    alunos = cur.fetchall()
    cur.close()
    conn.close()
    return {"total": len(alunos), "alunos": alunos}


# DELETE - resetar lista de alunos (deve vir ANTES do /{aluno_id})
@app.delete("/api/v1/alunos/")
def resetar_alunos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM alunos")
    cur.execute("DELETE FROM enrollment_counters")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Lista de alunos resetada com sucesso."}


# GET - buscar aluno por ID
@app.get("/api/v1/alunos/{aluno_id}")
def buscar_aluno(aluno_id: str):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id.upper(),))
    aluno = cur.fetchone()
    cur.close()
    conn.close()
    if not aluno:
        raise HTTPException(status_code=404, detail=f"Aluno '{aluno_id}' não encontrado.")
    return aluno


# PATCH - atualizar dados de um aluno parcialmente
@app.patch("/api/v1/alunos/{aluno_id}")
def atualizar_aluno(aluno_id: str, aluno: AlunoUpdate):
    aluno_id = aluno_id.upper()

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
    existing = cur.fetchone()
    if not existing:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Aluno '{aluno_id}' não encontrado.")

    validate_input(aluno.nome, aluno.email, aluno.curso, current_id=aluno_id)

    if aluno.nome:
        cur.execute("UPDATE alunos SET nome = %s WHERE id = %s", (aluno.nome.strip(), aluno_id))
    if aluno.email:
        cur.execute("UPDATE alunos SET email = %s WHERE id = %s", (aluno.email.strip().lower(), aluno_id))
    if aluno.curso:
        curso = aluno.curso.upper()
        cur.execute("UPDATE alunos SET curso = %s, curso_nome = %s WHERE id = %s",
                    (curso, AVAILABLE_COURSES[curso], aluno_id))
    conn.commit()

    cur.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
    atualizado = cur.fetchone()
    cur.close()
    conn.close()
    return {"message": "Aluno atualizado com sucesso!", "aluno": atualizado}


# DELETE - remover aluno por ID
@app.delete("/api/v1/alunos/{aluno_id}")
def remover_aluno(aluno_id: str):
    aluno_id = aluno_id.upper()

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
    aluno = cur.fetchone()
    if not aluno:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Aluno '{aluno_id}' não encontrado.")

    cur.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Aluno '{aluno['nome']}' removido com sucesso."}