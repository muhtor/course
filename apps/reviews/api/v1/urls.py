from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = (
    path('review-create', views.ReviewCreateListView.as_view(), name='review_create'),
    path('review-list/<int:pk>/', views.ReviewCreateListView.as_view(), name='review_list'),
)
