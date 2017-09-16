from django import forms

from models import Captcha


class CaptchaAddForm(forms.ModelForm):
    class Meta:
        model = Captcha
        fields = ['md5', 'answer']