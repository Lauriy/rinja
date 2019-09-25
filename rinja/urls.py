from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from rinja import views
from rinja.views import ProfileEditView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.all_stocks, name='home'),
    url(r'^watchlist/', views.all_stocks, name='watchlist'),
    url(r'^api/v1/', include('rinja.api.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/', ProfileEditView.as_view(), name='account_profile'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
