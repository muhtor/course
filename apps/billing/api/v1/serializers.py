from rest_framework import serializers
from ...models import Card, CardStatusTypes, AccountBalance, BalanceTransaction


class CardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('user', 'holder_name', 'brand', 'country',
                  'expire', 'token', 'first6', 'last4', 'masked16', 'phone', 'is_verify')

    def create(self, validated_data):
        obj, created = Card.objects.update_or_create(
            user=validated_data.get('user'),
            brand=validated_data.get('brand'),
            country=validated_data.get('country'),
            expire=validated_data.get('expire'),
            first6=validated_data.get('first6'),
            last4=validated_data.get('last4'),
            masked16=validated_data.get('masked16'),
            phone=validated_data.get('phone'),
            is_verify=validated_data.get('is_verify'),
            status=CardStatusTypes.ACTIVE,
            defaults={
                "token": validated_data.get('token')
            }  # this field for update
        )
        return obj


class CardListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Card
        fields = ('id', 'user', 'brand', 'country', 'expire', 'first6', 'last4', 'masked16', 'phone')


class BalanceTransactionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BalanceTransaction
        fields = ('id', 'user', 'amount')


class AccountBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountBalance
        fields = ('id', 'user', 'bonus', 'amount')


class BalanceTransactionDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', read_only=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = BalanceTransaction
        fields = ('id', 'user', 'amount', 'status')
