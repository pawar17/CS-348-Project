from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseForm, EnrollmentForm, ReportFilterForm, StudentForm
from .models import Course, Enrollment, Student
from .sql_checks import student_exists


def home(request):
    students = Student.objects.all().order_by("name")
    courses = Course.objects.all().order_by("course_name")
    enrollments = (
        Enrollment.objects.select_related("student", "course")
        .order_by("-enrollment_id")[:20]
    )

    student_form = StudentForm()
    course_form = CourseForm()
    enroll_form = EnrollmentForm()

    report_form = ReportFilterForm(request.GET or None)
    rows = []
    sql_preview = None
    ran_report = False

    if request.GET.get("run_report") and report_form.is_valid():
        data = report_form.cleaned_data
        qs = Student.objects.all()

        if data.get("min_age") is not None:
            qs = qs.filter(age__gte=data["min_age"])
        if data.get("max_age") is not None:
            qs = qs.filter(age__lte=data["max_age"])
        if data.get("min_gpa") is not None:
            qs = qs.filter(gpa__gte=data["min_gpa"])
        if data.get("max_gpa") is not None:
            qs = qs.filter(gpa__lte=data["max_gpa"])
        if data.get("course"):
            qs = qs.filter(enrollments__course=data["course"]).distinct()

        rows = list(qs.order_by("name").values("student_id", "name", "age", "gpa"))

        sql_preview = (
            "SELECT DISTINCT s.student_id, s.name, s.age, s.gpa\n"
            "FROM students s\n"
        )
        if data.get("course"):
            sql_preview += (
                "JOIN enrollments e ON e.student_id = s.student_id\n"
                "JOIN courses c ON c.course_id = e.course_id\n"
                "WHERE c.course_id = %s\n"
            )
            extra = []
            if data.get("min_age") is not None:
                extra.append("s.age >= %s")
            if data.get("max_age") is not None:
                extra.append("s.age <= %s")
            if data.get("min_gpa") is not None:
                extra.append("s.gpa >= %s")
            if data.get("max_gpa") is not None:
                extra.append("s.gpa <= %s")
            if extra:
                sql_preview += "AND " + "\nAND ".join(extra) + "\n"
        else:
            clauses = []
            if data.get("min_age") is not None:
                clauses.append("s.age >= %s")
            if data.get("max_age") is not None:
                clauses.append("s.age <= %s")
            if data.get("min_gpa") is not None:
                clauses.append("s.gpa >= %s")
            if data.get("max_gpa") is not None:
                clauses.append("s.gpa <= %s")
            if clauses:
                sql_preview += "WHERE " + "\nAND ".join(clauses) + "\n"
        sql_preview += "ORDER BY s.name;"
        ran_report = True

    elif request.GET.get("run_report"):
        messages.error(request, "Invalid filters.")

    return render(
        request,
        "core/home.html",
        {
            "students": students,
            "courses": courses,
            "enrollments": enrollments,
            "student_form": student_form,
            "course_form": course_form,
            "enroll_form": enroll_form,
            "report_form": report_form,
            "rows": rows,
            "sql_preview": sql_preview,
            "ran_report": ran_report,
        },
    )


def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added.")
            return redirect("home")
    else:
        form = StudentForm()
    return render(request, "core/student_form.html", {"form": form, "title": "Add Student"})


def student_update(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated.")
            return redirect("home")
    else:
        form = StudentForm(instance=student)
    return render(
        request,
        "core/student_form.html",
        {"form": form, "title": "Edit Student", "student": student},
    )


def student_delete(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted.")
        return redirect("home")
    return render(request, "core/student_confirm_delete.html", {"student": student})


def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added.")
            return redirect("home")
    else:
        form = CourseForm()
    return render(request, "core/course_form.html", {"form": form, "title": "Add Course"})


def course_update(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect("home")
    else:
        form = CourseForm(instance=course)
    return render(
        request,
        "core/course_form.html",
        {"form": form, "title": "Edit Course", "course": course},
    )


def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("home")
    return render(request, "core/course_confirm_delete.html", {"course": course})


def enroll(request):
    if request.method != "POST":
        return redirect("home")

    form = EnrollmentForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Could not enroll.")
        return redirect("home")

    student = form.cleaned_data["student"]
    course = form.cleaned_data["course"]
    try:
        with transaction.atomic():
            if not student_exists(student.student_id):
                raise ValueError("missing student")
            locked = Student.objects.select_for_update().get(pk=student.student_id)
            _, created = Enrollment.objects.get_or_create(student=locked, course=course)
    except ValueError:
        messages.error(request, "Student not found.")
        return redirect("home")
    except IntegrityError:
        messages.info(request, "Already enrolled in that course.")
        return redirect("home")

    if created:
        messages.success(request, "Enrollment saved.")
    else:
        messages.info(request, "Already enrolled in that course.")
    return redirect("home")


def enrollment_delete(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Enrollment removed.")
        return redirect("home")
    return render(
        request,
        "core/enrollment_confirm_delete.html",
        {"enrollment": enrollment},
    )
