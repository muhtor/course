from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from .managers import PhoneActivationManager
from ..core.utils.eskiz_api.api import SendSMSApi
from ..accounts.utils.generators import generate_phone_code, generate_unique_referral_token
from ..core.models import TimestampedModel


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_superuser=False, email=None):
        if not phone:
            raise ValueError('Users must have an phone number')

        user = self.model(phone=phone, email=email)
        user.set_password(password)
        user.is_superuser = is_superuser

        if password is None:
            # For social login (facebook, instagram). Password isn't required
            user.is_active = True
        user.save()
        return user

    def create_staffuser(self, phone, password):
        if not password:
            raise ValueError('staff/admins must have a password.')
        user = self.create_user(phone, password=password)
        user.is_staff = True
        user.save()
        return user

    def create_superuser(self, phone, password):
        if not password:
            raise ValueError('superusers must have a password.')
        user = self.create_user(phone, password=password, is_superuser=True)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, TimestampedModel):
    phone = models.CharField(max_length=20, unique=True, db_index=True)
    ref = models.CharField(max_length=50, blank=True, help_text="This field is created automatically")
    email = models.EmailField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []  # email and password required by default

    objects = UserManager()

    def __str__(self):
        return f"{self.phone}"

    def get_short_name(self):
        if not self.password:
            return self.email or 'Unknown user'
        return self.phone

    def has_perm(self, perm, obj=None):
        return True  # does user have a specific permision, simple answer - yes

    def has_module_perms(self, app_label):
        return True  # does user have permission to view the app 'app_label'?

    def get_full_name(self):
        return self.profile.get_full_name()


class BonusRate(TimestampedModel):
    value = models.DecimalField(max_digits=8, decimal_places=1, default=1000)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.value}"


class AccountBalance(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bonus = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.amount}"


class UserReferral(TimestampedModel):
    referrer = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Referrer: ⇢ ',  related_name='referrer')
    called = models.ForeignKey(
        User, verbose_name="Called By", null=True, blank=True, on_delete=models.CASCADE, related_name='called')
    is_referred = models.BooleanField(default=False)
    referred_users = models.ManyToManyField(User, verbose_name='Referred: ⇠ ', related_name='referred_users', blank=True)

    def referrer_code(self):
        return self.referrer.ref

    def referred_users_count(self):
        count = self.referred_users.all().count()
        return f"Count: {count}"

    def __str__(self):
        return self.referrer.phone


class PhoneActivation(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=120)
    code = models.CharField(max_length=10, blank=True, help_text="This field is created automatically")
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)  # 7 Days
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PhoneActivationManager()

    def __str__(self):
        return self.phone

    def activate(self):
        user = self.user
        user.is_active = True
        user.save()
        # post activation signal for user
        self.activated = True
        self.save()
        if not user.is_active:
            user.is_active = True
            user.save()
        return True

    def send_activation_sms(self, resend: bool = False):
        code = generate_phone_code()
        SendSMSApi().send_user_sms(msg=f'Sizga Aristotel saytidan kelgan kod: {code}', phone=self.phone)
        if resend:
            if not self.forced_expired:
                self.code = code
                self.save()
                return True
                # return self.code
        else:
            if self.code and not self.activated and not self.forced_expired:
                return True
            else:
                return False


def pre_save_phone_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.code:
            instance.code = generate_phone_code()
pre_save.connect(pre_save_phone_activation, sender=PhoneActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.ref = generate_unique_referral_token(instance)
        obj = PhoneActivation.objects.create(user=instance, phone=instance.phone)
        UserReferral.objects.create(referrer=instance)
        AccountBalance.objects.create(user=instance)
        phone = instance.phone[1:]
        if phone.isnumeric():
            obj.send_activation_sms()
        instance.save()
post_save.connect(post_save_user_create_receiver, sender=User)


def pre_save_bonus_rate(sender, instance, *args, **kwargs):
    if instance is not None:
        qs = BonusRate.objects.filter(is_active=True)
        if qs.exists():
            qs.update(is_active=False)
pre_save.connect(pre_save_bonus_rate, sender=BonusRate)


