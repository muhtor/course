from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import reverse_lazy
from .models import User, BonusRate, AccountBalance, PhoneActivation, UserReferral


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone', 'ref', 'password', 'is_active', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].help_text = ("<a href=\"%s\"><strong>Change the Password</strong></a>."
                                             )% reverse_lazy('admin:auth_user_password_change', args=[self.instance.id])

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone', 'ref', 'is_active', 'is_staff', 'is_superuser', 'email')
    list_filter = ('is_superuser', 'is_active', 'is_staff',)
    fieldsets = (
        (None, {'fields': ('phone', 'ref', 'password', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('phone', 'ref', 'password1', 'password2'),}),
    )
    search_fields = ('phone',)
    ordering = ('phone',)
    filter_horizontal = ()


class PhoneActivationAdmin(admin.ModelAdmin):
    list_display = ('phone', 'user_id', 'user', 'code', 'activated')
    search_fields = ['user__phone', 'phone']


class BonusRateAdmin(admin.ModelAdmin):
    list_display = ('value', 'is_active')


class AccountBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'bonus', 'amount')


class UserReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referrer_code', 'called', 'is_referred', 'referred_users_count')


admin.site.register(User, UserAdmin)
admin.site.register(BonusRate, BonusRateAdmin)

admin.site.register(AccountBalance, AccountBalanceAdmin)
admin.site.register(UserReferral, UserReferralAdmin)
admin.site.register(PhoneActivation, PhoneActivationAdmin)
admin.site.unregister(Group)
