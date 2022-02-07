from rest_framework import serializers
from ...models import Review
from ....profiles.models import Profile
from datetime import datetime


class ReviewSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    user_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    date_after = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'user_name', 'image_url', 'date_after', 'course_id', 'course_name', 'desc', 'rates')
        # extra_kwargs = {'user': {'required': False}, 'course': {'required': False}}

    def get_user_name(self, obj):
        qs = Profile.objects.filter(user=obj.user)
        if qs.exists():
            return qs.first().first_name
        return ""

    def get_image_url(self, obj):
        qs = Profile.objects.filter(user=obj.user)
        image = None
        if qs.exists():
            image = qs.first().image.url if qs.first().image else None
            return image
        return image

    def get_date_after(self, obj):
        date = datetime.today().date() - obj.date_created
        return date.days
