from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _
from ..core.models import TimestampedModel
from ..carts.models import Cart, CartCourse, Course
from ..accounts.models import User, AccountBalance
from .utils.order_services import unique_order_id_generator

PAYCOM_STATUS = (
    (0, _("Инвойсе создан")),
    (1, _("Транзакция создан")),
    (2, _("Инвойсе оплачен")),
    (-1, _("Транзакция отменен")),
    (-2, _("Транзакция отменена после завершения"))
)


class OrderCheckout(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkout_courses = models.ManyToManyField(Course, blank=True, through='CheckoutItem',
                                              related_name='checkout_courses')
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=3)
    paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _(' Order Checkout')
        verbose_name_plural = _(' Order Checkout')
        ordering = ['id']

    @property
    def all_items(self):
        return ",".join([str(c) for c in self.checkout_courses.all()])

    def __str__(self):
        return f"{self.user}"


class CheckoutItem(TimestampedModel):
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)
    checkout = models.ForeignKey(OrderCheckout, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Checkout item')
        verbose_name_plural = _('Checkout Items')
        ordering = ['id']

    def __str__(self):
        return f"Course Item: {self.course.name}"


class Order(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=15, blank=True)
    checkout = models.ForeignKey(OrderCheckout, related_name='checkout', on_delete=models.CASCADE)
    subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=3)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=3)
    STATUS = (('created', 'Created'), ('paid', 'Paid'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded'))
    payment_status = models.CharField(max_length=64, default="created", choices=STATUS)
    state = models.IntegerField(default=0, choices=PAYCOM_STATUS)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.order_id[:3]}-{self.order_id[3:7]}-{self.order_id[7:]}"

    # def payment_control(self):
    #     if self.state == 2 and self.payment_status == "paid":
    #         qs = OrderCheckout.objects.filter(pk=self.checkout.pk)
    #         if qs.exists():
    #             qs.update(paid=True, is_active=False)
    #             self.cart_product_control()
    #         return self.checkout
    #
    # def cart_product_control(self):
    #     products = self.checkout.checkout_courses.all()
    #     for product in products:
    #         qs = CartCourse.objects.filter(course_id=product.id)
    #         if qs.exists():
    #             qs.update(paid=True, insert_type="PAID")
    #     return True


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(user=instance.user)
    if qs.exists():
        qs.update(is_active=False)
pre_save.connect(pre_save_create_order_id, sender=Order)


def pre_save_checkout_order(sender, instance, *args, **kwargs):
    qs = OrderCheckout.objects.filter(user=instance.user, paid=False, is_active=True)
    if qs.exists():
        qs.delete()
pre_save.connect(pre_save_checkout_order, sender=OrderCheckout)
