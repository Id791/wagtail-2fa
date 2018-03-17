from django import forms
from django.utils.translation import ugettext_lazy as _

from django_otp.forms import OTPAuthenticationFormMixin
from django_otp.plugins.otp_totp.models import TOTPDevice


class TokenForm(OTPAuthenticationFormMixin, forms.Form):
    otp_token = forms.CharField(required=True)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.fields['otp_token'].widget.attrs.update({
            'autofocus': 'autofocus',
            'autocomplete': 'off',
        })

    def clean(self):
        self.clean_otp(self.user)
        return self.cleaned_data


class DeviceForm(forms.ModelForm):
    otp_token = forms.CharField(required=True)

    class Meta:
        model = TOTPDevice
        fields = ['name', 'otp_token']

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.fields['otp_token'].widget.attrs.update({
            'autofocus': 'autofocus',
            'autocomplete': 'off',
        })

        self.fields['name'].initial = _("Default two factor code")
        if self.instance.confirmed:
            del self.fields['otp_token']

        self.user = user

    def clean_otp_token(self):
        token = self.cleaned_data.get('otp_token')

        if token and self.instance.verify_token(token):
            return token

        raise forms.ValidationError(
            _('Invalid token. Please make sure you have entered it correctly.'),
            code='invalid')

    def save(self):
        self.instance.confirmed = True
        self.instance.save()
