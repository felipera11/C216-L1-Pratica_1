def generate_enrollment_id(course_abbr: str, cur) -> str:
    """Gera ID sequencial por curso usando o banco. IDs deletados não são reutilizados."""
    cur.execute("""
        INSERT INTO enrollment_counters (curso, contador)
        VALUES (%s, 1)
        ON CONFLICT (curso) DO UPDATE
            SET contador = enrollment_counters.contador + 1
        RETURNING contador
    """, (course_abbr,))
    contador = cur.fetchone()[0]
    return f"{course_abbr}{contador}"


def validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]