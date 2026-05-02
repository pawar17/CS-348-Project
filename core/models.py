from django.db import models


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    age = models.PositiveSmallIntegerField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table = "students"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["age"], name="students_age_report_idx"),
            models.Index(fields=["gpa"], name="students_gpa_report_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=200)

    class Meta:
        db_table = "courses"
        ordering = ["course_name"]

    def __str__(self):
        return self.course_name


class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_column="student_id",
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        db_column="course_id",
        related_name="enrollments",
    )

    class Meta:
        db_table = "enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="uniq_enrollment_student_course",
            )
        ]
        indexes = [
            models.Index(fields=["course", "student"], name="enroll_course_student_idx"),
        ]

    def __str__(self):
        return f"{self.student_id} -> {self.course_id}"
