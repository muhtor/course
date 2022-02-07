from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path('detail/', views.ProfileRetrieveAPIView.as_view(), name="retrieve"),
    path('update/', views.ProfileUpdateView.as_view(), name="update"),
    path('notifications/', views.NotificationListUpdateView.as_view(), name="notifications-list-update"),
    path('notifications/<int:pk>/', views.NotificationDeleteView.as_view(), name="notifications-delete"),

    path('my-courses', views.UserProfileCoursesView.as_view(), name="profile_courses")
]
