from utils import print_header, print_separator
from students import (
    create_student,
    list_students,
    find_student,
    update_student,
    delete_student,
)

ACTIONS = {
    "1": ("Cadastrar aluno",           create_student),
    "2": ("Listar alunos",             list_students),
    "3": ("Buscar aluno por matrícula", find_student),
    "4": ("Atualizar aluno",           update_student),
    "5": ("Remover aluno",             delete_student),
}


def show_menu():
    print_header("SISTEMA DE GERENCIAMENTO DE ALUNOS")
    for code, (description, _) in ACTIONS.items():
        print(f"  [{code}] {description}")
    print("  [0] Sair")
    print_separator()
    return input("  Escolha uma opção: ").strip()


def run():
    print("\n  Bem-vindo ao Sistema de Gerenciamento de Alunos!")

    while True:
        option = show_menu()

        if option == "0":
            print("\n  Encerrando o sistema. Até logo!\n")
            break
        elif option in ACTIONS:
            _, action = ACTIONS[option]
            action()
        else:
            print("\n  ⚠  Opção inválida. Escolha entre 0 e 5.")

        input("\n  Pressione Enter para continuar...")