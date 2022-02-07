from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from ...models import Profile, Notification
from ....courses.models import UserCourse, CourseCertificate
from .serializers import Cart, ProfileSerializer, NotificationSerializer, ProfileCoursesSerializer
from ....core.api.response import get_error_response, get_success_response
from ....core.api.schemas import ProfileDetailScheme, ProfileUpdateScheme
from ....core.utils.apiviews import PaginationResponse, PaginationListAPIView, CustomDestroyAPIView


class ProfileRetrieveAPIView(APIView):
    # GET http://127.0.0.1:2000/api/profiles/v1/detail
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    schema = ProfileDetailScheme

    def get(self, request):
        user = self.request.user
        qs = Profile.objects.filter(user=user)
        if qs.exists():
            serializer = self.serializer_class(qs[0])
            return Response({"success": True, "code": 200, "profile": serializer.data})
        else:
            return Response({"success": False, "code": 209, "profile": "Профиль пользователя не существует"})


class ProfileUpdateView(APIView):
    # POST http://127.0.0.1:2000/api/profiles/v1/update
    permission_classes = (IsAuthenticated,)
    schema = ProfileUpdateScheme

    def post(self, request):
        user = self.request.user
        data = request.data.copy()
        data['user'] = user
        qs = Profile.objects.filter(user=user)
        if qs.exists():
            try:
                profile = Profile.objects.get(user=user)
                serializer = ProfileSerializer(profile, data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response({"success": True, "code": 202, "profile": serializer.data})
                else:
                    return Response({"success": False, "code": 203, "profile": {}})
            except Exception as e:
                return Response({"success": False, "code": 213, "error": e.args})
        else:
            return Response({"success": False, "code": 209, "profile": "Профиль пользователя не существует"})


class NotificationListUpdateView(PaginationListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    list_codes = {'success': 210, 'error': 211}
    update_codes = {'success': 215, 'error': 216}

    def get_queryset(self):
        return self.request.user.profile.notifications.all()

    def post(self, request):
        try:
            for notification in Notification.objects.filter(id__in=request.data['ids']):
                notification.toggle()
            return Response(get_success_response(code=self.update_codes['success']))
        except Exception as e:
            return Response(get_error_response(code=self.update_codes['error'], exception=e))


class NotificationDeleteView(CustomDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    destroy_codes = {'success': 220, 'error': 221}

    def get_queryset(self):
        return self.request.user.profile.notifications.all()


class UserProfileCoursesView(generics.ListAPIView, PaginationResponse):
    # GET http://127.0.0.1:2000/api/profiles/v1/my-courses
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileCoursesSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        try:
            certificate_count = 0
            user_courses = UserCourse.objects.filter(user=user)
            for item in user_courses:
                user_certificate = CourseCertificate.objects.filter(user=user, course_id=item.course.id)
                if user_certificate.exists():
                    certificate_count += 1
            queryset = Cart.objects.filter(user=user, is_active=True)
            result = self.paginated_queryset(queryset, request)
            serializer = self.serializer_class(result, many=True)
            data = {
                "paid_courses": user_courses.filter(status="new").count(),
                "progress_courses": user_courses.filter(status="progress").count(),
                "finished_courses": user_courses.filter(status="finished").count(),
                "certificated_course": certificate_count
            }
            response = self.paginated_response(status=True, code=250, data=serializer.data[0]['data'])
            data.update(response.data)
            return Response(data)
        except Exception as e:
            return Response({"success": False, "code": 251, "error": e.args})
