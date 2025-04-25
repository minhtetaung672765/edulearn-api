from django.contrib import admin

# Register your models here.

from .models import User, Educator, Student, Course, Lesson, CourseTag

admin.site.register(User)
admin.site.register(Educator)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(CourseTag)