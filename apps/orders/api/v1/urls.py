from django.urls import path
from . import views

app_name = "orders"

urlpatterns = (
    path('order-checkout', views.OrderCheckoutAPIView.as_view(), name="checkout"),
    path('order-active', views.UserActiveOrder.as_view(), name="order_active"),
    path('order-list/', views.UserOrderListView.as_view(), name="order_list"),
    path('order-detail/<int:pk>/', views.UserOrderDetailView.as_view(), name="order_detail"),
    path('receipt-pay', views.PaycomPerformTransactionView.as_view(), name="receipts_pay"),
    path('merchant-pay', views.PaymentWithPaycomView.as_view(), name="paycom_pay"),
    path('paycom-api', views.PaycomView.as_view(), name="paycom_pay"), # only paycom sends requests
)
