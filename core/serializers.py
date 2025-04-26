from rest_framework import serializers
from .models import Course, Lesson, CourseTag, SubscribedCourse

class CourseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTag
        fields = ['id', 'name']

class LessonSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'lesson_number', 'course', 'created_at']

# class CourseSerializer(serializers.ModelSerializer):
#     lessons = LessonSerializer(many=True, read_only=True)
#     tags = CourseTagSerializer(many=True)

#     class Meta:
#         model = Course
#         fields = ['id', 'title', 'description', 'category', 'tags', 'lessons', 'created_by', 'created_at']
#         read_only_fields = ['created_by']

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CourseTag.objects.all()
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'category', 'tags', 'lessons', 'created_by', 'created_at']
        read_only_fields = ['created_by']


class SubscribedCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribedCourse
        fields = ['id', 'student', 'course', 'subscribed_at']
        read_only_fields = ['student', 'subscribed_at']

