from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Cart, CartCourse
from ...utils.cart_services import Queries, add_cart_items, \
    handle_error_response, remove_cart_item
from .serializers import ActiveCartSerializer, ActiveWishlistSerializer
from ....courses.models import CertificatedCourse, Course


# ************** CART *****************

class UserActiveCart(APIView):
    # http://127.0.0.1:2000/api/carts/v1/active/cart
    # http://45.132.104.180:2000/api/carts/v1/active/cart
    permission_classes = (IsAuthenticated,)

    @handle_error_response()
    def get(self, request):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user, is_active=True, defaults={'user': user})
        serializer = ActiveCartSerializer(cart)
        data = {"success": True, "code": 400}
        data.update(serializer.data)
        return Response(data)


class AddToCart(APIView, Queries):
    # http://127.0.0.1:2000/api/carts/v1/add/to/cart
    permission_classes = (IsAuthenticated, )

    @handle_error_response()
    def post(self, request):
        """Add all courses, certificated courses sub courses.
        For courses cart updating by them price
        For certificated courses cart updating by the certificated course price
        """
        user = self.request.user
        courses_id = request.data.get('courses', [])
        certificated_courses_id = request.data.get('certificated_courses', [])
        if not courses_id and not certificated_courses_id:
            return Response({
                "success": False,
                "code": 405,
                "message": "Укажите корректные courses/certificated_courses"
            })

        cart, _ = Cart.objects.get_or_create(user=user, is_active=True, defaults={'user': user})
        validation = self.data_is_valid(items=courses_id, user=user)

        if not validation['is_valid']:
            return Response({
                "success": False,
                "code": 403,
                "message": f"неверный идентификатор ("
                           f"{validation['invalid_id']}) /"
                           f" или этот курс уже был куплен"
            })

        add_cart_items(
            courses_id=validation['items'],
            certificated_courses_id=certificated_courses_id,
            cart=cart
        )

        serializer = ActiveCartSerializer(cart)
        data = {"success": True, "code": 402}
        data.update(serializer.data)
        return Response(data)


class RemoveUnpaidCartCourse(APIView, Queries):
    permission_classes = (IsAuthenticated,)
    # http://127.0.0.1:2000/api/carts/v1/remove/unpaid/course

    @handle_error_response()
    def post(self, request):
        """Remove an object from the cart.
        The available types: course, certificated_course.
        The default is course.
        """
        course_id = request.data['id']  # int
        cart = Cart.objects.get(user=self.request.user, is_active=True)

        try:
            remove_cart_item(
                course_id=course_id,
                cart=cart
            )
        except ObjectDoesNotExist:
            e = 'неверный идентификатор объекта'
            return Response({'success': False, 'code': 407, 'message': e})

        return Response({"success": True, "code": 406})



# ************** WISHLIST *****************

class UserActiveWishlist(APIView):
    # http://127.0.0.1:2000/api/carts/v1/active/wishlist
    # http://45.132.104.180:2000/api/carts/v1/active/wishlist
    permission_classes = (IsAuthenticated,)

    @handle_error_response()
    def get(self, request):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user, is_active=True, defaults={'user': user})
        serializer = ActiveWishlistSerializer(cart)
        data = {"success": True, "code": 400}
        data.update(serializer.data)
        return Response(data)


class AddToDesire(APIView, Queries):
    # http://127.0.0.1:2000/api/carts/v1/add/to/wishlist
    permission_classes = (IsAuthenticated, )

    @handle_error_response(411)
    def post(self, request):
        user = self.request.user
        raw_ids = request.data['courses']
        if not raw_ids:
            return Response({"success": False, "code": 405, "message": "неверные данные"})

        cart, _ = Cart.objects.get_or_create(user=user, is_active=True, defaults={'user': user})
        is_validated = self.data_is_valid(items=raw_ids, user=user)
        if is_validated['is_valid']:
            for course_id in is_validated['items']:
                course = Course.objects.get(id=course_id)
                item, _ = CartCourse.objects.get_or_create(
                    insert_type="DESIRE",
                    course=course,
                    cart=cart,
                    defaults={"course": course}
                )
        else:
            return Response({
                "success": False, "code": 403,
                "message": f"неверный идентификатор ({is_validated['invalid_id']}) / или этот курс уже был куплен"
            })
        serializer = ActiveWishlistSerializer(cart)
        data = {"success": True, "code": 410}
        data.update(serializer.data)
        return Response(data)


class RemoveDesireCartCourse(APIView):
    permission_classes = (IsAuthenticated,)
    # http://127.0.0.1:2000/api/carts/v1/remove/desire/course

    def post(self, request):
        course_id = request.data['id']  # int
        try:
            cart = Cart.objects.get(user=self.request.user, is_active=True)
            qs = CartCourse.objects.filter(course_id=course_id, cart=cart, insert_type="DESIRE")
            if qs.exists():
                qs.delete()
                return Response({"success": True, "code": 409})
            else:
                return Response({"success": False, "code": 407, "message": "неверный идентификатор курса"})
        except Exception as e:
            return Response({"success": False, "code": 404, "message": e.args})


