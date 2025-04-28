from core.models import Course, CourseTag
import random

# bash to run:
# run > python manage.py shell
# exit shell > exit()

# Optional: Clear previous courses and tags (only if needed)
# Course.objects.all().delete()
# CourseTag.objects.all().delete()

# Define Tags
tags_data = [
    # Language
    'English', 'French', 'Spanish', 'Grammar', 'Speaking', 'Writing',

    # Business
    'Marketing', 'Analytics', 'Finance', 'Leadership', 'Strategy', 'Management',

    # Engineering
    'Electrical', 'Mechanical', 'Civil', 'Software', 'Robotics', 'Automation',
]

# Create Tags
tags = {}
for tag_name in tags_data:
    tag_obj = CourseTag.objects.create(name=tag_name)
    tags[tag_name] = tag_obj

# Define Courses
course_data = [
    # Language Courses
    ('English Grammar Basics', 'language', ['English', 'Grammar']),
    ('French for Beginners', 'language', ['French', 'Speaking']),
    ('Spanish Conversation Skills', 'language', ['Spanish', 'Speaking']),
    ('Business English Communication', 'language', ['English', 'Writing']),
    ('German Intermediate Course', 'language', ['Grammar', 'Speaking']),
    ('Mandarin Essentials', 'language', ['Speaking', 'Writing']),

    # Business Courses
    ('Marketing Principles', 'business', ['Marketing', 'Strategy']),
    ('Business Analytics Fundamentals', 'business', ['Analytics', 'Finance']),
    ('Financial Accounting Basics', 'business', ['Finance', 'Management']),
    ('Entrepreneurship Essentials', 'business', ['Leadership', 'Strategy']),
    ('Business Strategy Development', 'business', ['Strategy', 'Leadership']),
    ('Project Management 101', 'business', ['Management', 'Leadership']),

    # Engineering Courses
    ('Electrical Circuits Introduction', 'engineering', ['Electrical']),
    ('Mechanical Design Concepts', 'engineering', ['Mechanical']),
    ('Civil Engineering Basics', 'engineering', ['Civil']),
    ('Software Engineering Practices', 'engineering', ['Software']),
    ('Thermodynamics and Heat Transfer', 'engineering', ['Mechanical']),
    ('Robotics and Automation Fundamentals', 'engineering', ['Robotics', 'Automation']),
]

# Create Courses
for title, category, tag_list in course_data:
    course = Course.objects.create(
        title=title,
        description=f"This course covers {title.lower()} concepts in depth.",
        category=category
    )
    for tag_name in tag_list:
        course.tags.add(tags[tag_name])

print("✅ Seeding Complete: 18 courses successfully created!")
