from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from ...utils.query import Query
from ....core.api.schemas import UserCreateScheme
from ....accounts.models import User, PhoneActivation
from .serializers import UserCreateSerializer, UserSerializer, LogoutSerializer
from .renderers import UserJSONRenderer
from ....profiles.models import Notification, Profile


class UserCreateAPIView(APIView):
    # http://127.0.0.1:2000/api/auth/v1/create
    permission_classes = (AllowAny,)
    schema = UserCreateScheme

    def post(self, request):
        data = self.request.data['user']
        phone = data['phone']
        qs_user = User.objects.filter(phone=phone)
        if qs_user.exists():
            if qs_user.filter(is_active=True).exists():
                return Response({"success": False, "code": 100, "error": "с этим номером есть активный пользователь"})
            else:
                return Response({"success": False, "code": 101,
                                 "error": f"этот номер уже зарегистрирован и ожидает активации"})
        else:
            serializer = UserCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            qs_activation = PhoneActivation.objects.filter(user__phone=serializer.data['phone'])
            if qs_activation.exists():
                response = serializer.data
                response['referrer'] = data['referrer']
                Notification.objects.create(
                    profile=Profile.objects.get(user__phone=phone),
                    title="Xush kelibsiz. Siz muvaffaqiyatli royhattdan"
                          "o'ttingiz. Iltimos shaxsiz ma'lumotlaringizni to'ldiring"
                )
                return Response({"success": True, "code": 102, "user": response})
            else:
                return Response({"success": False, "code": 103, "error": "не удалось создать пользователя"})


class LogoutApiView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True}, status=status.HTTP_205_RESET_CONTENT)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_data = request.data.get('user', {})
        serializer_data = {
            'phone': user_data.get('phone', request.user.phone),
            'profile': {
                'first_name': user_data.get('first_name', request.user.profile.first_name),
                'last_name': user_data.get('last_name', request.user.profile.last_name)
            }
        }
        serializer = self.serializer_class(request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PhoneActivationView(APIView, Query):
    # http://127.0.0.1:2000/api/auth/v1/activate
    def post(self, request):
        data = self.request.data
        qs_user = User.objects.filter(phone=data['phone'])
        qs_activation = PhoneActivation.objects.filter(phone=data['phone'])

        if qs_user.exists() and qs_activation.exists():
            user = qs_user.first()
            if qs_user.filter(is_active=True).exists() and qs_activation.filter(activated=True).exists():
                return Response({"success": False, "code": 105, "message": f"пользователь уже активирован"})
            obj = qs_activation.first()
            if obj.code == data['code']:
                obj.activate()
                self.save_referred_users(user=user, key=data['referrer'])
                return Response({"success": True, "code": 104, "message": "активация прошло успешно"})
            else:
                return Response({"success": False, "code": 106, "error": "неправильный код подтверждения"})
        else:
            return Response({"success": False, "code": 107, "error": "неправильный номер телефона"})


class ResendActivationSMS(APIView):
    # http://127.0.0.1:2000/api/auth/v1/resend/sms
    def post(self, request):
        phone = self.request.data['phone']
        password = self.request.data['password']
        qs_user = User.objects.filter(phone=phone)
        qs_activation = PhoneActivation.objects.filter(phone=phone)
        if qs_user.exists() and qs_activation.exists():
            if qs_user.filter(is_active=True).exists() and qs_activation.filter(activated=True).exists():
                return Response({"success": False, "code": 109, "error": "этот номер уже активирован"})
            else:
                user = qs_user.first()
                user.set_password(password)
                user.save()
                qs_activation.first().send_activation_sms(resend=True)
                return Response({"success": True, "code": 108, "message": "код подтверждения повторно отправлен"})
        else:
            return Response({"success": False, "code": 110, "error": "неправильный номер телефона"})


class PasswordResetSendView(APIView):
    # URL: http://127.0.0.1:8000/api/auth/v1/password/reset
    def post(self, request):
        phone = self.request.data['phone']
        qs_user = User.objects.filter(phone=phone, is_active=True)
        qs_activation = PhoneActivation.objects.filter(phone=phone, activated=True)
        if qs_user.exists() and qs_activation.exists():
            qs_activation.first().send_activation_sms(resend=True)
            return Response({"success": True, "code": 111, "message": "код подтверждения отправлен"})
        else:
            return Response({"success": False, "code": 112, "error": "неправильный номер телефона"})


class PasswordBeforeRestoreView(APIView):
    # URL: http://127.0.0.1:8000/api/auth/v1/password/before/restore

    def post(self, request):
        data = self.request.data
        qs = PhoneActivation.objects.filter(phone=data['phone'], code=data['sms'], activated=True)
        if qs.exists():
            return Response({"success": True, "code": 113, "message": "проверка кода прошло успешно"})
        else:
            return Response({"success": False, "code": 114, "error": "неправильный код подтверждения"})


class PasswordRestoreView(APIView):
    # URL: http://127.0.0.1:8000/api/auth/v1/password/restore

    def post(self, request):
        data = self.request.data
        qs_user = User.objects.filter(phone=data['phone'], is_active=True)
        qs_activation = PhoneActivation.objects.filter(phone=data['phone'], code=data['sms'], activated=True)
        if qs_user.exists() and qs_activation.exists():
            user = qs_user.first()
            user.set_password(data['password1'])
            user.save()
            return Response({"success": True, "code": 115, "message": "аккаунт успешно восстановлена"})
        else:
            return Response({"success": False, "code": 116, "error": "неправильный код подтверждения"})


class UserPasswordBeforeChangeView(APIView):
    # URL: http://127.0.0.1:8000/api/auth/v1/before/change

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        password_control = user.check_password(self.request.data['old_password'])  # bool
        if password_control:
            return Response({"success": True, "code": 117, "message": "проверка прошло успешно"})
        else:
            return Response({"success": False, "code": 118, "error": "Введен неверный пароль"})


class UserPasswordChangeView(APIView):
    # URL: http://127.0.0.1:8000/api/auth/v1/password/change

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = self.request.data
        user = self.request.user
        password1 = data['password1']
        password2 = data['password2']
        if password1 == password2:
            user.set_password(password1)
            user.save()
            return Response({"success": True, "code": 119, "message": "пароль успешно изменен"})
        else:
            return Response({"success": False, "code": 120, "error": "пароль не совпадал"})

