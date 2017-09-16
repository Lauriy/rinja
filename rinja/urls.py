from django.conf.urls import url
from django.contrib import admin

from rinja.views import CaptchaCreate, HomeView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^captcha/add', CaptchaCreate.as_view(), name='captcha_add'),
    url(r'^admin/', admin.site.urls),
]
