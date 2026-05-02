import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("course_id", models.AutoField(primary_key=True, serialize=False)),
                ("course_name", models.CharField(max_length=200)),
            ],
            options={
                "db_table": "courses",
                "ordering": ["course_name"],
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("student_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("age", models.PositiveSmallIntegerField()),
                ("gpa", models.DecimalField(decimal_places=2, max_digits=3)),
            ],
            options={
                "db_table": "students",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("enrollment_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "course",
                    models.ForeignKey(
                        db_column="course_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="core.course",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        db_column="student_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="core.student",
                    ),
                ),
            ],
            options={
                "db_table": "enrollments",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("student", "course"),
                        name="uniq_enrollment_student_course",
                    )
                ],
            },
        ),
    ]
