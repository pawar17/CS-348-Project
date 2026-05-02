from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(fields=["course", "student"], name="enroll_course_student_idx"),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(fields=["age"], name="students_age_report_idx"),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(fields=["gpa"], name="students_gpa_report_idx"),
        ),
    ]
