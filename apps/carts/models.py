from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, m2m_changed
from django.utils.translation import gettext_lazy as _
from ..billing.models import User, Voucher
from ..core.models import TimestampedModel
from ..courses.models import Course, UserCourse, CertificatedCourse


class Cart(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, null=True, blank=True, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True, through='CartCourse', related_name='courses')
    subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=3)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"CART: {self.pk} / {self.user.phone}"

    @property
    def paid_courses(self):
        return ",".join([str(c) for c in self.courses.filter(cartcourse__insert_type="PAID")])

    @property
    def unpaid_courses(self):
        return ",".join([str(c) for c in self.courses.filter(cartcourse__insert_type="UNPAID")])

    @property
    def desire_courses(self):
        return ",".join([str(c) for c in self.courses.filter(cartcourse__insert_type="DESIRE")])


class CartCourse(TimestampedModel):
    class InsertType(models.TextChoices):
        UNPAID = "UNPAID", "unpaid"
        PAID = "PAID", "paid"
        DESIRE = "DESIRE", "desire"

    insert_type = models.CharField(max_length=30, choices=InsertType.choices, default=InsertType.UNPAID)
    quantity = models.PositiveSmallIntegerField(default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    certificated_course = models.ForeignKey(
        CertificatedCourse,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    paid = models.BooleanField(default=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Cart Course')
        verbose_name_plural = _('     Cart Courses')
        ordering = ['id']

    def __str__(self):
        return f"{self.course.name} / ID: {self.pk} Quantity: {self.quantity}"

    @property
    def course_price(self):
        return f"{self.course.price}"


def pre_save_create_cart(sender, instance, *args, **kwargs):
    if instance.user is not None:
        qs = Cart.objects.filter(user=instance.user, is_active=True)
        if qs.exists():
            qs.update(is_active=False)
pre_save.connect(pre_save_create_cart, sender=Cart)
