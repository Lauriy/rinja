from django.conf.urls import url

from rinja.api.views import AllStocksViewset

urlpatterns = [
    url(r'^stocks', AllStocksViewset.as_view({'get': 'list'}), name='api-list-all-stocks'),
]