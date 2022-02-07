from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = (
    path('create', views.UserCreateAPIView.as_view(), name="create"),
    path('activate', views.PhoneActivationView.as_view(), name='activated'),  # Postman
    path('resend/sms', views.ResendActivationSMS.as_view(), name='resend'),  # Postman
    # path('me', views.UserRetrieveUpdateAPIView.as_view(), name="me"),
    path('password/reset', views.PasswordResetSendView.as_view(), name='reset'),
    path('before/restore', views.PasswordBeforeRestoreView.as_view(), name='before'),
    path('password/restore', views.PasswordRestoreView.as_view(), name='restore'),
    path('before/change', views.UserPasswordBeforeChangeView.as_view(), name='control'),
    path('password/change', views.UserPasswordChangeView.as_view(), name='change'),

    # Social login
    path('login/', include('rest_social_auth.urls_jwt_pair'))
)
