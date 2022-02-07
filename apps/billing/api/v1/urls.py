from django.urls import path
from . import views

app_name = "billing"

urlpatterns = (
    path('card/get/token', views.PaycomCardGetToken.as_view(), name="card_token"),
    path('card/verify/create', views.PaycomCardVerifyCreateAPIView.as_view(), name="verify_create"),
    path('user/card/list', views.UserCardListView.as_view(), name="cards_list"),
    path('user/card/retrieve/<int:pk>/', views.UserCardRetrieveDestroyView.as_view(), name="card_remove"),
    path('get-money', views.UserBalancePerformTransactionView.as_view(), name="get_money"),
)
