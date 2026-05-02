from django.db import connection


def student_exists(student_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM students WHERE student_id = %s",
            [student_id],
        )
        return cursor.fetchone() is not None
