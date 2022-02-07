from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path('category-list/', views.CategoryListView.as_view(), name='category_list'),  # All Category list
    path('course-list/', views.CourseListView.as_view(), name='course-list'),
    path('course-detail/<int:pk>/', views.CourseRetrieveView.as_view(), name='course-detail'),
    path('topic-list/', views.TopicListView.as_view(), name='topic-list'),
    path('topic-detail/<int:pk>/', views.TopicRetrieveView.as_view(), name='topic-list'),
    path('lesson-list/', views.LessonListView.as_view(), name='lesson-list'),
    path('lesson-detail/<int:pk>/', views.LessonRetrieveView.as_view(), name='lesson-detail'),
    path('user-lessons/update/<int:pk>/', views.UserLessonAPI.as_view(), name='user-lessons-update'),  # Lesson pk
    path('certificates/', views.CourseCertificateListView.as_view(), name='certificates-list'),
    path('certificates/<str:hash>/verify/', views.CourseCertificateVerifyView.as_view()),
    path('certificated-courses/', views.CertificatedCourseListView.as_view(), name='certificated-courses-list'),
    path('certificated-courses/<int:pk>/data/', views.CertificatedCourseDetailView.as_view()),
    path('certificated-courses/<int:pk>/courses/', views.CertificatedCourseDetailCoursesView.as_view()),
]
