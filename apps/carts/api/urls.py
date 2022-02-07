from django.urls import path, include

urlpatterns = (
    path('v1/', include('apps.carts.api.v1.urls')),
)