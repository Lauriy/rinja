from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from rinja import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    path('stocks', views.all_stocks),
]
