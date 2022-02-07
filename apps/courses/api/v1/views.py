from django.db.models import Q
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsAvailableForLesson, IsLessonCoursePaid, IsUserLessonCoursePaid
from ...models import Course, Topic, Lesson, Category, UserCourse, UserLesson, CertificatedCourse, CourseCertificate
from ....quiz.api.v1.serializers import CourseCertificateSerializer
from ....core.utils.apiviews import PaginationListAPIView, \
    CustomRetrieveAPIView, \
    CustomPartialUpdateAPIView, ViewSerializerRequestContext
from .serializers import (
    CourseListSerializer,
    UserCourseListSerializer,
    TopicSerializer,
    LessonListSerializer,
    LessonDetailSerializer,
    CategorySerializer,
    TopicDetailSerializer,
    CourseDetailSerializer, UserLessonSerializer, CertificatedCourseSerializer, CertificatedCourseSubCourseSerializer,
)


class CategoryListView(PaginationListAPIView):
    # http://127.0.0.1:2000/api/courses/v1/category-list/?id=1
    serializer_class = CategorySerializer
    list_codes = {'success': 500, 'error': 501}

    def get_queryset(self):
        """
            Query params:
            ?id (int): id of parent category
        """
        queryset = Category.objects.filter(parent_category=None, is_active=True)
        category_id = self.request.query_params.get('id')
        if category_id is not None:
            try:
                queryset = queryset.filter(id=int(category_id))
            except ValueError:
                return []
        return queryset


class CourseListView(PaginationListAPIView):
    # http://127.0.0.1:2000/api/courses/v1/course-list/?cat=1
    serializer_class = CourseListSerializer
    list_codes = {'success': 505, 'error': 506}

    def get_queryset(self, *args, **kwargs):
        """
            Query params:
            ?cat_id (int): courses category id
        """
        queryset = Course.objects.filter(is_active=True)
        category_id = self.request.query_params.get('cat_id')
        if category_id is not None:
            try:
                category_ids = []
                qs_category = Category.objects.filter(id=category_id)
                for item in qs_category:
                    category_ids.append(item.pk)
                    children = item.children.all()
                    for child in children:
                        category_ids.append(child.pk)
                queryset = queryset.filter(category__in=category_ids)
            except ValueError:
                return []
        return queryset


class CourseRetrieveView(CustomRetrieveAPIView):
    # http://127.0.0.1:2000/api/courses/v1/course-detail/{id}
    serializer_class = CourseDetailSerializer
    retrieve_codes = {'success': 510, 'error': 511}

    def get_queryset(self):
        return Course.objects.filter(is_active=True)


class TopicListView(PaginationListAPIView):
    # http://127.0.0.1:2000/api/courses/v1/topic-list/?q=OOP
    serializer_class = TopicSerializer
    list_codes = {'success': 515, 'error': 516}

    def get_queryset(self, *args, **kwargs):
        queryset = Topic.objects.all()
        query = self.request.GET.get("q", None)
        if query:
            try:
                return queryset.filter(Q(name__icontains=query) | Q(course__name__icontains=query)).distinct()
            except ValueError:
                return []
        return queryset


class TopicRetrieveView(CustomRetrieveAPIView):
    # http://127.0.0.1:2000/api/courses/v1/topic-detail/{id}
    serializer_class = TopicDetailSerializer
    retrieve_codes = {'success': 520, 'error': 521}
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Topic.objects.all()


class LessonListView(PaginationListAPIView):
    # http://127.0.0.1:2000/api/courses/v1/lesson-list/?q=opop
    serializer_class = LessonListSerializer
    list_codes = {'success': 525, 'error': 526}

    def get_queryset(self, *args, **kwargs):
        queryset = Lesson.objects.all()
        query = self.request.GET.get("q", None)
        if query:
            try:
                return queryset.filter(Q(name__icontains=query) | Q(topic__name__icontains=query)).distinct()
            except ValueError:
                return []
        return queryset


class LessonRetrieveView(CustomRetrieveAPIView):
    # http://127.0.0.1:2000/api/courses/v1/lesson-detail/{id}/
    serializer_class = LessonDetailSerializer
    permission_classes = (IsLessonCoursePaid, IsAvailableForLesson,)
    retrieve_codes = {'success': 530, 'error': 531}

    def get_queryset(self):
        return Lesson.objects.all()


class UserLessonAPI(CustomPartialUpdateAPIView):
    """Partial update user lesson. Update the status"""
    serializer_class = UserLessonSerializer
    permission_classes = (IsAuthenticated, IsUserLessonCoursePaid)
    patch_codes = {'success': 535, 'error': 536}

    def get_object(self, pk):
        lesson = Lesson.objects.get(id=pk)
        if lesson.is_blocked(self.request.user):
            raise ValueError('Previous lesson was not completed')

        user_lesson, created = UserLesson.objects.get_or_create(
            user=self.request.user,
            lesson__id=pk,
            defaults={'lesson': lesson}
        )
        return user_lesson


class CourseCertificateListView(PaginationListAPIView):
    serializer_class = CourseCertificateSerializer
    permission_classes = (IsAuthenticated,)
    list_codes = {'success': 540, 'error': 541}

    def get_queryset(self):
        return self.request.user.certificates.all()


class CourseCertificateVerifyView(RetrieveAPIView):
    """API for verifying certificates by hash.
    If there's a certificate with the given hash - successfully verified
    """
    queryset = CourseCertificate.objects.all()
    lookup_field = 'hash'

    def retrieve(self, request, *args, **kwargs):
        certificate_qs = self.queryset.filter(hash=kwargs['hash'])
        if certificate_qs:
            certificate_pdf = certificate_qs.last().pdf.url
            return Response(
                status=200,
                data={'success': True, 'certificate_pdf': certificate_pdf, 'code': 555}
            )
        return Response(status=400, data={'success': False, 'code': 556})


class CertificatedCourseListView(PaginationListAPIView, ViewSerializerRequestContext):
    serializer_class = CertificatedCourseSerializer
    list_codes = {'success': 545, 'error': 546}

    def get_queryset(self):
        return CertificatedCourse.objects.all()


class CertificatedCourseDetailView(CustomRetrieveAPIView, ViewSerializerRequestContext):
    """Main certificated course info"""
    serializer_class = CertificatedCourseSerializer
    retrieve_codes = {'success': 550, 'error': 551}

    def get_queryset(self):
        return CertificatedCourse.objects.all()


class CertificatedCourseDetailCoursesView(PaginationListAPIView):
    """Certificated course sub courses detail info"""
    serializer_class = CertificatedCourseSubCourseSerializer
    list_codes = {'success': 555, 'error': 556}

    def get_queryset(self, *args, **kwargs):
        return CertificatedCourse.objects.get(id=self.kwargs['pk']).sub_courses.all()
