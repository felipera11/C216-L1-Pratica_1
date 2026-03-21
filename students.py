from data import students
from utils import (
    display_student,
    generate_enrollment_id,
    print_header,
    print_separator,
    select_course,
    validate_email,
)


def create_student():
    print_header("CADASTRAR ALUNO")

    while True:
        name = input("\n  Nome completo: ").strip()
        if len(name) >= 3:
            break
        print("  ⚠  Nome deve ter pelo menos 3 caracteres.")

    while True:
        email = input("  E-mail: ").strip().lower()
        if not validate_email(email):
            print("  ⚠  E-mail inválido. Ex: nome@dominio.com")
            continue
        existing_emails = [s["email"] for s in students.values()]
        if email in existing_emails:
            print("  ⚠  Já existe um aluno com esse e-mail.")
            continue
        break

    course_code, course_name = select_course()
    enrollment_id = generate_enrollment_id(course_code)

    students[enrollment_id] = {
        "enrollment_id": enrollment_id,
        "name": name,
        "email": email,
        "course_code": course_code,
        "course_name": course_name,
    }

    print(f"\n  ✔  Aluno cadastrado com sucesso!")
    print(f"     Matrícula gerada: {enrollment_id}")
    display_student(students[enrollment_id])


def list_students():
    print_header("LISTAR ALUNOS")

    if not students:
        print("\n  Nenhum aluno cadastrado ainda.")
        return

    print(f"\n  Total: {len(students)} aluno(s)\n")
    print_separator()
    for student in students.values():
        print(
            f"  [{student['enrollment_id']:6s}]  {student['name']:30s}  "
            f"{student['course_code']}  |  {student['email']}"
        )
    print_separator()


def find_student():
    print_header("BUSCAR ALUNO")

    if not students:
        print("\n  Nenhum aluno cadastrado.")
        return

    enrollment_id = input("\n  Informe a matrícula (ex: GES1): ").strip().upper()

    if enrollment_id in students:
        print("\n  Aluno encontrado:")
        display_student(students[enrollment_id])
    else:
        print(f"\n  ⚠  Matrícula '{enrollment_id}' não encontrada.")


def update_student():
    print_header("ATUALIZAR ALUNO")

    if not students:
        print("\n  Nenhum aluno cadastrado.")
        return

    enrollment_id = input("\n  Informe a matrícula do aluno a atualizar: ").strip().upper()

    if enrollment_id not in students:
        print(f"\n  ⚠  Matrícula '{enrollment_id}' não encontrada.")
        return

    student = students[enrollment_id]
    print("\n  Dados atuais:")
    display_student(student)
    print("  Deixe em branco para manter o valor atual.\n")

    new_name = input(f"  Novo nome [{student['name']}]: ").strip()
    if new_name:
        if len(new_name) >= 3:
            student["name"] = new_name
        else:
            print("  ⚠  Nome inválido, mantendo o atual.")

    new_email = input(f"  Novo e-mail [{student['email']}]: ").strip().lower()
    if new_email:
        if not validate_email(new_email):
            print("  ⚠  E-mail inválido, mantendo o atual.")
        else:
            existing_emails = [
                s["email"] for id_, s in students.items() if id_ != enrollment_id
            ]
            if new_email in existing_emails:
                print("  ⚠  E-mail já em uso, mantendo o atual.")
            else:
                student["email"] = new_email

    print(f"\n  Curso atual: {student['course_code']} - {student['course_name']}")
    change_course = input("  Deseja alterar o curso? (s/N): ").strip().lower()
    if change_course == "s":
        new_code, new_course_name = select_course()
        student["course_code"] = new_code
        student["course_name"] = new_course_name

    print("\n  ✔  Dados atualizados com sucesso!")
    display_student(student)


def delete_student():
    print_header("REMOVER ALUNO")

    if not students:
        print("\n  Nenhum aluno cadastrado.")
        return

    enrollment_id = input("\n  Informe a matrícula do aluno a remover: ").strip().upper()

    if enrollment_id not in students:
        print(f"\n  ⚠  Matrícula '{enrollment_id}' não encontrada.")
        return

    student = students[enrollment_id]
    print("\n  Aluno a ser removido:")
    display_student(student)

    confirm = input("  Confirma a remoção? (s/N): ").strip().lower()
    if confirm == "s":
        del students[enrollment_id]
        print(f"\n  ✔  Aluno '{student['name']}' removido com sucesso.")
    else:
        print("\n  Operação cancelada.")