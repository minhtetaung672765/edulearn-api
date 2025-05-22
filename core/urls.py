
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonViewSet,
    CourseTagViewSet, 
    RegisterView, 
    SubscribedCourseViewSet, 
    my_courses, 
    subscribe_course, 
    my_course_lessons,
    recommended_courses,
    user_profile,
    generate_questions
    )
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'tags', CourseTagViewSet)
router.register(r'subscribed-courses', SubscribedCourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/profile/', user_profile, name='user-profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('my-courses/', my_courses, name='my-courses'),
    path('subscribe/<int:course_id>/', subscribe_course, name='subscribe-course'),
    path('my-courses/<int:course_id>/lessons/', my_course_lessons, name='my-course-lessons'),
    # 
    path('recommended-courses/', recommended_courses, name='recommended-courses'),
    path("generate-questions/", generate_questions, name="generate-questions"),
]

