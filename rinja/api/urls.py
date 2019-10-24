from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rinja.api.views import AllStocksViewset, WatchlistViewset

router = DefaultRouter()
router.register(r'stocks', AllStocksViewset, basename='StockScrapingResult')
router.register(r'stocks/follow', WatchlistViewset, basename='WatchlistEntry')

urlpatterns = [
    path('', include(router.urls)),
]
