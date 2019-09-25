from django.conf.urls import url

from rinja.api.views import AllStocksViewset, SubscriptionViewset

urlpatterns = [
    url(r'^stocks/', AllStocksViewset.as_view({'get': 'list'}), name='api-list-all-stocks'),
    url(r'^stocks/follow/(?P<pk>[-\w]+)/', SubscriptionViewset.as_view({'post': 'update'}),
        name='api-toggle-followed-stock'),

]
