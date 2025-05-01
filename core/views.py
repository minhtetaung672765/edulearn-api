from django.shortcuts import render

from rest_framework import viewsets, permissions
from .models import Course, Lesson, CourseTag, SubscribedCourse, Student
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

from decouple import config
import google.generativeai as genai
import json
import re

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    full_name = ''

    try:
        if user.role == 'student':
            student = Student.objects.get(user=user)
            full_name = student.full_name
        elif user.role == 'educator':
            full_name = "Educator"  # Later you can adjust if educator has profile info
    except Student.DoesNotExist:
        full_name = user.email  # fallback if not found

    return Response({
        'id': user.id,
        'email': user.email,
        'name': full_name,
        'role': user.role,
    })

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

# --------------------- AI: Questions and MCQs Generation -------------------------------

# Load API key from env
genai.configure(api_key=config("GEMINI_API_KEY"))

@api_view(["POST"])
def generate_questions(request):
    lesson_content = request.data.get("lesson_content")

    if not lesson_content:
        return Response({"error": "Lesson content is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            "Generate 3 open-ended answer questions with answers (2-4 sentences) and 3 multiple choice questions with 4 options each and the correct option, "
            "based on the following lesson content:\n\n"
            f"{lesson_content}\n\n"
            "Return the response in JSON format like:\n"
            "{\n"
            "  \"questions\": [\n"
            "    { \"question\": \"Q1...\", \"answer\": \"...\" },\n"
            "    ...\n"
            "  ],\n"
            "  \"mcqs\": [\n"
            "    {\n"
            "      \"question\": \"What is...\",\n"
            "      \"options\": [\"A\", \"B\", \"C\", \"D\"],\n"
            "      \"answer\": \"B\"\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}"
        )

        response = model.generate_content(prompt)
        raw_text = response.text

        # Extract JSON using regex if it's wrapped in code block
        json_match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
        json_data = json_match.group(1) if json_match else raw_text

        parsed = json.loads(json_data)

        return Response(parsed)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ----------------------------------------------------------------------------