import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
import django
django.setup()
from server.system.models import Menu, MenuButton

# 获取TikTok订单菜单
tiktok_menu = Menu.objects.get(name='TikTok订单')
shangma_menu = Menu.objects.get(name='上马订单')

# TikTok订单按钮配置
tiktok_buttons = [
    {'name': '查询', 'value': 'tiktok_order:Search', 'api': '/api/order/tiktok/', 'method': 0},
    {'name': '详情', 'value': 'tiktok_order:Retrieve', 'api': '/api/order/tiktok/{id}/', 'method': 0},
    {'name': '新增', 'value': 'tiktok_order:Create', 'api': '/api/order/tiktok/', 'method': 1},
    {'name': '编辑', 'value': 'tiktok_order:Update', 'api': '/api/order/tiktok/{id}/', 'method': 2},
    {'name': '删除', 'value': 'tiktok_order:Delete', 'api': '/api/order/tiktok/{id}/', 'method': 3},
    {'name': '导出', 'value': 'tiktok_order:Export', 'api': '/api/order/tiktok/export_data/', 'method': 0},
    {'name': '导入', 'value': 'tiktok_order:Import', 'api': '/api/order/tiktok/import_data/', 'method': 1}
]

# 上马订单按钮配置
shangma_buttons = [
    {'name': '查询', 'value': 'shangma_order:Search', 'api': '/api/order/shangma/', 'method': 0},
    {'name': '详情', 'value': 'shangma_order:Retrieve', 'api': '/api/order/shangma/{id}/', 'method': 0},
    {'name': '新增', 'value': 'shangma_order:Create', 'api': '/api/order/shangma/', 'method': 1},
    {'name': '编辑', 'value': 'shangma_order:Update', 'api': '/api/order/shangma/{id}/', 'method': 2},
    {'name': '删除', 'value': 'shangma_order:Delete', 'api': '/api/order/shangma/{id}/', 'method': 3},
    {'name': '导出', 'value': 'shangma_order:Export', 'api': '/api/order/shangma/export_data/', 'method': 0},
    {'name': '导入', 'value': 'shangma_order:Import', 'api': '/api/order/shangma/import_data/', 'method': 1}
]

# 创建按钮
for btn in tiktok_buttons:
    MenuButton.objects.get_or_create(menu=tiktok_menu, value=btn['value'], defaults=btn)
    print(f'创建TikTok按钮: {btn["name"]}')

for btn in shangma_buttons:
    MenuButton.objects.get_or_create(menu=shangma_menu, value=btn['value'], defaults=btn)
    print(f'创建上马按钮: {btn["name"]}')

print('按钮权限创建完成！')
