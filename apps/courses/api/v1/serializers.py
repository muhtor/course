from rest_framework import serializers
from ....quiz.api.v1.serializers import MyQuizListSerializer, QuizShortInfoSerializer
from ...models import *


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'parent_category', 'title', 'slug', 'image_url')


class CategorySerializer(serializers.ModelSerializer):
    children = SubCategorySerializer(many=True, required=False)

    class Meta:
        model = Category
        fields = ('id', 'title', 'slug', 'image_url', 'children',)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'name')


class LessonListSerializer(serializers.ModelSerializer):
    process_status = serializers.SerializerMethodField('get_lesson_process_status')
    is_blocked = serializers.SerializerMethodField('get_is_blocked')

    class Meta:
        model = Lesson
        fields = ('id', 'name', 'process_status', 'is_blocked')

    def get_lesson_process_status(self, lesson):
        try:
            return lesson.get_process_status(self.context['request'].user)
        except:
            return Status.NEW

    def get_is_blocked(self, lesson):
        return lesson.is_blocked(self.context['request'].user)


class LessonDetailSerializer(LessonListSerializer):
    text = serializers.CharField(source='description', read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'name', 'text', 'process_status', 'is_blocked')


class TopicListSerializer(serializers.ModelSerializer):
    topic_number = serializers.CharField(source='id', read_only=True)
    quiz = QuizShortInfoSerializer()
    lessons = LessonListSerializer(many=True)

    class Meta:
        model = Topic
        fields = ('id', 'name', 'topic_number', 'lessons', 'quiz')


class TopicDetailSerializer(TopicListSerializer):
    lessons = LessonDetailSerializer(many=True)
    quiz = MyQuizListSerializer()


class CourseListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', read_only=True)
    status = serializers.SerializerMethodField()
    finished_lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'category_id', 'category', 'description', 'id',
            'image_url', 'name', 'old_price', 'price', 'status',
            'lessons_count', 'finished_lessons_count'
        )

    def get_status(self, course):
        return course.get_status(self.context['request'].user)

    def get_finished_lessons_count(self, course):
        try:
            return UserLesson.objects.filter(
                user=self.context['request'].user,
                lesson__topic__course=course,
                status=Status.FINISHED
            ).count()
        except:
            return 0


class CourseShortSerializer(serializers.ModelSerializer):
    """Short info about course"""

    class Meta:
        model = Course
        fields = ('id', 'name', 'price')


class UserCourseListSerializer(serializers.ModelSerializer):
    course = CourseListSerializer()

    class Meta:
        model = UserCourse
        fields = ('course',)

    def get_status(self, course):
        return course.get_status(self.context['request'].user)

    def to_representation(self, instance):
        data = super(UserCourseListSerializer, self).to_representation(instance)
        course = data['course']
        course['status'] = instance.status
        return course


class CourseDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', read_only=True)
    last_update = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d', read_only=True)
    material = TopicDetailSerializer(source='topic_courses', many=True)
    status = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()
    final_quiz = MyQuizListSerializer()

    class Meta:
        model = Course
        fields = (
            'category_id',
            'category',
            'description',
            'id',
            'image_url',
            'name',
            'author',
            'old_price',
            'price',
            'status',
            'paid',
            'viewed_count',
            'person_count',
            'lessons_count',
            'last_update',
            'permission',
            'certificate',
            'is_active',
            'material',
            'final_quiz'
        )

    def get_status(self, course):
        return course.get_status(self.context['request'].user)

    def get_paid(self, course):
        try:
            return self.context['request'].user.profile.is_course_paid(course)
        except:
            return False


class UserLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLesson
        fields = ('id', 'user', 'lesson', 'status')
        read_only_fields = ['user', 'lesson']


class CertificatedCourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', allow_null=True)
    status = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    real_price = serializers.FloatField(source='sub_courses_price')
    sub_courses = CourseShortSerializer(many=True)
    sub_courses_count = serializers.ReadOnlyField()

    class Meta:
        model = CertificatedCourse
        fields = (
            'id', 'name', 'description', 'image_url', 'category', 'price',
            'real_price', 'old_price', 'status', 'lessons_count', 'quiz',
            'created_at', 'updated_at', 'sub_courses_count', 'sub_courses'
        )

    def get_status(self, certificated_course):
        return certificated_course.get_status(self.context['request'].user)

    def get_price(self, certificated_course):
        user = self.context['request'].user
        if user.is_authenticated:
            return certificated_course.get_price_for_user(user)
        return certificated_course.price


class CertificatedCourseSubCourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', read_only=True)
    status = serializers.SerializerMethodField()
    finished_lessons_count = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'category_id', 'category', 'description', 'id',
            'image_url', 'name', 'author', 'old_price', 'price', 'status',
            'lessons_count', 'finished_lessons_count', 'paid'
        )

    def get_status(self, course):
        return course.get_status(self.context['request'].user)

    def get_paid(self, course):
        try:
            return self.context['request'].user.profile.is_course_paid(course)
        except:
            return False

    def get_finished_lessons_count(self, course):
        try:
            return UserLesson.objects.filter(
                user=self.context['request'].user,
                lesson__topic__course=course,
                status=Status.FINISHED
            ).count()
        except:
            return 0
