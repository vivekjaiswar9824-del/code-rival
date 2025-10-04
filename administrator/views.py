
from django import forms
from .models import User 
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import DeveloperRegistrationForm, HRRegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from administrator.models import User, Course, Certification, TestSettings
from .models import Course
from .forms import CourseForm
from .models import Certificate
from django.core.mail import send_mail
from django.utils import timezone
import random
from datetime import timedelta
from django.shortcuts import render, redirect
from .forms import CertificationForm
from .models import Certification
from .forms import QuestionForm
from .models import Course
from .forms import CourseForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
import os
from django.views.decorators.http import require_POST
from .models import Course, CourseEnrollment
from django.shortcuts import render
from .models import Question
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.utils import timezone
import pandas as pd
from xhtml2pdf import pisa
import io
from django.contrib.auth.hashers import make_password
from .certificate_generator import CertificateGenerator
from django.http import FileResponse
import json
from twilio.rest import Client

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse


def generate_certificate_pdf(certificate):
    """
    Generate a certificate file using ReportLab for professional PDF creation
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfutils
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        
        # Prepare context for the certificate template
        context = {
            'developer': certificate.developer,
            'course': certificate.course,
            'level': certificate.level,
            'certificate': certificate,
            'today': timezone.now().strftime('%B %d, %Y')
        }
        
        # Render the HTML template for web view
        html_content = render_to_string('certificate/certificate_template.html', context)
        
        # Create the certificates directory if it doesn't exist
        certificates_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
        os.makedirs(certificates_dir, exist_ok=True)
        
        # Save as HTML file for web view
        html_filename = f"certificate_{certificate.developer.id}_{certificate.course.id}_{certificate.level}_{certificate.id}.html"
        html_file_path = os.path.join(certificates_dir, html_filename)
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Store the HTML file path in the model
        certificate.certificate_file = f'certificates/{html_filename}'
        certificate.save()
        
        # Generate PDF using ReportLab
        pdf_filename = f"certificate_{certificate.developer.id}_{certificate.course.id}_{certificate.level}_{certificate.id}.pdf"
        pdf_file_path = os.path.join(certificates_dir, pdf_filename)
        
        # Create PDF with ReportLab
        page_width, page_height = landscape(A4)
        c = canvas.Canvas(pdf_file_path, pagesize=landscape(A4))
        
        # Define colors
        blue_color = HexColor('#1e3a8a')
        light_blue = HexColor('#3b82f6')
        red_color = HexColor('#dc2626')
        gray_color = HexColor('#666666')
        
        # Draw outer border
        c.setStrokeColor(blue_color)
        c.setLineWidth(8)
        c.rect(30, 30, page_width-60, page_height-60)
        
        # Draw inner border
        c.setStrokeColor(light_blue)
        c.setLineWidth(2)
        c.rect(50, 50, page_width-100, page_height-100)
        
        # Title section
        c.setFillColor(blue_color)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(page_width/2, page_height-120, "CODE RIVAL")
        
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(page_width/2, page_height-170, "CERTIFICATE OF COMPLETION")
        
        # Subtitle
        c.setFillColor(gray_color)
        c.setFont("Helvetica", 16)
        c.drawCentredString(page_width/2, page_height-210, "This is to certify that")
        
        # Recipient name
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 28)
        name_text = certificate.developer.name.upper()
        c.drawCentredString(page_width/2, page_height-260, name_text)
        
        # Underline for name
        c.setStrokeColor(blue_color)
        c.setLineWidth(2)
        name_width = c.stringWidth(name_text, "Helvetica-Bold", 28)
        c.line(page_width/2 - name_width/2, page_height-270, page_width/2 + name_width/2, page_height-270)
        
        # Course completion text
        c.setFillColor(gray_color)
        c.setFont("Helvetica", 16)
        c.drawCentredString(page_width/2, page_height-310, "has successfully completed the")
        
        # Level badge
        level_text = f"{certificate.level} Level".upper()
        c.setFillColor(red_color)
        c.setFont("Helvetica-Bold", 18)
        level_width = c.stringWidth(level_text, "Helvetica-Bold", 18)
        
        # Draw level badge background
        c.setFillColor(HexColor('#fef2f2'))
        c.setStrokeColor(red_color)
        c.setLineWidth(2)
        badge_x = page_width/2 - level_width/2 - 15
        badge_y = page_height-345
        c.roundRect(badge_x, badge_y, level_width + 30, 25, 12, fill=1, stroke=1)
        
        # Draw level text
        c.setFillColor(red_color)
        c.drawCentredString(page_width/2, page_height-340, level_text)
        
        # Course info
        c.setFillColor(gray_color)
        c.setFont("Helvetica", 16)
        c.drawCentredString(page_width/2, page_height-380, "course in")
        
        c.setFillColor(blue_color)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(page_width/2, page_height-410, certificate.course.title.upper())
        
        c.setFillColor(gray_color)
        c.setFont("Helvetica", 16)
        c.drawCentredString(page_width/2, page_height-440, f"Domain: {certificate.course.domain}")
        
        # Date
        c.setFillColor(gray_color)
        c.setFont("Helvetica", 14)
        date_text = f"Date of Completion: {certificate.issued_at.strftime('%B %d, %Y')}"
        c.drawCentredString(page_width/2, page_height-480, date_text)
        
        # Signatures
        sig_y = 120
        sig1_x = page_width/4
        sig2_x = 3*page_width/4
        
        # Signature lines
        c.setStrokeColor(blue_color)
        c.setLineWidth(1)
        c.line(sig1_x-80, sig_y, sig1_x+80, sig_y)
        c.line(sig2_x-80, sig_y, sig2_x+80, sig_y)
        
        # Signature labels
        c.setFillColor(gray_color)
        c.setFont("Helvetica", 12)
        c.drawCentredString(sig1_x, sig_y-20, "COURSE INSTRUCTOR")
        c.drawCentredString(sig2_x, sig_y-20, "PROGRAM DIRECTOR")
        
        # Certificate ID
        c.setFillColor(HexColor('#999999'))
        c.setFont("Helvetica", 10)
        cert_id = f"Certificate ID: CR-{certificate.id}-{certificate.issued_at.year}"
        c.drawRightString(page_width-40, 40, cert_id)
        
        # Save the PDF
        c.save()
        
        # Verify the PDF file was created and has content
        if os.path.exists(pdf_file_path) and os.path.getsize(pdf_file_path) > 0:
            print(f"Successfully generated PDF with ReportLab: {pdf_filename}")
            return True
        else:
            print(f"PDF file creation failed or file is empty: {pdf_filename}")
            return False
            
    except Exception as e:
        print(f"Error generating certificate file: {e}")
        import traceback
        traceback.print_exc()
        return False


#======================================= ADMIN  ==============================================================#

@login_required
def admin_dashboard(request):
    developer_count = User.objects.filter(role='DEV').count()
    enrollments = CourseEnrollment.objects.select_related('developer', 'course')
    hr_count = User.objects.filter(role='HR').count()
    course_count = Course.objects.count()
    cert_count = Certification.objects.count()
    certifications = Certification.objects.select_related('user', 'course')
    developers = User.objects.filter(role='DEV')[:5]
    all_hrs = User.objects.filter(role='HR')

    return render(request, 'dashboard/admin.html', {
        'developer_count': developer_count,
        'hr_count': hr_count,
        'course_count': course_count,
        'cert_count': cert_count,
        'developers': developers,
        'all_hrs': all_hrs,
    })

#============================================LANDING PAGE===========================================================#

def home(request):
    dev_form = DeveloperRegistrationForm()
    hr_form = HRRegistrationForm()
    login_form = LoginForm()
    return render(request, 'main/landing_page.html', {
        'dev_form': dev_form,
        'hr_form': hr_form,
        'login_form': login_form,
        
    })

#============================================ DEVELOPER ============================================================#
def manage_user(request):
    developers = User.objects.filter(role='DEV')
    return render(request,"admin/manage_user.html", {'developers': developers,})


@login_required
def developer_dashboard(request):
    if request.user.role != 'DEV':
        return redirect('dashboard')  # Optional check

    enrolled_count = CourseEnrollment.objects.filter(developer=request.user).count()
    certificate_count = Certificate.objects.filter(developer=request.user).count()

    return render(request, 'dashboard/developer.html', {
        'enrolled_count': enrolled_count,
        'certificate_count': certificate_count,
    })


def register_developer(request):
    from django.contrib import messages  # optional: for success messages

    if request.method == 'POST':
        form = DeveloperRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Roles.DEV
            user.save()
            messages.success(request, "Registration successful! You can now login.")
            return redirect('home')  # Redirect to login page instead of home
        else:
            # More specific error messages
            if 'email' in form.errors:
                messages.error(request, "Email is already taken or invalid.")
                return redirect('home')
            elif 'password' in form.errors:
                messages.error(request, "Password requirements not met.")
                return redirect('home')
            else:
                messages.error(request, "Please correct the errors below.")
                return redirect('home')
    else:
        form = DeveloperRegistrationForm()

    return render(request, 'main/landing_page.html', {  # 👈 this changed from register.html
        'dev_form': form,
        'hr_form': HRRegistrationForm(),
    })


def assign_developers(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    developers = User.objects.filter(role='DEV')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('assigned_developers')
        selected_users = User.objects.filter(id__in=selected_ids)
        course.assigned_developers.set(selected_users)
        messages.success(request, 'Developers assigned successfully!')
        return redirect('course_list')

    return render(request, 'developer/assign_developer.html', {
        'course': course,
        'developers': developers
    })


@login_required
def developer_courses(request):
    if request.user.role != 'DEV':
        return Http404("Unauthorized")
    courses = Course.objects.all()
    return render(request, 'dashboard/developer_courses.html', {'courses': courses})

#============================================ HR ===================================================================#
def manage_hr(request):
    all_hrs = User.objects.filter(role='HR')  # or any custom logic
    return render(request,"admin/manage_hr.html", {'all_hrs': all_hrs})


@login_required(login_url='custom_login')
def hr_dashboard(request):
    from django.core.paginator import Paginator
    
    domain = request.GET.get('domain', '').strip()
    cert_level = request.GET.get('cert_level', '').strip()
    page_number = request.GET.get('page', 1)
    
    developers = User.objects.filter(role='DEV')
    if domain:
        developers = developers.filter(domain__icontains=domain)
    if cert_level:
        dev_ids_with_cert = Certificate.objects.filter(level=cert_level).values_list('developer_id', flat=True)
        developers = developers.filter(id__in=dev_ids_with_cert)
    
    # Get total count for display
    total_developers = developers.count()
    
    # Implement pagination - 10 records per page
    paginator = Paginator(developers, 10)
    page_obj = paginator.get_page(page_number)
    
    domain_choices = User.objects.values_list('domain', flat=True).distinct()
    level_choices = [c[0] for c in Certificate.LEVEL_CHOICES]
    
    # Create a separate paginator for the history section to ensure it also shows only 10 records per page
    history_paginator = Paginator(developers, 10)
    history_page_obj = history_paginator.get_page(page_number)
    
    context = {
        'developers': page_obj,  # Use paginated developers for the developers section
        'contact_history': history_page_obj,  # Use paginated developers for the history section
        'filter_domain': domain,
        'filter_cert_level': cert_level,
        'domain_choices': domain_choices,
        'level_choices': level_choices,
        'hr_user': request.user,  # Add the logged-in HR user
        'total_developers': total_developers,
        'page_obj': page_obj,  # Add page object for template
        'paginator': paginator,  # Add paginator for template
        'history_page_obj': history_page_obj,  # Add history page object for template
        'history_paginator': history_paginator,  # Add history paginator for template
    }
    return render(request, 'dashboard/hr.html', context)


def register_hr(request):
    if request.method == 'POST':
        form = HRRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            hr = form.save(commit=False)
            hr.role = 'HR'
            hr.is_verified = False
            hr.save()
            messages.warning(request, "Your account is under verification. Please wait for admin approval.")
            return redirect('home')  # Redirect to login page
        else:
            # More specific error messages
            if 'email' in form.errors:
                messages.error(request, "Email is already taken or invalid.")
                return redirect('home')  # Redirect to login page
            elif 'password' in form.errors:
                messages.error(request, "Password requirements not met.")
                return redirect('home')  # Redirect to login page
            else:
                messages.error(request, "Please correct the errors below.")
                return redirect('home')  # Redirect to login page
    else:
        form = HRRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



@require_POST
def toggle_hr_verification(request, hr_id):
    hr = get_object_or_404(User, id=hr_id, role='HR')
    hr.is_verified = not hr.is_verified
    hr.save()
    messages.success(request, f"{hr.name}'s verification status changed.")
    return redirect('manage_hr')

@login_required
def toggle_hr_status(request, hr_id):
    if request.method == 'POST':
        hr = get_object_or_404(User, id=hr_id, role='HR')
        hr.is_verified = not hr.is_verified
        hr.save()
    return redirect('manage_hr')

#============================================ LOGIN ================================================================#



def login_view(request):
    print("=" * 50)
    print(f"LOGIN VIEW CALLED - Method: {request.method}")
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        print(f"Form is valid: {form.is_valid()}")
        
        if form.is_valid():
            user = form.get_user()
            print(f"User found: {user.email}, Role: {user.role}")

            # If HR but not verified, block login
            if user.role == 'HR' and not user.is_verified:
                messages.error(request, "Your account is under review. Please wait for admin approval.")
                return redirect('home')

            # Login the user
            login(request, user)
            print(f"User logged in successfully, redirecting to: developer_dashboard")

            # ✅ Role-based redirect
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif user.role == 'HR':
                return redirect('hr_dashboard')
            elif user.role == 'DEV':
                return redirect('developer_dashboard')
            else:
                return redirect('home')  # fallback
        else:
            # Handle invalid credentials - render the same page with error
            print("Form is invalid - showing error message")
            print(f"Form errors: {form.errors}")
            messages.error(request, "Invalid username or password. Please try again.")
            # Render landing page with login modal open and the bound form errors
            ctx = {
                'dev_form': DeveloperRegistrationForm(),
                'hr_form': HRRegistrationForm(),
                'login_form': form,  # bound form with errors
                'open_login_modal': True,
            }
            return render(request, 'main/landing_page.html', ctx)
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


#============================================ PASSWORD RESET ================================================================#

from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


#============================================ PASSWORD RESET ================================================================#

def password_reset_landing(request):
    """
    Unified landing page for password reset. Handles both:
    - requesting a reset link (email form)
    - confirming reset (new password form) using uid/token query params
    """
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")

    # helper to include base forms required by landing page modal
    def base_ctx(extra=None):
        ctx = {
            'dev_form': DeveloperRegistrationForm(),
            'hr_form': HRRegistrationForm(),
            'login_form': LoginForm(),
        }
        if extra:
            ctx.update(extra)
        return ctx

    # If token in URL, validate it and render new password form
    token_valid = False
    user_from_token = None
    if uidb64 and token:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user_from_token = User.objects.get(pk=uid)
            token_valid = default_token_generator.check_token(user_from_token, token)
        except Exception:
            token_valid = False

    # State 2: Handle POST of new password with token (handle this BEFORE email POST)
    if request.method == "POST" and (request.POST.get("uid") and request.POST.get("token")):
        uidb64 = request.POST.get("uid")
        token = request.POST.get("token")
        pwd1 = request.POST.get("new_password1", "")
        pwd2 = request.POST.get("new_password2", "")

        # Re-validate token for POST
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user_from_token = User.objects.get(pk=uid)
            token_valid = default_token_generator.check_token(user_from_token, token)
        except Exception:
            token_valid = False

        errors = []
        if not token_valid:
            errors.append("The reset link is invalid or has expired.")
            return render(request, "main/landing_page.html", base_ctx({
                "open_login_modal": True,
                "show_reset_form": True,
                "uid": uidb64,
                "token": token,
                "errors": errors
            }))

        if len(pwd1) < 8:
            errors.append("Password must be at least 8 characters.")
        if pwd1 != pwd2:
            errors.append("Passwords do not match.")
        if errors:
            return render(request, "main/landing_page.html", base_ctx({
                "open_login_modal": True,
                "show_reset_form": True,
                "uid": uidb64,
                "token": token,
                "errors": errors
            }))

        user_from_token.set_password(pwd1)
        user_from_token.save()
        messages.success(request, "Your password has been reset successfully. Please log in with your new password.")
        return render(request, "main/landing_page.html", base_ctx({
            "open_login_modal": True,
            "reset_success": True
        }))

    # State 1: Email submit (no token in GET and not a reset POST)
    if request.method == "POST" and not (request.POST.get("uid") and request.POST.get("token")):
        email = request.POST.get("email", "").strip()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            try:
                # Build reset URL that will render on landing page modal
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_landing') + f"?uid={uid}&token={default_token_generator.make_token(user)}"
                )

                subject = "Password Reset Request"
                message = render_to_string("password_reset/email_reset_link.txt", {
                    "user": user,
                    "reset_link": reset_link,
                })
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log but do not reveal email validity
                print(f"Password reset email send error: {e}")
        # Always show success on landing page modal to avoid enumeration
        messages.success(request, "If an account exists for that email, a reset link has been sent.")
        debug_link = None
        try:
            from django.conf import settings as dj_settings
            if dj_settings.DEBUG and user:
                debug_link = reset_link
                messages.info(request, f"Dev reset link: {reset_link}")
        except Exception:
            pass
        return render(request, "main/landing_page.html", base_ctx({
            "open_login_modal": True,
            "show_forgot_form": True,
            "email_sent": True,
            "reset_debug_link": debug_link,
        }))

    # Default GET render: if accessing /password-reset/ without token, open Forgot view in modal
    if request.method == "GET" and not uidb64 and not token:
        return render(request, "main/landing_page.html", base_ctx({
            "open_login_modal": True,
            "show_forgot_form": True,
        }))

    return render(request, "main/landing_page.html", base_ctx({
        "open_login_modal": True if (uidb64 or token) else False,
        "show_reset_form": True if (uidb64 or token) else False,
        "token_invalid": (bool(uidb64) and bool(token) and not token_valid),
        "uid": uidb64,
        "token": token,
    }))

#============================================ DASHBOARD ============================================================#

@login_required
def dashboard(request):
    if request.user.role == User.Roles.ADMIN:
        template = 'dashboard/admin.html'
    elif request.user.role == User.Roles.HR:
        template = 'dashboard/hr.html'
    else:
        template = 'dashboard/developer.html'
    return render(request, template)

#============================================COURSES================================================================#

@login_required
def view_course_enrollments(request):
    enrollments = CourseEnrollment.objects.select_related('developer', 'course')
    return render(request, 'courses/view_enrollment.html', {'enrollments': enrollments})


@login_required
def enroll_courses(request):
    courses = Course.objects.all()
    enrolled_courses = CourseEnrollment.objects.filter(developer=request.user).values_list('course_id', flat=True)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        CourseEnrollment.objects.get_or_create(developer=request.user, course=course)
        messages.success(request, f"You have successfully enrolled in {course.title}.")
        return redirect('enroll_courses')

    return render(request, 'courses/enroll_courses.html', {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    })


@login_required
def enroll_course_action(request, course_id):
    user = request.user
    if user.role == 'DEV':
        course = Course.objects.get(id=course_id)
        CourseEnrollment.objects.get_or_create(developer=user, course=course)
    return redirect('enroll_courses')


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully.")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})


def edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})


def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course.delete()
    messages.success(request, "Course deleted.")
    return redirect('course_list')


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Example logic - you may have better tracking
    completed_levels = ['Basic']  # Replace with real logic
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'completed_levels': completed_levels,
    })

#============================================CERTIFICATIONS=========================================================#

@login_required
def add_certification(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('certification_list')  # redirect after successful add
    else:
        form = CertificationForm()
    return render(request, 'certificate/certification_form.html', {'form': form})


@login_required
def developer_certificates(request):
    if request.user.role != 'DEV':
        return Http404("Unauthorized")
    certificates = Certificate.objects.filter(developer=request.user)
    return render(request, 'dashboard/developer_certificates.html', {'certificates': certificates})

def generate_certificate(request, user_id, course_id, level):
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Course, id=course_id)

    # Check if certificate already exists for this level
    existing = Certificate.objects.filter(developer=user, course=course, level=level).first()
    if existing:
        return redirect('developer_dashboard')  # or show a message

    # Create certificate
    cert = Certificate.objects.create(
        developer=user,
        course=course,
        level=level,
        status='Issued'
    )
    return redirect('developer_dashboard')

@login_required
def download_certificate(request, cert_id):
    print(f"DEBUG: Download certificate called with cert_id: {cert_id}")
    certificate = get_object_or_404(Certificate, id=cert_id, developer=request.user)
    print(f"DEBUG: Certificate found: {certificate}")
    print(f"DEBUG: Certificate developer: {certificate.developer.name}")
    print(f"DEBUG: Certificate course: {certificate.course.title}")
    print(f"DEBUG: Certificate level: {certificate.level}")
    
    import os
    # Always generate the PDF if it doesn't exist
    pdf_filename = f"certificate_{certificate.developer.id}_{certificate.course.id}_{certificate.level}_{certificate.id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'certificates', pdf_filename)
    print(f"DEBUG: PDF path: {pdf_path}")
    print(f"DEBUG: PDF exists: {os.path.exists(pdf_path)}")
    
    if not os.path.exists(pdf_path):
        print("DEBUG: Generating PDF...")
        result = generate_certificate_pdf(certificate)
        print(f"DEBUG: PDF generation result: {result}")
        print(f"DEBUG: PDF exists after generation: {os.path.exists(pdf_path)}")
        if os.path.exists(pdf_path):
            print(f"DEBUG: PDF file size: {os.path.getsize(pdf_path)} bytes")
    
    if os.path.exists(pdf_path):
        print("DEBUG: Serving PDF file")
        with open(pdf_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response
    
    print("DEBUG: PDF not found, raising 404")
    raise Http404("Certificate PDF not found or could not be generated.")

@login_required
def test_pdf_generation(request):
    """Simple test function to debug PDF generation"""
    try:
        # Get the first certificate for testing
        certificate = Certificate.objects.first()
        if not certificate:
            return HttpResponse("No certificates found in database")
        
        print(f"TEST: Found certificate: {certificate}")
        print(f"TEST: Developer: {certificate.developer.name}")
        print(f"TEST: Course: {certificate.course.title}")
        
        # Test PDF generation directly
        result = generate_certificate_pdf(certificate)
        print(f"TEST: PDF generation result: {result}")
        
        import os
        pdf_filename = f"certificate_{certificate.developer.id}_{certificate.course.id}_{certificate.level}_{certificate.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'certificates', pdf_filename)
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            return HttpResponse(f"SUCCESS: PDF generated at {pdf_path}, size: {file_size} bytes")
        else:
            return HttpResponse(f"FAILED: PDF not found at {pdf_path}")
            
    except Exception as e:
        import traceback
        return HttpResponse(f"ERROR: {str(e)}\n\nTraceback:\n{traceback.format_exc()}")

@login_required
def view_certificate(request, cert_id):
    certificate = get_object_or_404(Certificate, id=cert_id, developer=request.user)
    context = {
        'developer': certificate.developer,
        'course': certificate.course,
        'level': certificate.level,
        'certificate': certificate,
        'today': timezone.now().strftime('%B %d, %Y')
    }
    return render(request, 'certificate/certificate_template.html', context)

#============================================ QUESTIONS ============================================================#

@login_required
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('question_list')  # Create this route if needed
    else:
        form = QuestionForm()
    return render(request, 'question/question_form.html', {'form': form})


@staff_member_required
def question_list(request):
    level_filter = request.GET.get('level', '')
    if level_filter:
        questions = Question.objects.filter(stage=level_filter)
    else:
        questions = Question.objects.all()
    return render(request, 'question/question_list.html', {'questions': questions, 'level_filter': level_filter})


def edit_question(request, q_id):
    question = get_object_or_404(Question, pk=q_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated.")
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)
    return render(request, 'question/question_form.html', {'form': form})


def delete_question(request, q_id):
    question = get_object_or_404(Question, pk=q_id)
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect('question_list')

#============================================TESTS==================================================================#

@login_required
def test_settings_view(request):
    # Only allow admin users to access this view
    if request.user.role != 'ADMIN':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')
    
    # Get or create test settings
    settings = TestSettings.get_settings()
    
    if request.method == 'POST':
        # Update settings
        try:
            pass_percentage = int(request.POST.get('pass_percentage', 50))
            time_limit = int(request.POST.get('time_limit', 30))
            
            # Validate inputs
            if pass_percentage < 1 or pass_percentage > 100:
                messages.error(request, "Pass percentage must be between 1 and 100.")
            elif time_limit < 1 or time_limit > 180:
                messages.error(request, "Time limit must be between 1 and 180 minutes.")
            else:
                # Save settings
                settings.pass_percentage = pass_percentage
                settings.time_limit = time_limit
                settings.save()
                messages.success(request, "Test settings updated successfully.")
        except ValueError:
            messages.error(request, "Please enter valid numbers for settings.")
    
    return render(request, 'test/test_settings.html', {'settings': settings})


@login_required
def attempt_test_view(request):
    # Show all courses the developer is enrolled in
    enrolled_courses = CourseEnrollment.objects.filter(developer=request.user)
    return render(request, 'test/attempt_test.html', {'courses': enrolled_courses})


@login_required
def select_level_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    levels = ['Basic', 'Intermediate', 'Advanced']
    return render(request, 'test/attempt_levels.html', {'course': course, 'levels': levels})


@login_required
def show_questions_view(request, course_id, level):
    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course, stage=level)
    
    # Get test settings for time limit
    test_settings = TestSettings.get_settings()

    if request.method == 'POST':
        total = questions.count()
        correct = 0
        answered_questions = 0
        question_results = []
        
        for question in questions:
            selected = request.POST.get(f"question_{question.id}")
            is_correct = False
            
            if selected:
                answered_questions += 1
                if selected.strip().upper() == question.correct_answer.strip().upper():
                    correct += 1
                    is_correct = True
            
            question_results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'selected': selected,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct
            })

        # Get test settings for pass percentage
        test_settings = TestSettings.get_settings()
        
        score = int((correct / total) * 100) if total > 0 else 0
        status = 'Passed' if score >= test_settings.pass_percentage else 'Failed'
        
        # Calculate additional metrics
        accuracy = int((correct / answered_questions) * 100) if answered_questions > 0 else 0
        unanswered = total - answered_questions

        # Create certification record
        certification = Certification.objects.create(
            user=request.user,
            course=course,
            level=level,
            score=score,
            status=status
        )

        # If test is passed, automatically create a certificate
        if status == 'Passed':
            # Check if certificate already exists for this level
            existing_certificate = Certificate.objects.filter(
                developer=request.user, 
                course=course, 
                level=level
            ).first()
            
            if not existing_certificate:
                # Create certificate
                certificate = Certificate.objects.create(
                    developer=request.user,
                    course=course,
                    level=level
                )
                
                # Generate the actual certificate file
                try:
                    success = generate_certificate_pdf(certificate)
                    if success:
                        messages.success(request, f"🏆 Outstanding achievement! You've earned your {level} level certificate for {course.title}!")
                    else:
                        messages.warning(request, f"Certificate created but file generation failed. Please contact support.")
                except Exception as e:
                    messages.warning(request, f"Certificate created but file generation failed. Please contact support.")
                    print(f"Certificate file generation error: {e}")
            else:
                # Certificate exists but might not have a file
                if not existing_certificate.certificate_file or existing_certificate.certificate_file == '':
                    try:
                        success = generate_certificate_pdf(existing_certificate)
                        if success:
                            messages.success(request, f"Certificate file generated for {course.title} - {level} level!")
                    except Exception as e:
                        print(f"Certificate file generation error for existing certificate: {e}")

        # Store detailed results in session for the result page
        request.session['test_results'] = {
            'total_questions': total,
            'correct_answers': correct,
            'answered_questions': answered_questions,
            'unanswered_questions': unanswered,
            'accuracy': accuracy,
            'score': score,
            'status': status,
            'question_results': question_results
        }

        messages.success(request, f"Test completed! You scored {score}%. Status: {status}")
        return redirect('test-result', course_id=course_id, level=level)

    return render(request, 'test/test_question.html', {
        'course': course,
        'questions': questions,
        'level': level,
        'time_limit': test_settings.time_limit
    })


@login_required
def test_result(request, course_id, level):
    cert = Certification.objects.filter(user=request.user, course_id=course_id, level=level).last()
    if not cert:
        messages.error(request, "No test result found for this course and level.")
        return redirect('attempt-test')
    
    # Get detailed results from session
    test_results = request.session.get('test_results', {})
    
    # Get user's test history for this course
    user_certifications = Certification.objects.filter(
        user=request.user, 
        course_id=course_id
    ).order_by('-issued_at')
    
    # Get user's certificates for the download button
    certificates = Certificate.objects.filter(developer=request.user)
    
    # Calculate performance trends
    if user_certifications.count() > 1:
        previous_scores = list(user_certifications.values_list('score', flat=True)[1:])
        avg_score = sum(previous_scores) / len(previous_scores)
        improvement = cert.score - avg_score
    else:
        avg_score = None
        improvement = None
    
    context = {
        'certification': cert,
        'test_results': test_results,
        'show_details': bool(test_results),  # Only show details if we have session data
        'user_certifications': user_certifications,
        'certificates': certificates,  # Add certificates to context
        'avg_score': avg_score,
        'improvement': improvement,
        'total_attempts': user_certifications.count()
    }
    
    # Clear session data after displaying
    if 'test_results' in request.session:
        del request.session['test_results']
    
    return render(request, 'test/test_result.html', context)


@login_required
def test_history(request):
    """View for displaying user's complete test history and analytics"""
    user_certifications = Certification.objects.filter(user=request.user).order_by('-issued_at')
    
    # Get user's certificates for the download buttons
    certificates = Certificate.objects.filter(developer=request.user)
    
    # Calculate overall statistics
    total_tests = user_certifications.count()
    passed_tests = user_certifications.filter(status='Passed').count()
    failed_tests = user_certifications.filter(status='Failed').count()

    # Calculate overall average score for all tests
    circumference = 2 * 3.14 * 50  # For r=50
    if total_tests > 0:
        avg_score = sum([c.score for c in user_certifications]) / total_tests
    else:
        avg_score = 0
    stroke_dasharray = circumference
    stroke_dashoffset = circumference - (avg_score / 100) * circumference
    
    # Get performance by course
    course_performance = {}
    for cert in user_certifications:
        course_name = cert.course.title
        if course_name not in course_performance:
            course_performance[course_name] = {
                'total_attempts': 0,
                'passed': 0,
                'failed': 0,
                'avg_score': 0,
                'scores': [],
                'pass_percent': 0,  # Add this field
            }
        course_performance[course_name]['total_attempts'] += 1
        course_performance[course_name]['scores'].append(cert.score)
        if cert.status == 'Passed':
            course_performance[course_name]['passed'] += 1
        else:
            course_performance[course_name]['failed'] += 1
    # Calculate average scores and pass percent for each course
    for course_name, data in course_performance.items():
        data['avg_score'] = sum(data['scores']) / len(data['scores'])
        if data['total_attempts'] > 0:
            data['pass_percent'] = round((data['passed'] / data['total_attempts']) * 100, 1)
        else:
            data['pass_percent'] = 0
    
    context = {
        'certifications': user_certifications,
        'certificates': certificates,  # Add certificates to context
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'pass_rate': round((passed_tests / total_tests * 100), 1) if total_tests > 0 else 0,
        'course_performance': course_performance,
        'stroke_dasharray': stroke_dasharray,
        'stroke_dashoffset': stroke_dashoffset,
        'avg_score': round(avg_score, 1),
    }
    
    return render(request, 'test/test_history.html', context)


def get_filtered_developers(request):
    """Helper to get filtered developers queryset based on request.GET."""
    domain = request.GET.get('domain', '').strip()
    cert_level = request.GET.get('cert_level', '').strip()
    developers = User.objects.filter(role='DEV')
    if domain:
        developers = developers.filter(domain__icontains=domain)
    if cert_level:
        dev_ids_with_cert = Certificate.objects.filter(level=cert_level).values_list('developer_id', flat=True)
        developers = developers.filter(id__in=dev_ids_with_cert)
    return developers

@login_required(login_url='login')
def export_developers_excel(request):
    developers = get_filtered_developers(request)
    data = []
    for dev in developers:
        certs = ', '.join([f"{c.course.title} ({c.level})" for c in dev.certificate_set.all()])
        data.append({
            'Name': dev.name,
            'Email': dev.email,
            'Skills': dev.skills,
            'Domain': dev.domain,
            'Certificates': certs,
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Developers')
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=developers.xlsx'
    return response

@login_required(login_url='login')
def export_developers_pdf(request):
    developers = get_filtered_developers(request)
    html = render_to_string('dashboard/developer_export_pdf.html', {'developers': developers})
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=developers.pdf'
    return response

@login_required(login_url='login')
def update_hr_profile(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '').strip()
        profile_photo = request.FILES.get('profile_photo')

        if name:
            user.name = name
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if address:
            user.address = address
        if password:
            user.password = make_password(password)
        if profile_photo:
            user.profile_photo = profile_photo
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('hr_dashboard')
    else:
        return redirect('hr_dashboard')


# ======================================= CERTIFICATE DOWNLOAD ==============================================================#

@login_required
def download_certificate_pdf(request, certification_id):
    """
    Download certificate as PDF using ReportLab
    """
    try:
        # Get the certification object
        certification = get_object_or_404(Certification, id=certification_id)
        
        # Check if user has permission to download this certificate
        if request.user.role == 'DEV' and certification.user != request.user:
            return HttpResponseForbidden("You can only download your own certificates.")
        
        # Only allow download for passed certifications
        if certification.status != 'Passed':
            messages.error(request, "Certificate can only be downloaded for passed certifications.")
            return redirect('developer_dashboard' if request.user.role == 'DEV' else 'admin_dashboard')
        
        # Generate the certificate PDF
        generator = CertificateGenerator(certification)
        pdf_buffer = generator.generate_certificate_pdf()
        filename = generator.get_filename()
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error generating certificate: {str(e)}")
        return redirect('developer_dashboard' if request.user.role == 'DEV' else 'admin_dashboard')


@login_required
def view_certificate_pdf(request, certification_id):
    """
    View certificate as PDF in browser (inline)
    """
    try:
        # Get the certification object
        certification = get_object_or_404(Certification, id=certification_id)
        
        # Check if user has permission to view this certificate
        if request.user.role == 'DEV' and certification.user != request.user:
            return HttpResponseForbidden("You can only view your own certificates.")
        
        # Only allow viewing for passed certifications
        if certification.status != 'Passed':
            messages.error(request, "Certificate can only be viewed for passed certifications.")
            return redirect('developer_dashboard' if request.user.role == 'DEV' else 'admin_dashboard')
        
        # Generate the certificate PDF
        generator = CertificateGenerator(certification)
        pdf_buffer = generator.generate_certificate_pdf()
        filename = generator.get_filename()
        
        # Create HTTP response with PDF for inline viewing
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error viewing certificate: {str(e)}")
        return redirect('developer_dashboard' if request.user.role == 'DEV' else 'admin_dashboard')


@login_required
def list_user_certificates(request):
    """
    List all certificates for the current user (developers only)
    """
    if request.user.role != 'DEV':
        return HttpResponseForbidden("Only developers can access this page.")
    
    # Get all passed certifications for the current user
    certifications = Certification.objects.filter(
        user=request.user, 
        status='Passed'
    ).select_related('course').order_by('-issued_at')
    
    return render(request, 'certificates/user_certificates.html', {
        'certifications': certifications
    })


