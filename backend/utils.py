from data import AVAILABLE_COURSES, enrollment_counters


def print_separator(char="─", width=50):
    print(char * width)


def print_header(title):
    print()
    print_separator("═")
    print(f"  {title}")
    print_separator("═")


def display_student(student):
    print_separator()
    print(f"  Matrícula : {student['enrollment_id']}")
    print(f"  Nome      : {student['name']}")
    print(f"  E-mail    : {student['email']}")
    print(f"  Curso     : {student['course_code']} - {student['course_name']}")
    print_separator()


def generate_enrollment_id(course_code):
    if course_code not in enrollment_counters:
        enrollment_counters[course_code] = 0
    enrollment_counters[course_code] += 1
    return f"{course_code}{enrollment_counters[course_code]}"


def validate_email(email):
    return "@" in email and "." in email.split("@")[-1]


def select_course():
    print("\n  Cursos disponíveis:")
    for code, (abbr, name) in AVAILABLE_COURSES.items():
        print(f"    [{code}] {abbr} - {name}")
    print()

    while True:
        choice = input("  Informe o número do curso: ").strip()
        if choice in AVAILABLE_COURSES:
            abbr, name = AVAILABLE_COURSES[choice]
            return abbr, name
        print("  ⚠  Opção inválida. Tente novamente.")