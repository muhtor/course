from datetime import datetime, timezone

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from ..core.models import TimestampedModel
from ..accounts.models import AccountBalance
from ..quiz.models import QuizTaker


class Profile(TimestampedModel):
    user = models.OneToOneField('accounts.User', related_name='profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    date_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='images/profiles', null=True, blank=True)
    street = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.first_name} / {self.user.phone}"

    @property
    def image_url(self):
        return f"{self.image.url}" if self.image else None

    @property
    def balance(self):
        qs = AccountBalance.objects.filter(user=self.user)
        if qs.exists():
            return qs.first().amount
        else:
            return 0

    def is_course_paid(self, course) -> bool:
        for cart in self.user.cart_set.all():
            if cart.cartcourse_set.filter(course=course, paid=True).exists():
                return True

    def get_last_quiztaker(self, quiz):
        return get_object_or_404(QuizTaker, user=self.user, quiz=quiz)

    def get_full_name(self) -> str:
        result = ''
        if self.first_name:
            result = self.first_name
        if self.last_name:
            result = f'{result} {self.last_name}'
        if self.full_name:
            result = f'{result} {self.full_name}'

        if not self.user.password and not result:
            return self.user.email or 'Unknown user'
        if not result:
            return self.user.phone
        return result


class NotificationCategory(models.Model):
    name = models.CharField(_('Name'), max_length=30)

    def __str__(self):
        return self.name


class Notification(models.Model):
    profile = models.ForeignKey(Profile, related_name='notifications', on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    show_status = models.BooleanField(verbose_name=_('Show'), default=True)
    category = models.ForeignKey(NotificationCategory, related_name='notifications',
                                 on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.profile.user.phone} - {self.title}'

    def toggle(self):
        self.show_status = not self.show_status
        self.save(update_fields=('show_status',))

    def created_ago(self):
        """Created time ago in minutes"""
        return int((datetime.now(timezone.utc) - self.created_at).total_seconds() / 60)
