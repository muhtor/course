from rest_framework import serializers

from ...models import Cart, Course, CartCourse


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ('id', 'name', 'image_url', 'price')


class CartCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CartCourse
        fields = ('id', 'insert_type', 'course', 'paid')


class ActiveCartSerializer(serializers.ModelSerializer):
    # courses = CartCourseSerializer(source='cartcourse_set', many=True)
    carts = CourseSerializer(source='courses', many=True)

    class Meta:
        model = Cart
        fields = ('carts', )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        courses_qs = instance.courses.filter(cartcourse__insert_type="UNPAID")
        if courses_qs.exists():
            data['carts'] = CourseSerializer(instance=courses_qs, many=True).data
        else:
            data['carts'] = []

        data['total_price'] = instance.total
        return data


class WishlistCourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'image_url', 'category', 'price', 'old_price')


class ActiveWishlistSerializer(serializers.ModelSerializer):
    data = WishlistCourseSerializer(source='courses', many=True)

    class Meta:
        model = Cart
        fields = ('data', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        qs = instance.courses.filter(cartcourse__insert_type="DESIRE")
        if qs.exists():
            data['data'] = WishlistCourseSerializer(instance=qs, many=True).data
        else:
            data['data'] = None
        return data


class CreateCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartCourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartCourse
        fields = '__all__'

