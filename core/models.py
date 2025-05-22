from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'educator')  # Optional default

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('educator', 'Educator'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    profile_image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Educator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class CourseTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    # CATEGORY_CHOICES = [
    #     ('programming', 'Programming'),
    #     ('design', 'Design'),
    #     ('business', 'Business'),
    #     ('language', 'Language'),
        
    # ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    # created_by = models.ForeignKey('Educator', on_delete=models.CASCADE, related_name='courses')
    # allow null for created_by
    created_by = models.ForeignKey('Educator', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    # category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    category = models.CharField(max_length=100)
    tags = models.ManyToManyField(CourseTag, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    # course_image = models.URLField(null=True, blank=True)  # New field for image URL
    course_image = models.ImageField(upload_to='img_courses/', null=True, blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    lesson_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lesson_number']  # Optional: always fetch lessons in order

    # def __str__(self):
    #     return f"{self.title} ({self.course.title})"
    def __str__(self):
        return f"Lesson {self.lesson_number}: {self.title} ({self.course.title})"


class SubscribedCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # Prevent duplicate subscriptions

    def __str__(self):
        return f"{self.student.full_name} subscribed to {self.course.title}"

