from django.urls import path
from . import views

app_name = "carts"

urlpatterns = (
    path('active/cart', views.UserActiveCart.as_view(), name="cart"),
    path('add/to/cart', views.AddToCart.as_view(), name="add_cart"),
    path('remove/unpaid/course', views.RemoveUnpaidCartCourse.as_view(), name="remove_unpaid"),
    path('active/wishlist', views.UserActiveWishlist.as_view(), name="wishlist"),
    path('add/to/wishlist', views.AddToDesire.as_view(), name="add_desire"),
    path('remove/desire/course', views.RemoveDesireCartCourse.as_view(), name="remove_desire"),
)
