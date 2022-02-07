from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


class PhoneActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=7)
        # does my object have a timestamp in here
        end_range = now
        return self.filter(
            activated=False, forced_expired=False).filter(timestamp__gt=start_range, timestamp__lte=end_range)

    def is_confirmable(self, phone):
        now = timezone.now()
        start_range = now - timedelta(days=7)
        return self.filter(
            forced_expired=False, phone=phone).filter(timestamp__gt=start_range, timestamp__lte=now)


class PhoneActivationManager(models.Manager):
    def get_queryset(self):
        return PhoneActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def phone_exists(self, phone):
        return self.get_queryset().filter(Q(phone=phone) | Q(user__phone=phone)).filter(activated=False)
