
from django.urls import path
from . import views

urlpatterns = [

#======================================= LANDING PAGE ==============================================================#

    path('', views.home, name='home'),

#======================================= DEVELOPER  ================================================================#

    path('manage-user/', views.manage_user, name='manage_user'),
    path('developer-dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('register/developer/', views.register_developer, name='register_developer'),
    path('admin/courses/assign/<int:course_id>/', views.assign_developers, name='assign_developers'),

#======================================= ADMIN =====================================================================#

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/toggle_hr/<int:hr_id>/', views.toggle_hr_verification, name='toggle_hr_verification'),
    path('toggle-hr-status/<int:hr_id>/', views.toggle_hr_status, name='toggle_hr_status'),

#======================================= LOGIN  ====================================================================#

    path('login/', views.login_view, name='custom_login'),
    path('password-reset/', views.password_reset_landing, name='password_reset_landing'),

#======================================= HR ========================================================================#

    path('manage-hr/', views.manage_hr, name='manage_hr'),
    path('register/hr/', views.register_hr, name='register_hr'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr-dashboard/export/pdf/', views.export_developers_pdf, name='export_developers_pdf'),
    path('hr-dashboard/export/excel/', views.export_developers_excel, name='export_developers_excel'),
    path('update-hr/', views.update_hr_profile, name='update_hr_profile'),

#======================================= TEST ======================================================================#

    path('test_result/<int:course_id>/<str:level>', views.test_result, name='test-result'),
    path('test_history/', views.test_history, name='test-history'),
    path('admin/test-settings/', views.test_settings_view, name='test_settings'),

#======================================= COURSES ===================================================================#

    path('courses/', views.developer_courses, name='developer_courses'),
    path('admin/courses/', views.course_list, name='course_list'),
    path('admin/courses/add/', views.add_course, name='add_course'),
    path('admin/courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('admin/courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),  
    path('developer/enroll-courses/', views.enroll_courses, name='enroll_courses'),
    path('developer/enroll/<int:course_id>/', views.enroll_course_action, name='enroll_course_action'),
    path('enroll-courses/', views.enroll_courses, name='enroll_courses'),
    path('admin/enrollments/', views.view_course_enrollments, name='view_course_enrollments'),

#======================================= DASHBOARD==================================================================#

    path('dashboard/', views.dashboard, name='dashboard'),

#======================================= CERTIFICATE ===============================================================#

    path('certificates/', views.developer_certificates, name='developer_certificates'),
    path('certificates/download/<int:cert_id>/', views.download_certificate, name='download_certificate'),
    path('certificates/view/<int:cert_id>/', views.view_certificate, name='view_certificate'),
    path('test-pdf/', views.test_pdf_generation, name='test_pdf_generation'),
    path('admin/certifications/add/', views.add_certification, name='add_certification'),
    path('certificate/generate/<int:user_id>/<int:course_id>/<str:level>/', views.generate_certificate, name='generate_certificate'),

#======================================= QUESTION ==================================================================#

    path('admin/questions/add/', views.add_question, name='add_question'),
    path('admin/question-list/', views.question_list, name='question_list'),
    path('admin/question/edit/<int:q_id>/', views.edit_question, name='edit_question'),
    path('admin/question/delete/<int:q_id>/', views.delete_question, name='delete_question'),
    path('attempt-test/', views.attempt_test_view, name='attempt-test'),
    path('select-level/<int:course_id>/', views.select_level_view, name='select-level'),
    path('test/<int:course_id>/<str:level>/', views.show_questions_view, name='test-questions'),

]

     
  

