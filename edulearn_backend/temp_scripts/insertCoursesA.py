from core.models import Course, CourseTag
import random

# Clear previous data if needed
# Course.objects.all().delete()
# CourseTag.objects.all().delete()

# Tags
tag_names = [
    'Python', 'Backend', 'Frontend', 'DSA', 'Problem Solving', 
    'Machine Learning', 'SQL', 'MySQL', 'Cloud', 'DevOps', 
    'React', 'Django', 'Java', 'OOP', 'Cybersecurity', 
    'Mobile App', 'Flutter', 'Dart', 'AI', 'Networking'
]

tags = []
for name in tag_names:
    tag = CourseTag.objects.create(name=name)
    tags.append(tag)

# Courses
course_data = [
    ('Learn Python Programming', 'programming', ['Python', 'Backend']),
    ('Data Structures and Algorithms', 'programming', ['DSA', 'Problem Solving']),
    ('Introduction to Machine Learning', 'ai', ['Machine Learning', 'Python']),
    ('Web Development with React', 'web', ['React', 'Frontend']),
    ('Django for Beginners', 'web', ['Django', 'Backend']),
    ('Database Fundamentals', 'database', ['SQL', 'MySQL']),
    ('DevOps Essentials', 'it', ['DevOps', 'Cloud']),
    ('Advanced Java Programming', 'programming', ['Java', 'OOP']),
    ('Cybersecurity Basics', 'security', ['Cybersecurity', 'Hacking']),
    ('Mobile App Development', 'mobile', ['Flutter', 'Dart']),
    ('AI for Everyone', 'ai', ['AI', 'Python']),
    ('Networking Basics', 'it', ['Networking', 'Security']),
    ('Cloud Computing Fundamentals', 'it', ['Cloud']),
    ('Introduction to SQL', 'database', ['SQL']),
    ('Advanced React Techniques', 'web', ['React', 'Frontend']),
    ('Full Stack Development', 'web', ['Django', 'React']),
    ('Ethical Hacking 101', 'security', ['Cybersecurity', 'Hacking']),
    ('Natural Language Processing', 'ai', ['AI', 'Machine Learning']),
    ('Software Testing Fundamentals', 'programming', ['Testing', 'Automation']),
    ('Linux System Administration', 'it', ['Linux', 'DevOps']),
    ('Intro to Data Science', 'ai', ['Data Science', 'Python']),
    ('Web Security Fundamentals', 'security', ['Web Security', 'Cybersecurity']),
    ('JavaScript for Beginners', 'programming', ['JavaScript', 'Frontend']),
    ('Building APIs with Django Rest Framework', 'web', ['Django', 'Backend']),
]

# Create courses
for title, category, tag_list in course_data:
    course = Course.objects.create(
        title=title,
        description=f"This course covers {title.lower()} with practical examples.",
        category=category
    )
    for tag_name in tag_list:
        tag_obj = CourseTag.objects.get(name=tag_name)
        course.tags.add(tag_obj)

print("✅ Seeding Complete: 20+ courses created successfully!")
