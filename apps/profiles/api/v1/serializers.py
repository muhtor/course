from django.conf import settings
from rest_framework import serializers

from ....carts.models import Cart, Course
from ....profiles.models import Profile, Notification, NotificationCategory
from ....accounts.models import AccountBalance


class AccountBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountBalance
        fields = ('amount', )


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.phone', read_only=True)
    ref = serializers.CharField(source='user.ref', read_only=True)
    # balance = serializers.SerializerMethodField()
    # image = serializers.CharField(source='image', read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'ref', 'balance', 'first_name', 'last_name', 'full_name',
            'phone', 'country', 'city', 'date_birth', 'image_url', 'image', 'street')
        read_only_fields = ('user', 'ref')

    # def get_balance(self, obj):
    #     return AccountBalance.objects.get(user=obj.user).amount

    # def get_image(self, obj):
    #     qs = Profile.objects.filter(user=obj.user)
    #     image = None
    #     if qs.exists():
    #         image = qs.first().image.url if qs.first().image else None
    #         return image
    #     return image

    # def to_representation(self, instance):
    #     if instance.image:
    #         url = instance.image.url
    #         print("URL........", url, type(url))
    #         request = self.context.get('request', None)
    #         if request is not None:
    #             return request.build_absolute_uri(url)
    #         return url

    # def to_representation(self, value):
    #     # Build absolute URL (next line is just sample code)
    #     return settings.MEDIA_URL + str(value.image)


class NotificationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCategory
        fields = ('name',)


class NotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    time = serializers.IntegerField(source='created_ago', read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'title', 'category', 'time', 'show_status')


class PaidCoursesSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'image_url', 'category', 'price', 'old_price')


class ProfileCoursesSerializer(serializers.ModelSerializer):
    data = PaidCoursesSerializer(source='courses', many=True)

    class Meta:
        model = Cart
        fields = ('data', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        qs = instance.courses.filter(cartcourse__insert_type="PAID")
        if qs.exists():
            data['data'] = PaidCoursesSerializer(instance=qs, many=True).data
        else:
            data['data'] = None
        return data


