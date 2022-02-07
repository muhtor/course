from rest_framework import serializers
from ...models import OrderCheckout, CheckoutItem, Order
from ....carts.api.v1.serializers import CourseSerializer, ActiveCartSerializer


class ActiveOrderCheckoutSerializer(serializers.ModelSerializer):
    orders = CourseSerializer(source='checkout_courses', many=True)

    class Meta:
        model = OrderCheckout
        fields = ('orders', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        total = 0
        qs = instance.checkout_courses.all()
        if qs.exists():
            data['orders'] = CourseSerializer(instance=qs, many=True).data
            for item in qs:
                total += item.price
        else:
            data['orders'] = None
        data['total_price'] = instance.total
        return data


class CheckoutItemSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(source='checkout_courses', many=True)

    class Meta:
        model = OrderCheckout
        fields = ('courses', )


class ActiveOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_id', 'subtotal', 'total', 'payment_status', 'is_active')

    def to_representation(self, instance):
        data = super(ActiveOrderSerializer, self).to_representation(instance)
        checkout = instance.checkout
        if checkout:
            courses = CheckoutItemSerializer(checkout)
            data.update(courses.data)
        else:
            data['courses'] = None
        return data


class UserOrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_id', 'subtotal', 'total', 'payment_status', 'is_active')

    def to_representation(self, instance):
        data = super(UserOrderListSerializer, self).to_representation(instance)
        checkout = instance.checkout
        if checkout:
            courses = CheckoutItemSerializer(checkout)
            data.update(courses.data)
        else:
            data['courses'] = None
        return data


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
