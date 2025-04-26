from django.shortcuts import render

from rest_framework import viewsets, permissions
from .models import Course, Lesson, CourseTag, SubscribedCourse
from .serializers import CourseSerializer, LessonSerializer, CourseTagSerializer, SubscribedCourseSerializer
from .permissions import IsEducatorOrReadOnly

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User, Educator, Student
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from rest_framework.decorators import api_view, permission_classes

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsEducatorOrReadOnly]

    # automatically set the created_by field to the current user's educator
    def perform_create(self, serializer):
        educator = self.request.user.educator
        serializer.save(created_by=educator)

    # ------+ manually added by mac - remove if it introduces inconsistencies
    # order lessons by lesson_number
        Course.objects.prefetch_related('lessons')
    # -------+

# class CourseViewSet(viewsets.ModelViewSet):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     # permission_classes = [IsEducatorOrReadOnly]
#     permission_classes = [AllowAny]  # ⚠️ TEMPORARY FOR TESTING ONLY


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsEducatorOrReadOnly]
    # permission_classes = [AllowAny]  # ⚠️ TEMPORARY FOR TESTING ONLY

class CourseTagViewSet(viewsets.ModelViewSet):
    queryset = CourseTag.objects.all()
    serializer_class = CourseTagSerializer


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    # full_name = serializers.CharField()
    # profile_image = serializers.URLField(required=False)
    full_name = serializers.CharField(write_only=True)
    profile_image = serializers.URLField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'role', 'full_name', 'profile_image')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role')
        full_name = validated_data.pop('full_name')
        profile_image = validated_data.pop('profile_image', None)

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )

        if role == 'educator':
            Educator.objects.create(user=user, full_name=full_name, profile_image=profile_image)
        elif role == 'student':
            Student.objects.create(user=user, full_name=full_name, profile_image=profile_image)

        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class SubscribedCourseViewSet(viewsets.ModelViewSet):
    queryset = SubscribedCourse.objects.all()
    serializer_class = SubscribedCourseSerializer
    permission_classes = [IsAuthenticated]

    # Subscribe to a course
    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'student'):
            raise PermissionDenied('Only students can subscribe to courses.')

        serializer.save(student=self.request.user.student)

    # A student only sees list of their own subscriptions, not others
    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return SubscribedCourse.objects.filter(student=self.request.user.student)
        return SubscribedCourse.objects.none()

# student can see his subscribed courses
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses(request):
    if not hasattr(request.user, 'student'):
        return Response({'detail': 'Only students can access this.'}, status=status.HTTP_403_FORBIDDEN)

    subscriptions = SubscribedCourse.objects.filter(student=request.user.student)
    courses = [subscription.course for subscription in subscriptions]

    from .serializers import CourseSerializer
    serializer = CourseSerializer(courses, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

# subscribe to a course, but with another endpoint - with parameter
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_course(request, course_id):
    if not hasattr(request.user, 'student'):
        return Response({'detail': 'Only students can subscribe to courses.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if already subscribed
    if SubscribedCourse.objects.filter(student=request.user.student, course=course).exists():
        return Response({'detail': 'Already subscribed.'}, status=status.HTTP_400_BAD_REQUEST)

    SubscribedCourse.objects.create(student=request.user.student, course=course)

    return Response({'detail': 'Subscribed successfully.'}, status=status.HTTP_201_CREATED)

# get lessons of a course
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_course_lessons(request, course_id):
    if not hasattr(request.user, 'student'):
        return Response({'detail': 'Only students can access lessons.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the student is subscribed to the course
    if not SubscribedCourse.objects.filter(student=request.user.student, course=course).exists():
        return Response({'detail': 'You are not subscribed to this course.'}, status=status.HTTP_403_FORBIDDEN)

    # Get lessons of the course
    lessons = course.lessons.all().order_by('lesson_number')  # Order lessons
    from .serializers import LessonSerializer
    serializer = LessonSerializer(lessons, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

# --------------------- AI: Personalized Course Recommendation -------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_courses(request):
    if not hasattr(request.user, 'student'):
        return Response({'detail': 'Only students can access recommendations.'}, status=status.HTTP_403_FORBIDDEN)

    # Get student's subscribed courses
    subscriptions = SubscribedCourse.objects.filter(student=request.user.student)
    subscribed_courses = [sub.course for sub in subscriptions]

    if not subscribed_courses:
        return Response({'detail': 'No subscriptions found. Subscribe to courses first!'}, status=status.HTTP_404_NOT_FOUND)

    subscribed_course_ids = [course.id for course in subscribed_courses]
    recommended_courses_set = set()

    for course in subscribed_courses:
        # Find other courses with the same category
        similar_courses = Course.objects.filter(category=course.category).exclude(id__in=subscribed_course_ids)

        # Filter by tag similarity
        course_tags = set(tag.name for tag in course.tags.all())
        course_scores = []

        for candidate in similar_courses:
            candidate_tags = set(tag.name for tag in candidate.tags.all())
            common_tags = course_tags.intersection(candidate_tags)
            score = len(common_tags)
            course_scores.append((candidate, score))

        # Sort by number of common tags (higher = better)
        course_scores.sort(key=lambda x: x[1], reverse=True)

        # Take top 3-4 best matches (you can tweak number)
        top_matches = [course_score[0] for course_score in course_scores[:4]]

        recommended_courses_set.update(top_matches)

    recommended_courses_list = list(recommended_courses_set)

    # If not enough, add same-category random courses
    if len(recommended_courses_list) < 5:
        additional_courses = Course.objects.exclude(id__in=subscribed_course_ids + [c.id for c in recommended_courses_list]).order_by('?')[:(5 - len(recommended_courses_list))]
        recommended_courses_list += list(additional_courses)

    # Limit to 5 or more if you want
    recommended_courses_list = recommended_courses_list[:5]

    from .serializers import CourseSerializer
    serializer = CourseSerializer(recommended_courses_list, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

# ----------------------------------------------------------------------------