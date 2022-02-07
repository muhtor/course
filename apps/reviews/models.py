from ckeditor.fields import RichTextField
from django.db import models
from ..accounts.models import User
from ..courses.models import Course
from django.utils.translation import gettext_lazy as _


class Review(models.Model):
    RATES = ((5, 5), (4, 4), (3, 3), (2, 2), (1, 1))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    desc = RichTextField(verbose_name=_('Review content'))
    rates = models.IntegerField(choices=RATES)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'reviewed by {self.user}'
