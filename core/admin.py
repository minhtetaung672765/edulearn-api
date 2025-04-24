from django.contrib import admin

# Register your models here.

from .models import User, Educator, Student

admin.site.register(User)
admin.site.register(Educator)
admin.site.register(Student)