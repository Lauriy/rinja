from django.conf.urls import url

from api.views import RetrieveCaptcha, GuessCaptcha

urlpatterns = [
    url(r'^retrieve-captcha', RetrieveCaptcha.as_view(), name='api-retrieve-captcha'),
    url(r'^guess-captcha/(?P<pk>\d+)', GuessCaptcha.as_view(), name='api-guess-captcha')
]
