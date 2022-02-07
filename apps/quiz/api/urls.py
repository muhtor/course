from django.urls import path, include

urlpatterns = (
    path('v1/', include('apps.quiz.api.v1.urls')),
)
