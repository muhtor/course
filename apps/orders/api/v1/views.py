from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
import base64
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ...models import OrderCheckout, CheckoutItem, Order
from ....billing.models import Card
from ....carts.models import Cart, CartCourse
from .serializers import ActiveOrderCheckoutSerializer, CreateOrderSerializer, ActiveOrderSerializer, \
    UserOrderListSerializer
from ....core.utils.subscribe_api.api import PaycomApi
from ....core.utils.merchant_api.application import Application
from ....core.utils.apiviews import PaginationListAPIView, CustomRetrieveAPIView
from ....profiles.models import Notification


class OrderCheckoutAPIView(APIView):
    # http://127.0.0.1:2000/api/orders/v1/order/checkout

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        try:
            cart = Cart.objects.get(user=user, is_active=True)
            qs_checkout = OrderCheckout.objects.filter(user=user, paid=False, is_active=True)
            qs_order = Order.objects.filter(user=user, is_active=True)
            if qs_checkout.exists() and qs_order.exists():
                checkout = qs_checkout[0]
                checkout_items = checkout.checkout_courses.all()
                cart_items = cart.courses.filter(cartcourse__insert_type="UNPAID")

                set_list1 = set(tuple((d.id,) for d in checkout_items))
                set_list2 = set(tuple((d.id,) for d in cart_items))

                if set_list1 == set_list2:
                    serializer = ActiveOrderCheckoutSerializer(checkout)
                    data = {"success": True, "code": 700, 'order_unique_id': qs_order.first().order_id}
                    data.update(serializer.data)
                    return Response(data)
                else:
                    qs_checkout.delete()
                    qs_order.delete()
                    return self.new_order_checkout()
            else:
                return self.new_order_checkout()
        except Exception as e:
            return Response({"success": False, "code": 701, "message": e.args})

    def new_order_checkout(self):
        """Select unpaid items then Create new Order for Payment"""
        user = self.request.user
        try:
            cart = Cart.objects.get(user=user, is_active=True)
            unpaid_items = CartCourse.objects.filter(cart=cart, paid=False, insert_type="UNPAID")
            if not unpaid_items.exists():
                return Response({"success": False, "code": 704, "error": "курс не выбран для оплаты"})
            checkout = OrderCheckout.objects.create(user=user, total=cart.total)
            for item in unpaid_items:
                course = item.course
                CheckoutItem.objects.create(course=course, checkout=checkout)
            data = {'user': user.pk, 'checkout': checkout.pk, 'subtotal': cart.subtotal, 'total': cart.total}
            serializer = CreateOrderSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                new_order = ActiveOrderCheckoutSerializer(checkout)
                data = {"success": True, "code": 700, 'order_unique_id': serializer.data['order_id']}
                data.update(new_order.data)
                return Response(data)
            return Response({"success": False, "code": 703, "error": serializer.errors})
        except Cart.DoesNotExist:
            return Response({"success": False, "code": 702, "error": "активная корзина недоступна"})


class UserActiveOrder(APIView):
    # http://127.0.0.1:2000/api/orders/v1/order-active
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        qs = Order.objects.filter(user=user, is_active=True)
        if qs.exists():
            serializer = ActiveOrderSerializer(qs.first())
            return Response({"success": True, "code": 710, "order": serializer.data})
        else:
            return Response({"success": False, "code": 711, "message": "активный заказ недоступен"})


class UserOrderListView(PaginationListAPIView):
    # http://127.0.0.1:2000/api/orders/v1/order-list/?status=created
    permission_classes = (IsAuthenticated,)
    serializer_class = UserOrderListSerializer

    list_codes = {'success': 720, 'error': 721}

    def get_queryset(self):
        """
        Query params: /?status=paid
        """
        queryset = Order.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status')
        if status is not None:
            try:
                queryset = queryset.filter(payment_status=status)
            except ValueError:
                return []
        return queryset


class UserOrderDetailView(CustomRetrieveAPIView):
    # http://127.0.0.1:2000/api/orders/v1/order-detail/{id}
    permission_classes = (IsAuthenticated,)
    serializer_class = UserOrderListSerializer
    retrieve_codes = {'success': 722, 'error': 723}

    def get_queryset(self):
        return Order.objects.all()


class PaycomPerformTransactionView(APIView, PaycomApi):
    """
    POST: http://127.0.0.1:2000/api/orders/v1/receipt-pay
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        try:
            card = Card.objects.get(user=user, id=request.data['card_id'])
            order = Order.objects.get(user=user, order_id=request.data['order_unique_id'], is_active=True)
            return self.create_transaction(card=card, amount=int(order.total), order=order)
        except Exception as e:
            return Response({"success": False, "code": 754, "error": e.args})

    def create_transaction(self, card, amount, order):
        """Create Transaction"""
        receipt = self.receipts_create(amount=amount, order_id=order.id)
        if 'error' in receipt:
            return Response({"success": False, "code": 751, "message": receipt['message']})
        elif receipt['status'] == 200 and "transaction" in receipt:
            return self.perform_transaction(transaction=receipt['transaction'], card=card, order=order)
        else:
            return Response({"success": False, "code": 752, "message": receipt['message']})

    def perform_transaction(self, transaction, card, order):
        """Perform Transaction"""
        payment = self.receipt_pay(user=self.request.user, transaction_id=transaction, card=card, order=order)
        try:
            if 'error' in payment:
                return Response({"success": False, "paid": False, "code": 755, "message": payment['message']})
            elif payment['status'] == 200:
                Notification.objects.create(
                    profile=card.user.profile,
                    title=f"Siz {Cart.objects.filter(user=card.user).last().paid_courses} kursini xarid qildingiz."
                )
                return Response({"success": True, "paid": True, "code": 757, "message": "оплата произведена успешно"})
            else:
                return Response({"success": False, "paid": False, "code": 756, "message": payment['message']})
        except Exception as e:
            return Response({"success": False, "code": 759, "error": e.args})


class PaymentWithPaycomView(APIView):
    """
    POST: http://127.0.0.1:2000/api/orders/v1/merchant-pay
    https://checkout.paycom.uz/base64(m=587f72c72cac0d162c722ae2;ac.order_id=197;a=500)
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        merchant = settings.PAYCOM_MERCHANT_ID
        try:
            order = Order.objects.get(user=user, order_id=request.data['order_unique_id'], is_active=True)
            amount = int(order.total) * 100
            redirect_url = "https://aristotle.uz/user"
            paycom_url = "https://checkout.paycom.uz/"
            # paycom_url = "https://test.paycom.uz/"
            params = f"m={merchant};ac.order_id={order.id};a={amount};c={redirect_url}"
            encoded_param = base64.b64encode(bytes(params, "utf-8")).decode('ascii')
            data = f"{paycom_url}{encoded_param}"
            return Response({"success": True, "code": 760, "url": data})
        except Exception as e:
            return Response({"success": False, "code": 761, "error": e.args})


class PaycomView(APIView):
    """
    Paycom callback request
    POST: http://127.0.0.1:2000/api/orders/v1/paycom-pay
    """
    def post(self, request):
        app = Application(request=request)
        response = app.run()
        import json
        new_data = json.loads(response)
        return JsonResponse(data=new_data, safe=False)
