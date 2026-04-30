import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
import django
django.setup()
from server.system.models import Role, MenuButton, RoleMenuButtonPermission

# 获取admin角色
admin_role = Role.objects.get(key='admin')

# 获取订单相关按钮
tiktok_buttons = MenuButton.objects.filter(menu__name='TikTok订单')
shangma_buttons = MenuButton.objects.filter(menu__name='上马订单')

# 为admin角色分配按钮权限
for btn in tiktok_buttons:
    RoleMenuButtonPermission.objects.get_or_create(role=admin_role, menu_button=btn, defaults={'data_range': 0})
    print(f'分配权限: {btn.name}')

for btn in shangma_buttons:
    RoleMenuButtonPermission.objects.get_or_create(role=admin_role, menu_button=btn, defaults={'data_range': 0})
    print(f'分配权限: {btn.name}')

print('权限分配完成！')
