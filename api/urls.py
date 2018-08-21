from django.conf.urls import url

from api.views import RetrieveCaptcha, GuessCaptcha, ListCaptcha

urlpatterns = [
    url(r'^list-retrieved-captchas', ListCaptcha.as_view(), name='api-list-captcha'),
    url(r'^retrieve-captcha', RetrieveCaptcha.as_view(), name='api-retrieve-captcha'),
    url(r'^guess-captcha/(?P<pk>\d+)', GuessCaptcha.as_view(), name='api-guess-captcha')
]
