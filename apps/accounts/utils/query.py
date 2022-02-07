from ..models import User, BonusRate, AccountBalance, UserReferral
from ...profiles.models import Notification


class Query:

    _model = None

    def _get_object(self, *args, **kwargs):
        # print("*...", args, type(args))
        # print("**...", kwargs, type(kwargs))
        try:
            return self._model.objects.get(*args, **kwargs)
        except self._model.DoesNotExist:
            return None

    def _get_queryset(self, *args, **kwargs):
        try:
            return self._model.objects.filter(*args, **kwargs)
        except self._model.DoesNotExist:
            return None

    def get_or_none(self, Klass, qs: bool = False, *args, **kwargs):
        self._model = Klass
        if qs:
            return self._get_queryset(*args, **kwargs)
        return self._get_object(*args, **kwargs)

    def save_referred_users(self, user, key):
        """
        :param user: referred User 1
        :param key: referrer User 2
        :return: boolean True / None
        """
        called = self.get_or_none(Klass=User, ref=key)
        print("called.....", called, type(called))
        if key and called:
            referrer = self.get_or_none(Klass=UserReferral, referrer__ref__exact=key)
            referred = self.get_or_none(Klass=UserReferral, qs=True, referrer__phone=user.phone)
            # print("referrer.....", referrer, type(referrer))
            # print("referred.....", referred, type(referred))
            if referrer and referred.exists():
                referred.update(called=called, is_referred=True)
                referrer.referred_users.add(user.pk)
                Notification.objects.create(
                    profile=referrer.refferer.profile,
                    title="Sizning promo-kodingiz orqali yangi foydalanuvchi"
                          "ro'yhattadan o'tdi. Sizga 2 ball qoshildi."
                )
                return True
        return None

    @staticmethod
    def create_or_get_bonus_rate():
        qs = BonusRate.objects.filter(is_active=True)
        if qs.exists():
            return qs.first()
        rate = BonusRate.objects.create(value=1000)
        return rate

    def update_user_balance(self, user):
        is_success = False
        current_user = self.get_or_none(Klass=UserReferral, referrer=user)
        rate = self.create_or_get_bonus_rate()
        if current_user:
            called_user = current_user.called
            if current_user.is_referred and called_user:
                called_user_balance = self.get_or_none(Klass=AccountBalance, user=called_user)
                if called_user_balance:
                    bonus = called_user_balance.bonus + 2
                    called_user_balance.amount = bonus * rate.value
                    called_user_balance.bonus = bonus
                    called_user_balance.save()
                    is_success = True
        current_user_balance = self.get_or_none(Klass=AccountBalance, user=user)
        if current_user_balance:
            bonus = current_user_balance.bonus + 1
            current_user_balance.amount = bonus * rate.value
            current_user_balance.bonus = bonus
            current_user_balance.save()
            is_success = True
        return is_success


