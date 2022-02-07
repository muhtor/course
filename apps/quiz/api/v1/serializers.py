from rest_framework import serializers

from ....courses.models import CourseCertificate
from ...models import (
    Quiz,
    QuizTaker,
    Question,
    Answer,
    UsersAnswer
)


class QuizListSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(source='get_questions_count')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'topic', 'questions_count', 'duration', 'required_score_to_pass', 'slug',
                  'date_created']
        read_only_fields = ['questions_count']


class QuizShortInfoSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ('id', 'slug', 'title', 'completed')

    def get_completed(self, obj):
        return obj.is_completed(self.context['request'].user)


class AnswerSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'title', 'status']

    def get_status(self, answer):
        return UsersAnswer.objects.filter(
            quiz_taker__user=self.context['request'].user,
            answers__in=[answer]
        ).exists()


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    technique = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = '__all__'

    def get_technique(self, question):
        return question.get_technique_name(question.technique)


class UserQuestionSerializer(QuestionSerializer):
    status = serializers.SerializerMethodField()
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'status', 'technique', 'answers')

    def get_status(self, question):
        """Is the question completed by user"""
        return UsersAnswer.objects.filter(
            quiz_taker__user=self.context['request'].user,
            question=question,
            answers__isnull=False
        ).exists()


class UsersAnswerSerializer(serializers.ModelSerializer):
    answers = serializers.CharField(source='answers_string')

    class Meta:
        model = UsersAnswer
        fields = '__all__'


class UncompletedQuizListSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField(read_only=True)
    topic = serializers.CharField(source='topic.name', read_only=True)
    questions_count = serializers.IntegerField(source='get_questions_count')
    chances = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'time', 'topic', 'questions_count', 'chances')

    def get_time(self, quiz):
        try:
            return quiz.takers.filter(user=self.context['request'].user, completed=False).last().time_left
        except:
            raise serializers.ValidationError('Quiz has not been started or has already been completed')

    def get_chances(self, quiz):
        return {
            'total_chances': quiz.chances,
            'your_chances': quiz.takers.filter(user=self.context['request'].user, completed=False).last().chances_left
        }


class MyQuizListSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'topic', 'questions_count', 'duration', 'required_score_to_pass', 'slug',
                  'completed', 'progress', 'questions_count', 'score', 'is_blocked']
        read_only_fields = ['completed', 'progress', 'questions_count', 'score']

    def get_completed(self, obj):
        return obj.is_completed(self.context['request'].user)

    def get_progress(self, obj):
        try:
            quiztaker = QuizTaker.objects.get(user=self.context['request'].user, quiz=obj)
            if not quiztaker.completed:
                questions_answered = UsersAnswer.objects.filter(quiz_taker=quiztaker, answer__isnull=False).count()
                total_questions = obj.questions.all().count()
                return int(questions_answered / total_questions)
            return None
        except:
            return None

    def get_questions_count(self, obj):
        return obj.questions.all().count()

    def get_score(self, obj):
        try:
            quiztaker = QuizTaker.objects.get(user=self.context['request'].user, quiz=obj)
            if quiztaker.completed:
                return quiztaker.score
            return None
        except:
            return None

    def get_is_blocked(self, quiz):
        return quiz.is_blocked_for_user(self.context['request'].user)


class QuizTakerSerializer(serializers.ModelSerializer):
    answers = UsersAnswerSerializer(many=True)

    class Meta:
        model = QuizTaker
        fields = '__all__'


class QuizDetailSerializer(serializers.ModelSerializer):
    takers = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = '__all__'

    def get_takers(self, obj):
        try:
            quiz_taker = QuizTaker.objects.get(user=self.context['request'].user, quiz=obj)
            serializer = QuizTakerSerializer(quiz_taker)
            return serializer.data
        except QuizTaker.DoesNotExist:
            return None


class QuizResultSerializer(serializers.ModelSerializer):
    takers = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = '__all__'

    def get_takers(self, obj):
        try:
            quiztaker = QuizTaker.objects.get(user=self.context['request'].user, quiz=obj)
            serializer = QuizTakerSerializer(quiztaker)
            return serializer.data
        except QuizTaker.DoesNotExist:
            return None


class CourseCertificateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='certificated_object.name', read_only=True)
    finished_date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = CourseCertificate
        fields = ('id', 'name', 'pdf', 'finished_date')
