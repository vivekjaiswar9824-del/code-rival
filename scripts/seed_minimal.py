# Minimal seed script for baseline data
from administrator.models import User, Course, Question, Certification, CourseEnrollment, TestSettings
from django.contrib.auth.hashers import make_password

print("Seeding minimal baseline data...")

# Ensure Test Settings exists
settings = TestSettings.get_settings()
print(f"TestSettings: pass={settings.pass_percentage}%, time={settings.time_limit} mins")

# Create Course
course, created = Course.objects.get_or_create(
    title="Data Science 101",
    defaults={
        "description": "Introductory data science course covering Python, Pandas, and basic ML.",
        "domain": "Data Science",
        "is_active": True,
    }
)
print(f"Course: {course.title} ({'created' if created else 'existing'})")

# Create HR user
hr_email = "hr.seed@example.com"
hr_defaults = {
    "name": "Seed HR",
    "skills": "management",
    "domain": "HR",
    "address": "Pune",
    "company_name": "CodeRivals Inc",
    "phone_number": "9990000001",
    "role": User.Roles.HR,
    "is_active": True,
    "is_verified": True,
    "is_staff": False,
}
hr, hr_created = User.objects.get_or_create(email=hr_email, defaults=hr_defaults)
if hr_created:
    hr.password = make_password("Pass@1234")
    hr.save()
print(f"HR: {hr.email} ({'created' if hr_created else 'existing'})")

# Create DEV user
dev_email = "dev.seed@example.com"
dev_defaults = {
    "name": "Seed Dev",
    "skills": "python,pandas",
    "domain": "Data Science",
    "address": "Pune",
    "company_name": "CodeRivals Inc",
    "phone_number": "9990000002",
    "role": User.Roles.DEV,
    "is_active": True,
    "is_verified": True,
    "is_staff": False,
}
dev, dev_created = User.objects.get_or_create(email=dev_email, defaults=dev_defaults)
if dev_created:
    dev.password = make_password("Pass@1234")
    dev.save()
print(f"DEV: {dev.email} ({'created' if dev_created else 'existing'})")

# Enroll DEV in course
enroll, en_created = CourseEnrollment.objects.get_or_create(developer=dev, course=course)
print(f"Enrollment: {dev.email} -> {course.title} ({'created' if en_created else 'existing'})")

# Create a few Basic questions if less than 3 exist
existing_qs = Question.objects.filter(course=course, stage='Basic').count()
needed = max(0, 3 - existing_qs)
created_q = 0
for i in range(needed):
    q = Question.objects.create(
        course=course,
        stage='Basic',
        question_text=f"What does Pandas primarily help with? (q{i+1})",
        option_a="Web Development",
        option_b="Data Analysis",
        option_c="Game Design",
        option_d="Operating Systems",
        correct_answer='B',
    )
    created_q += 1
print(f"Questions (Basic): existing={existing_qs}, created_now={created_q}")

# Create a passed certification for DEV for result testing (if not present)
cert, cert_created = Certification.objects.get_or_create(
    user=dev,
    course=course,
    level='Basic',
    defaults={
        'score': 85,
        'status': 'Passed',
    }
)
print(f"Certification: {dev.email} - {course.title} (Basic) ({'created' if cert_created else 'existing'})")

print("Seeding complete.")
