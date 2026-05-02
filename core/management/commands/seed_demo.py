from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import Course, Enrollment, Student


class Command(BaseCommand):
    help = "Insert sample courses, students, and enrollments for demos."

    def handle(self, *args, **options):
        courses_data = [
            "CS 34800 - Information Systems",
            "CS 25200 - Systems Programming",
            "MA 26500 - Linear Algebra",
        ]
        courses = []
        for name in courses_data:
            c, _ = Course.objects.get_or_create(course_name=name)
            courses.append(c)

        students_data = [
            ("Alex Kim", 20, Decimal("3.45")),
            ("Jordan Lee", 19, Decimal("3.80")),
            ("Sam Patel", 21, Decimal("2.95")),
        ]
        for name, age, gpa in students_data:
            s, created = Student.objects.get_or_create(
                name=name,
                defaults={"age": age, "gpa": gpa},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Student: {s}"))
            else:
                self.stdout.write(f"Student exists: {s}")

        students = list(Student.objects.all()[:3])
        if len(students) >= 2 and len(courses) >= 2:
            pairs = [
                (students[0], courses[0]),
                (students[0], courses[1]),
                (students[1], courses[0]),
                (students[2], courses[2]) if len(students) > 2 else None,
            ]
            for pair in pairs:
                if not pair:
                    continue
                st, co = pair
                e, created = Enrollment.objects.get_or_create(student=st, course=co)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Enrollment: {st.name} -> {co.course_name}")
                    )

        self.stdout.write(self.style.SUCCESS("Done. Courses dropdown and course filter will have data."))
