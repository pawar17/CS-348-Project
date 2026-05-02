from django import forms

from .models import Course, Enrollment, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "age", "gpa"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "age": forms.NumberInput(attrs={"class": "input", "min": 0, "max": 120}),
            "gpa": forms.NumberInput(
                attrs={"class": "input", "min": 0, "max": 4, "step": "0.01"}
            ),
        }


class ReportFilterForm(forms.Form):
    min_age = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "e.g. 18"}),
    )
    max_age = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "e.g. 22"}),
    )
    min_gpa = forms.DecimalField(
        required=False,
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "input", "min": 0, "max": 4, "step": "0.01", "placeholder": "3.0"}
        ),
    )
    max_gpa = forms.DecimalField(
        required=False,
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "input", "min": 0, "max": 4, "step": "0.01", "placeholder": "4.0"}
        ),
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        required=False,
        empty_label="All courses",
        widget=forms.Select(attrs={"class": "input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.all().order_by("course_name")


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["course_name"]
        widgets = {
            "course_name": forms.TextInput(
                attrs={"class": "input", "placeholder": "e.g. CS 34800 - Information Systems"}
            ),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course"]
        widgets = {
            "student": forms.Select(attrs={"class": "input"}),
            "course": forms.Select(attrs={"class": "input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.all().order_by("name")
        self.fields["course"].queryset = Course.objects.all().order_by("course_name")
