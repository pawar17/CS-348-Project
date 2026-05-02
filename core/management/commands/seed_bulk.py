import itertools
import random
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from core.models import Course, Enrollment, Student


def purge_legacy_synthetic_data():
    enrollments = Enrollment.objects.filter(
        Q(course__course_name__startswith="GEN ")
        | Q(student__name__contains="#")
    ).delete()[0]
    courses = Course.objects.filter(course_name__startswith="GEN ").delete()[0]
    students = Student.objects.filter(name__contains="#").delete()[0]
    return enrollments, courses, students


# Purdue catalog style: https://catalog.purdue.edu/content.php?catoid=7&navoid=2928
PURDUE_CATALOG_COURSES = [
    "AAE 19000 - Introduction To Aerospace Engineering",
    "AAE 20300 - Aeromechanics I",
    "AAE 33300 - Fluid Mechanics",
    "AAE 33400 - Aerodynamics",
    "CS 18000 - Problem Solving And Object-Oriented Programming",
    "CS 18200 - Foundations Of Computer Science",
    "CS 24000 - Programming In C",
    "CS 25000 - Computer Architecture",
    "CS 25100 - Data Structures And Algorithms",
    "CS 25200 - Systems Programming",
    "CS 34800 - Information Systems",
    "CS 37300 - Data Structures And Algorithms For Data Science",
    "CS 38100 - Analysis Of Algorithms",
    "CS 42200 - Network Protocols",
    "CS 42600 - Computer Security",
    "CS 44800 - Introduction To Relational Database Systems",
    "MA 16100 - Plane Analytic Geometry And Calculus I",
    "MA 16500 - Analytic Geometry And Calculus I",
    "MA 26100 - Multivariate Calculus",
    "MA 26500 - Linear Algebra",
    "STAT 41600 - Probability",
    "STAT 41700 - Statistical Theory",
    "ECE 20001 - Electrical Engineering Fundamentals I",
    "ECE 20002 - Electrical Engineering Fundamentals II",
    "ECE 26400 - Advanced C Programming",
    "PHYS 17200 - Modern Mechanics",
    "PHYS 22000 - General Physics",
    "CHEM 11500 - General Chemistry",
    "ENGL 10600 - First-Year Writing",
    "ECON 25100 - Microeconomics",
    "ME 20000 - Thermodynamics I",
    "IE 34300 - Engineering Economics",
    "CNIT 17600 - Information Technology Architectures",
    "BIOL 11000 - Fundamentals Of Biology I",
    "PSY 12000 - Elementary Psychology",
    "SOC 10000 - Introductory Sociology",
    "HIST 10400 - Introduction To The Modern World",
    "COM 11400 - Fundamentals Of Speech Communication",
    "ASM 10400 - Introduction To Animal Agriculture",
    "AGRY 10000 - Crop Production",
    "MGMT 20000 - Introductory Accounting",
    "FIN 24000 - Fundamentals Of Finance",
    "PHIL 11000 - Introduction To Philosophy",
    "POL 13000 - Introduction To International Relations",
    "ASTR 26400 - Descriptive Astronomy: Stars And Galaxies",
]

_FIRST = (
    "Alex Jordan Sam Taylor Morgan Casey Riley Quinn Avery Jamie Drew Skyler "
    "Parker Reese Logan Blake Rowan Sage River Cameron Dakota Emerson Finley "
    "Hayden Jesse Kai Lane Max Nico Orion Phoenix Shiloh Tatum Vale River"
).split()

_LAST = (
    "Kim Lee Patel Garcia Chen Nguyen Williams Brown Jones Miller Davis Wilson "
    "Moore Taylor Anderson Thomas Jackson White Harris Martin Thompson "
    "Martinez Robinson Clark Rodriguez Lewis Walker Hall Allen Young King Wright "
    "Scott Torres Hill Green Adams Baker Nelson Carter Mitchell Perez Roberts"
).split()


class Command(BaseCommand):
    help = (
        "Add many students (unique first+last names, no # suffix), Purdue-style "
        "catalog courses, and random enrollments. Use --purge-legacy to delete old "
        "GEN* courses and #-named students from earlier runs."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--students",
            type=int,
            default=100,
            help="Number of new students to create (default: 100). Use 0 with "
            "--purge-legacy to only remove legacy rows.",
        )
        parser.add_argument(
            "--courses",
            type=int,
            default=24,
            help=(
                "How many distinct catalog courses to ensure exist "
                f"(max {len(PURDUE_CATALOG_COURSES)}, default: 24)."
            ),
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Random seed for reproducible data (optional).",
        )
        parser.add_argument(
            "--purge-legacy",
            action="store_true",
            help="Delete GEN* synthetic courses, students with '#' in the name, "
            "and their enrollments (then seed unless --students 0).",
        )

    def handle(self, *args, **options):
        n_students = options["students"]
        if n_students < 0:
            raise CommandError("--students must be >= 0")

        if options["purge_legacy"]:
            e, c, s = purge_legacy_synthetic_data()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Purge: removed {e} enrollments, {c} GEN courses, {s} #-named students."
                )
            )

        if n_students == 0:
            if not options["purge_legacy"]:
                self.stderr.write(
                    self.style.WARNING(
                        "Nothing to do (students=0). Use --purge-legacy --students 0 to only remove legacy data."
                    )
                )
            return

        n_courses = max(1, min(options["courses"], len(PURDUE_CATALOG_COURSES)))
        if options["seed"] is not None:
            random.seed(options["seed"])

        max_unique = len(_FIRST) * len(_LAST)
        if n_students > max_unique:
            self.stderr.write(
                self.style.WARNING(
                    f"Requested {n_students} students but only {max_unique} unique name pairs; "
                    f"creating {max_unique}."
                )
            )
            n_students = max_unique

        pairs = list(itertools.product(_FIRST, _LAST))
        random.shuffle(pairs)

        with transaction.atomic():
            courses = []
            for title in PURDUE_CATALOG_COURSES[:n_courses]:
                c, _ = Course.objects.get_or_create(course_name=title)
                courses.append(c)

            batch = []
            for i in range(n_students):
                first, last = pairs[i]
                name = f"{first} {last}"
                age = random.randint(17, 28)
                gpa = Decimal(str(round(random.uniform(2.0, 4.0), 2)))
                batch.append(Student(name=name, age=age, gpa=gpa))

            Student.objects.bulk_create(batch, batch_size=250)

            enrollments = []
            for st in batch:
                n_enroll = random.randint(1, min(5, len(courses)))
                for co in random.sample(courses, n_enroll):
                    enrollments.append(Enrollment(student=st, course=co))

            Enrollment.objects.bulk_create(enrollments, batch_size=500, ignore_conflicts=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {n_students} students (no # suffix), "
                f"ensured {len(courses)} Purdue catalog courses, "
                f"created {len(enrollments)} enrollment rows."
            )
        )
