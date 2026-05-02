from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("students/add/", views.student_create, name="student_create"),
    path("students/<int:student_id>/edit/", views.student_update, name="student_update"),
    path("students/<int:student_id>/delete/", views.student_delete, name="student_delete"),
    path("courses/add/", views.course_create, name="course_create"),
    path("courses/<int:course_id>/edit/", views.course_update, name="course_update"),
    path("courses/<int:course_id>/delete/", views.course_delete, name="course_delete"),
    path("enroll/", views.enroll, name="enroll"),
    path("enroll/<int:enrollment_id>/delete/", views.enrollment_delete, name="enrollment_delete"),
]
