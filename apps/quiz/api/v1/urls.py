from django.urls import path
from . import views

urlpatterns = [
	path('all-quizzes/', views.AllQuizListView.as_view()),
	path('my-quizzes/', views.UserCompletedQuizListView.as_view()),  # completed
	path('quizzes/', views.UserUnCompletedQuizListView.as_view()),	 # uncompleted
	path('quizzes/my/<slug:slug>/data/', views.UserUncompletedQuizDetailView.as_view()),
	path('quizzes/my/<slug:slug>/questions/', views.UserUncompletedQuizDetailQuestionsView.as_view()),
	path('quizzes/<slug:slug>/', views.QuizDetailView.as_view()),  # start
	path('save-answer/', views.SaveUsersAnswerView.as_view()),
	path('quizzes/<slug:slug>/submit/', views.SubmitQuizView.as_view()),
]
