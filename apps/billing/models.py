from django.db import models
from ..core.models import TimestampedModel
from ..accounts.models import User, AccountBalance
from django.utils.translation import ugettext_lazy as _

PAYCOM_STATUS = (
    (0, _("Инвойсе создан")),
    (1, _("Транзакция создан")),
    (2, _("Инвойсе оплачен")),
    (-1, _("Транзакция отменен")),
    (-2, _("Транзакция отменена после завершения"))
)

class CardStatusTypes(models.TextChoices):
    ACTIVE = "ACTIVE", "active"
    INACTIVE = "INACTIVE", "inactive"
    DELETED = "DELETED", "deleted"


class Card(TimestampedModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    holder_name = models.CharField(max_length=34, null=True, blank=True)
    brand = models.CharField(max_length=64, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    expire = models.CharField(null=True, blank=True, max_length=12)
    token = models.TextField()
    first6 = models.CharField(max_length=10, null=True, blank=True)
    last4 = models.CharField(max_length=10, null=True, blank=True)
    masked16 = models.CharField(max_length=16, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=8, null=True, blank=True)
    is_verify = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=CardStatusTypes.choices, default=CardStatusTypes.ACTIVE)

    def __str__(self):
        return "{} {}".format(self.brand, self.last4)


class Transaction(TimestampedModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True)
    transaction_id = models.CharField(max_length=255)
    order = models.ForeignKey('orders.Order', null=True, blank=True, on_delete=models.CASCADE)
    time_millisecond = models.CharField(max_length=255, blank=True, verbose_name="API kelgan millisecond vaqt")
    time_datetime = models.DateTimeField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True, verbose_name="Yaratilgan vaqti:")
    perform_time = models.DateTimeField(null=True, blank=True, verbose_name="Tasdiqlangan vaqti:")
    cancel_time = models.DateTimeField(null=True, blank=True)
    state = models.IntegerField(default=0, choices=PAYCOM_STATUS)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reason = models.CharField(max_length=300, verbose_name="Tranzaksiya sababi (izoh)", blank=True, null=True)
    error = models.TextField(default='None', max_length=255, blank=True, null=True)

    def __str__(self):
        return self.transaction_id


class BalanceTransaction(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    STATUS = ((1, "Created"), (2, "Done"),)
    status = models.IntegerField(choices=STATUS, default=1)

    def __str__(self):
        return f"{self.amount}"


class Voucher(TimestampedModel):
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    code = models.CharField(max_length=120)
    count = models.PositiveSmallIntegerField(default=0)
    is_unique = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    expiry_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

