from django.urls import path
from rest_framework import routers
from trade_api_server.order.views import TiktokOrderViewSet, ShangmaOrderViewSet, OrderStatisticsViewSet

order_url = routers.SimpleRouter()
order_url.register(r'tiktok', TiktokOrderViewSet)
order_url.register(r'shangma', ShangmaOrderViewSet)
order_url.register(r'statistics', OrderStatisticsViewSet, basename='statistics')

urlpatterns = [
    path('tiktok/export/', TiktokOrderViewSet.as_view({'post': 'export_data', })),
    path('tiktok/import/', TiktokOrderViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('shangma/export/', ShangmaOrderViewSet.as_view({'post': 'export_data', })),
    path('shangma/import/', ShangmaOrderViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('tiktok/statistics/', OrderStatisticsViewSet.as_view({'get': 'tiktok_statistics'})),
    path('shangma/statistics/', OrderStatisticsViewSet.as_view({'get': 'shangma_statistics'})),
    path('trend/', OrderStatisticsViewSet.as_view({'get': 'trend'})),
    path('summary/', OrderStatisticsViewSet.as_view({'get': 'summary'})),
]
urlpatterns += order_url.urls
