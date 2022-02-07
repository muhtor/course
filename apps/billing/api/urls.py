from django.urls import path, include

urlpatterns = (
    path('v1/', include('apps.billing.api.v1.urls')),
)