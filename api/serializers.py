from rest_framework import serializers

from api.models import Captcha


class CaptchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Captcha
        fields = ('image', 'md5', 'answer')


class GuessCaptchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Captcha
        fields = ('pk', 'answer')
