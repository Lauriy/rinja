from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from rinja import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stocks', views.all_stocks),
    url(r'^api/v1/', include('rinja.api.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
