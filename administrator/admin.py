from django.contrib import admin
# from .models import administrator

# Register your models here.



# admin.site.register(administrator)


from django.contrib import admin
from .models import Course, Question, EnrolledCourse

admin.site.register(Course)
admin.site.register(Question)
admin.site.register(EnrolledCourse)
