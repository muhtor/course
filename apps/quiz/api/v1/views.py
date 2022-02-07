from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response

from .permissions import IsAvailableForQuiz, IsQuizTakerAvailable
from ...services import get_certificate
from ...utils.answers import get_user_correct_answers_count
from ....core.utils.apiviews import PaginationListAPIView
from ...models import (
    Quiz,
    Question,
    Answer,
    QuizTaker,
    UsersAnswer,
)
from .serializers import (
    MyQuizListSerializer,
    QuizDetailSerializer,
    QuizListSerializer,
    QuizResultSerializer,
    UsersAnswerSerializer,
    UncompletedQuizListSerializer,
    UserQuestionSerializer,
    CourseCertificateSerializer
)
from ....profiles.models import Notification


class AllQuizListView(generics.ListAPIView):
    # http://127.0.0.1:2000/api/quizzes/v1/all-quizzes/?q=OOP
    serializer_class = QuizListSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self, *args, **kwargs):
        queryset = Quiz.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(topic__name__icontains=query)).distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            response = {'success': True, 'code': 600, 'result': serializer.data}
            return Response(response)
        else:
            response = {'success': False, 'code': 604, 'result': []}
            return Response(response)


class UserCompletedQuizListView(generics.ListAPIView):
    # http://127.0.0.1:2000/api/quizzes/v1/my-quizzes/
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = MyQuizListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = Quiz.objects.filter(takers__user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(topic__name__icontains=query)).distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            response = {'success': True, 'code': 600, 'result': serializer.data}
            return Response(response)
        else:
            response = {'success': False, 'code': 604, 'result': []}
            return Response(response)


class UserUnCompletedQuizListView(generics.ListAPIView):
    # http://127.0.0.1:2000/api/quizzes/v1/quizzes/
    serializer_class = UncompletedQuizListSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self, *args, **kwargs):
        queryset = Quiz.objects.filter(takers__user=self.request.user, takers__completed=False)
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(topic__name__icontains=query)).distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            response = {'success': True, 'code': 600, 'result': serializer.data}
            return Response(response)
        else:
            response = {'success': False, 'code': 604, 'result': []}
            return Response(response)


class UserUncompletedQuizDetailView(generics.RetrieveAPIView):
    """Uncompleted quiz main info"""
    serializer_class = UncompletedQuizListSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self, *args, **kwargs):
        queryset = Quiz.objects.filter(takers__user=self.request.user, takers__completed=False)
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(topic__name__icontains=query)).distinct()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]
        try:
            quiz = Quiz.objects.get(slug=slug)
        except Quiz.DoesNotExist as e:
            return Response({'success': False, 'code': 606, 'error': e.args})

        quiz_serializer = self.get_serializer(quiz)
        return Response({'success': True, 'code': 605, 'quiz': quiz_serializer.data})


class UserUncompletedQuizDetailQuestionsView(PaginationListAPIView):
    """All questions of the user uncompleted quiz"""
    serializer_class = UserQuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        return get_object_or_404(Quiz, slug=self.kwargs["slug"]).questions.all()


class QuizDetailView(generics.RetrieveAPIView):
    # http://127.0.0.1:2000/api/quizzes/v1/quizzes/
    queryset = Quiz.objects.all()
    lookup_field = 'slug'
    serializer_class = QuizDetailSerializer
    permission_classes = (permissions.IsAuthenticated, IsAvailableForQuiz)

    def get(self, *args, **kwargs):
        """User Question larga bergan javoblari..."""
        quiz = self.get_object()
        last_question = None
        obj, created = QuizTaker.objects.get_or_create(user=self.request.user, quiz=quiz)
        if created:
            for question in Question.objects.filter(quiz=quiz):
                UsersAnswer.objects.create(quiz_taker=obj, question=question)
        else:
            last_question = UsersAnswer.objects.filter(quiz_taker=obj, answers__isnull=False)
            if last_question.count() > 0:
                last_question = last_question.last().question.id
            else:
                last_question = None

        return Response(
            {
                'status': True,
                'code': 900,
                'quiz': self.get_serializer(quiz, context={'request': self.request}).data,
                'last_question_id': last_question
             }
        )


class SaveUsersAnswerView(generics.UpdateAPIView):
    serializer_class = UsersAnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsAvailableForQuiz, IsQuizTakerAvailable)

    def patch(self, request, *args, **kwargs):
        question = get_object_or_404(Question, id=request.GET.get('question', ''))
        self.check_object_permissions(self.request, question.quiz)
        quiztaker = request.user.profile.get_last_quiztaker(quiz=question.quiz)

        user_answer = get_object_or_404(UsersAnswer, quiz_taker=quiztaker, question=question)
        user_answer.clear()

        answer_id_string = request.GET.get('answers', '')
        try:
            answer_ids = answer_id_string.split(',')
        except ValueError:
            answer_ids = [int(answer_id_string)]

        for answer_id in answer_ids:
            user_answer.answers.add(get_object_or_404(Answer, id=answer_id))
        user_answer.save()

        return Response({'status': True, 'code': 900, 'message': 'Answered to question of the quiz'})


class SubmitQuizView(generics.GenericAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = (permissions.IsAuthenticated, IsAvailableForQuiz, IsQuizTakerAvailable)

    def post(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, quiz)

        try:
            quiztaker = QuizTaker.objects.filter(user=request.user, quiz=quiz).last()
        except:
            return Response({'success': False, 'code': 901, 'error': 'Quiz was not started'})

        response = {'status': True, 'code': 901}

        correct_answers = get_user_correct_answers_count(quiztaker)
        quiztaker.score = int((correct_answers / quiztaker.quiz.questions.count()) * 100)

        if not quiztaker.completed and quiztaker.score >= quiz.required_score_to_pass:
            quiztaker.completed = True
            quiztaker.save()
            Notification.objects.create(
                profile=request.user.profile,
                title=f'Tabriklaymiz!!! Siz muvaffaqiyatli {quiz.course_object.name} kursini tugatdingiz'
            )

            certificate = get_certificate(quiz=quiz, user=request.user, quiztaker=quiztaker,
                                          domain='aristotle.uz')
            if certificate:
                Notification.objects.create(
                    profile=request.user.profile,
                    title=f'{quiz.course_object.name} kursini muvaffaqiyatli tugatganingiz'
                          f'munosabati bilan, siz sertifikat bilan taqdirlandingiz'
                )
                certificates_serializer = CourseCertificateSerializer(certificate)
                response['certificates'] = certificates_serializer.data
        else:
            quiztaker.decrease_chances()
        quiztaker.save()

        response['quiz'] = self.get_serializer(quiz).data
        return Response(response)
