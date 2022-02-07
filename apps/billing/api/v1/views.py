from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ...models import Card, AccountBalance
from ....core.utils.subscribe_api.api import PaycomApi
from django.shortcuts import get_object_or_404
from ....billing.api.v1.serializers import (
    CardCreateSerializer,
    CardListSerializer,
    BalanceTransactionCreateSerializer,
    BalanceTransactionDetailSerializer
)


class PaycomCardGetToken(APIView, PaycomApi):
    # http://127.0.0.1:2000/api/billing/v1/card/get/token

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = self.card_create(str(request.data['number']), str(request.data['expire']))
        if response['success']:
            return Response(response)
        return Response(response)


class PaycomCardVerifyCreateAPIView(APIView, PaycomApi):
    # http://127.0.0.1:2000/api/billing/v1/card/verify/create

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        verification = self.card_verify(sms=str(request.data['sms']), token=str(request.data['token']))
        try:
            if verification['success']:
                paycom = verification.pop('paycom')
                card = paycom['result']['card']
                number = card['number']
                expire = card['expire']
                # exp_month = expire.split("/")[0]
                # exp_year = expire.split("/")[1]
                first = number[:4]
                first6 = number.replace(" ", "")[:6]
                last4 = number[len(number) - 4:]
                token = card['token']
                phone = request.data['phone']
                holder_name = self.get_holder(user=user)
                card_data = {
                    'user': user.pk, 'holder_name': holder_name,
                    'brand': self.get_brand(card_4=first), 'country': "Uzbekistan",
                    'expire': expire, 'token': token,
                    'first6': first6, 'last4': last4, 'masked16': number,
                    'phone': phone, 'is_verify': card['verify']
                }
                serializer = CardCreateSerializer(data=card_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response({
                        "success": True, "verify": card['verify'], "code": 310, "message": verification['message']})
                else:
                    return Response({"success": False, "code": 311, "message": serializer.errors})
            else:
                return Response({"success": False, "code": 312, "message": verification['message']})
        except Exception as e:
            return Response({"success": False, "code": 334, "message": e.args})


class UserCardListView(generics.ListAPIView):
    #  http://127.0.0.1:2000/api/billing/v1/user/card/list
    permission_classes = (IsAuthenticated, )
    serializer_class = CardListSerializer

    def list(self, request, *args, **kwargs):
        queryset = Card.objects.filter(user=self.request.user, status="ACTIVE")
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            response = {'success': True, 'code': 320, 'result': serializer.data}
            return Response(response)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = {'success': False, 'code': 321, 'result': serializer.data}
            return Response(response)


class UserCardRetrieveDestroyView(generics.RetrieveUpdateDestroyAPIView, PaycomApi):
    """
    GET, DELETE > http://127.0.0.1:2000/api/billing/v1/user/card/retrieve/2/
    """
    permission_classes = (IsAuthenticated,)
    queryset = Card.objects.filter(status="ACTIVE")
    serializer_class = CardListSerializer
    lookup_field = 'pk'

    def get_object(self):
        return get_object_or_404(Card, id=self.kwargs["pk"])

    def retrieve(self, request, *args, **kwargs):
        try:
            queryset = self.get_object()
            serializer = self.get_serializer(queryset)
            return Response({"success": True, "code": 300, "data": serializer.data})
        except Exception as e:
            return Response({"success": False, "code": 304, "data": e.args})

    def delete(self, request, *args, **kwargs):
        qs_card = Card.objects.filter(pk=self.kwargs["pk"], status="ACTIVE")
        if qs_card.exists():
            response = self.card_remove(token=qs_card.first().token)
            if 'error' in response:
                return Response(response)
            elif response['success']:
                qs_card.update(status="DELETED")
                return Response({"success": True, "code": 330, "message": "карта успешно удалена"})
            else:
                return Response({"success": False, "code": 331, "message": "удаление не удалось"})
        else:
            return Response({
                "success": False, "code": 304, "message": "карта не найдена"})


class UserBalancePerformTransactionView(APIView):
    """
    POST > http://127.0.0.1:2000/api/billing/v1/get-money
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        try:
            balance = AccountBalance.objects.get(user=user)
            if balance.bonus < 1:
                raise ValueError('Баланс пользователя меньше допустимого')
            data = {"user": user.pk, "amount": balance.amount}
            serializer = BalanceTransactionCreateSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                balance.bonus = 0
                balance.amount = 0
                balance.save()
                detail = BalanceTransactionDetailSerializer(serializer.instance)
                return Response({"success": True, "code": 350, "data": detail.data})
            return Response({"success": False, "code": 351, "message": "Invalid data"})
        except Exception as e:
            return Response({"success": False, "code": 352, "message": e.args})
