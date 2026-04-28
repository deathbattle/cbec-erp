from django.apps import AppConfig

class OrderConfig(AppConfig):
    default_auto_field_type = 'django.db.models.BigAutoField'
    name = 'trade_api_server.order'
    verbose_name = '订单管理'
