from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from core.models import Course, Enrollment, Student


class AppIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = Course.objects.create(course_name="CS 34800 - Information Systems")
        cls.student = Student.objects.create(
            name="Smoke Test Student",
            age=20,
            gpa=Decimal("3.25"),
        )
        Enrollment.objects.create(student=cls.student, course=cls.course)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_home(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_home_shows_students_and_courses(self):
        r = self.client.get(reverse("home"))
        self.assertContains(r, "Smoke Test Student")
        self.assertContains(r, "CS 34800 - Information Systems")

    def test_report_empty(self):
        r = self.client.get(reverse("home"), {"run_report": "1"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context["ran_report"])

    def test_report_filtered_gpa(self):
        r = self.client.get(
            reverse("home"),
            {"run_report": "1", "min_gpa": "3.0", "max_gpa": "4.0"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Smoke Test Student")

    def test_report_filtered_with_course_join(self):
        r = self.client.get(
            reverse("home"),
            {
                "run_report": "1",
                "min_gpa": "3.0",
                "max_gpa": "4.0",
                "course": str(self.course.pk),
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Smoke Test Student")

    def test_report_no_results(self):
        r = self.client.get(
            reverse("home"),
            {"run_report": "1", "min_gpa": "3.99", "max_gpa": "4.0"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["rows"]), 0)

    def test_student_create(self):
        n = Student.objects.count()
        r = self.client.post(
            reverse("student_create"),
            {"name": "New Student", "age": "19", "gpa": "3.50"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Student.objects.count(), n + 1)

    def test_student_update(self):
        sid = self.student.pk
        r = self.client.post(
            reverse("student_update", args=[sid]),
            {"name": "Updated Name", "age": "21", "gpa": "3.00"},
        )
        self.assertEqual(r.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, "Updated Name")

    def test_student_delete(self):
        sid = self.student.pk
        self.assertEqual(
            self.client.get(reverse("student_delete", args=[sid])).status_code,
            200,
        )
        r = self.client.post(reverse("student_delete", args=[sid]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Student.objects.filter(pk=sid).exists())

    def test_enroll_post_creates_row(self):
        st = Student.objects.create(name="Enroll Target", age=22, gpa=Decimal("3.10"))
        n = Enrollment.objects.count()
        r = self.client.post(
            reverse("enroll"),
            {"student": str(st.pk), "course": str(self.course.pk)},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Enrollment.objects.count(), n + 1)

    def test_enroll_duplicate_is_idempotent(self):
        r = self.client.post(
            reverse("enroll"),
            {"student": str(self.student.pk), "course": str(self.course.pk)},
        )
        self.assertEqual(r.status_code, 302)

    def test_enrollment_delete(self):
        e = Enrollment.objects.create(
            student=Student.objects.create(name="Del Target", age=20, gpa=Decimal("2.0")),
            course=self.course,
        )
        r = self.client.post(reverse("enrollment_delete", args=[e.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Enrollment.objects.filter(pk=e.pk).exists())
