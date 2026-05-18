import pytest
import requests

BASE_URL = "http://localhost:8000"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def resetar_antes_de_cada_teste():
    """Reseta a lista de alunos antes de cada teste."""
    requests.delete(f"{BASE_URL}/api/v1/alunos/")
    yield


# ── Helper ────────────────────────────────────────────────────────────────────

def cadastrar(nome, email, curso):
    return requests.post(f"{BASE_URL}/api/v1/alunos/", json={
        "nome": nome,
        "email": email,
        "curso": curso,
    })


# ── Testes de Cadastro (POST) ─────────────────────────────────────────────────

class TestCadastro:

    def test_cadastrar_3_alunos_ges(self):
        r1 = cadastrar("Ana Lima", "ana@email.com", "GES")
        r2 = cadastrar("Bruno Silva", "bruno@email.com", "GES")
        r3 = cadastrar("Carlos Souza", "carlos@email.com", "GES")

        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

        assert r1.json()["aluno"]["id"] == "GES1"
        assert r2.json()["aluno"]["id"] == "GES2"
        assert r3.json()["aluno"]["id"] == "GES3"

    def test_cadastrar_3_alunos_gec(self):
        r1 = cadastrar("Diana Rocha", "diana@email.com", "GEC")
        r2 = cadastrar("Eduardo Pinto", "edu@email.com", "GEC")
        r3 = cadastrar("Fernanda Costa", "fernanda@email.com", "GEC")

        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

        assert r1.json()["aluno"]["id"] == "GEC1"
        assert r2.json()["aluno"]["id"] == "GEC2"
        assert r3.json()["aluno"]["id"] == "GEC3"

    def test_cadastrar_email_duplicado(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        r = cadastrar("Outro Nome", "ana@email.com", "GEC")
        assert r.status_code == 400

    def test_cadastrar_nome_curto(self):
        r = cadastrar("AB", "ab@email.com", "GES")
        assert r.status_code == 400

    def test_cadastrar_email_invalido(self):
        r = cadastrar("Nome Valido", "emailinvalido", "GES")
        assert r.status_code == 400

    def test_cadastrar_curso_invalido(self):
        r = cadastrar("Nome Valido", "valido@email.com", "XYZ")
        assert r.status_code == 400


# ── Testes de Listagem (GET) ──────────────────────────────────────────────────

class TestListagem:

    def test_listar_alunos_vazio(self):
        r = requests.get(f"{BASE_URL}/api/v1/alunos/")
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_listar_alunos(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        cadastrar("Bruno Silva", "bruno@email.com", "GEC")

        r = requests.get(f"{BASE_URL}/api/v1/alunos/")
        assert r.status_code == 200
        assert r.json()["total"] == 2


# ── Testes de Busca por ID (GET) ──────────────────────────────────────────────

class TestBusca:

    def test_buscar_aluno_existente(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        r = requests.get(f"{BASE_URL}/api/v1/alunos/GES1")
        assert r.status_code == 200
        assert r.json()["nome"] == "Ana Lima"

    def test_buscar_aluno_inexistente(self):
        r = requests.get(f"{BASE_URL}/api/v1/alunos/GES999")
        assert r.status_code == 404

    def test_id_nao_reutilizado_apos_delete(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        requests.delete(f"{BASE_URL}/api/v1/alunos/GES1")
        cadastrar("Bruno Silva", "bruno@email.com", "GES")

        r = requests.get(f"{BASE_URL}/api/v1/alunos/GES2")
        assert r.status_code == 200
        assert r.json()["nome"] == "Bruno Silva"

        r_old = requests.get(f"{BASE_URL}/api/v1/alunos/GES1")
        assert r_old.status_code == 404


# ── Testes de Atualização (PATCH) ─────────────────────────────────────────────

class TestAtualizacao:

    def test_atualizar_nome(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        r = requests.patch(f"{BASE_URL}/api/v1/alunos/GES1", json={"nome": "Ana Souza"})
        assert r.status_code == 200
        assert r.json()["aluno"]["nome"] == "Ana Souza"

    def test_atualizar_email(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        r = requests.patch(f"{BASE_URL}/api/v1/alunos/GES1", json={"email": "novo@email.com"})
        assert r.status_code == 200
        assert r.json()["aluno"]["email"] == "novo@email.com"

    def test_atualizar_curso(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        r = requests.patch(f"{BASE_URL}/api/v1/alunos/GES1", json={"curso": "GEC"})
        assert r.status_code == 200
        assert r.json()["aluno"]["curso"] == "GEC"

    def test_atualizar_aluno_inexistente(self):
        r = requests.patch(f"{BASE_URL}/api/v1/alunos/GES999", json={"nome": "Teste"})
        assert r.status_code == 404


# ── Testes de Remoção (DELETE) ────────────────────────────────────────────────

class TestRemocao:

    def test_remover_aluno(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        r = requests.delete(f"{BASE_URL}/api/v1/alunos/GES1")
        assert r.status_code == 200

        r_check = requests.get(f"{BASE_URL}/api/v1/alunos/GES1")
        assert r_check.status_code == 404

    def test_remover_aluno_inexistente(self):
        r = requests.delete(f"{BASE_URL}/api/v1/alunos/GES999")
        assert r.status_code == 404

    def test_resetar_lista(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        cadastrar("Bruno Silva", "bruno@email.com", "GEC")

        r = requests.delete(f"{BASE_URL}/api/v1/alunos/")
        assert r.status_code == 200

        r_lista = requests.get(f"{BASE_URL}/api/v1/alunos/")
        assert r_lista.json()["total"] == 0


# ── Testes de Persistência ────────────────────────────────────────────────────

class TestPersistencia:

    def test_dados_persistem_apos_multiplas_consultas(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        cadastrar("Bruno Silva", "bruno@email.com", "GEC")

        r1 = requests.get(f"{BASE_URL}/api/v1/alunos/")
        r2 = requests.get(f"{BASE_URL}/api/v1/alunos/")

        assert r1.json()["total"] == 2
        assert r2.json()["total"] == 2
        assert r1.json()["alunos"] == r2.json()["alunos"]

    def test_dado_persiste_apos_atualizacao(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        requests.patch(f"{BASE_URL}/api/v1/alunos/GES1", json={"nome": "Ana Souza"})

        r = requests.get(f"{BASE_URL}/api/v1/alunos/GES1")
        assert r.status_code == 200
        assert r.json()["nome"] == "Ana Souza"

    def test_dado_persiste_apos_remocao_parcial(self):
        cadastrar("Ana Lima", "ana@email.com", "GES")
        cadastrar("Bruno Silva", "bruno@email.com", "GES")
        cadastrar("Carlos Souza", "carlos@email.com", "GES")

        requests.delete(f"{BASE_URL}/api/v1/alunos/GES2")

        r = requests.get(f"{BASE_URL}/api/v1/alunos/")
        assert r.json()["total"] == 2

        ids = [a["id"] for a in r.json()["alunos"]]
        assert "GES1" in ids
        assert "GES3" in ids
        assert "GES2" not in ids