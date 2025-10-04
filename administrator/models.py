from django.db import models



from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        HR = 'HR', 'HR Manager'
        DEV = 'DEV', 'Developer'

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    skills = models.CharField(max_length=100)
    domain=models.CharField(max_length=100)
    address = models.TextField()
    company_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=5, choices=Roles.choices, default=Roles.DEV)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff      = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
  
  

   
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.email
    


    # administrator/models/course.py

from django.db import models
from administrator.models import User  # adjust if User model is elsewhere

class Course(models.Model):
    LEVEL_CHOICES = [
        ('Basic', 'Basic'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    DOMAIN_CHOICES = [
        ('Web Development', 'Web Development'),
        ('Data Science', 'Data Science'),
        ('AI/ML', 'AI/ML'),
        ('Cyber Security', 'Cyber Security'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Certification(models.Model):
    LEVEL_CHOICES = [
        ('Basic', 'Basic'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('Passed', 'Passed'),
        ('Failed', 'Failed'),
        ('Pending', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DEV'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    score = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.course.title} ({self.level})"
    


    # administrator/models/question.py

from django.db import models


class Question(models.Model):
    STAGE_CHOICES = [
        ('Basic', 'Basic'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])

    def __str__(self):
        return self.question_text[:50]
    



    # models/certification.py
from django.db import models
from django.conf import settings
from .models import Course

class Certificate(models.Model):
    LEVEL_CHOICES = [
        ('Basic', 'Basic'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    
    developer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DEV'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.developer.name} - {self.course.title} - {self.level}"

class CourseEnrollment(models.Model):
    developer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DEV'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.developer.name} -> {self.course.title}"

class TestSettings(models.Model):
    pass_percentage = models.PositiveIntegerField(default=50)
    time_limit = models.PositiveIntegerField(default=30)  # in minutes
    
    # Using singleton pattern to ensure only one settings record exists
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def __str__(self):
        return f"Test Settings (Pass: {self.pass_percentage}%, Time: {self.time_limit} mins)"

# Removed PasswordResetOTP model - replaced by Django built-in password reset
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.user.email}"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and self.expires_at > timezone.now()