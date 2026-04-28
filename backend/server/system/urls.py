from django.urls import path
from rest_framework import routers

from server.system.views.api_white_list import ApiWhiteListViewSet
from server.system.views.area import AreaViewSet
from server.system.views.clause import PrivacyView, TermsServiceView
from server.system.views.dept import DeptViewSet
from server.system.views.dictionary import DictionaryViewSet
from server.system.views.file_list import FileViewSet
from server.system.views.login_log import LoginLogViewSet
from server.system.views.menu import MenuViewSet
from server.system.views.menu_button import MenuButtonViewSet
from server.system.views.message_center import MessageCenterViewSet
from server.system.views.operation_log import OperationLogViewSet
from server.system.views.role import RoleViewSet
from server.system.views.role_menu import RoleMenuPermissionViewSet
from server.system.views.role_menu_button_permission import RoleMenuButtonPermissionViewSet
from server.system.views.system_config import SystemConfigViewSet
from server.system.views.user import UserViewSet
from server.system.views.menu_field import MenuFieldViewSet

system_url = routers.SimpleRouter()
system_url.register(r'menu', MenuViewSet)
system_url.register(r'menu_button', MenuButtonViewSet)
system_url.register(r'role', RoleViewSet)
system_url.register(r'dept', DeptViewSet)
system_url.register(r'user', UserViewSet)
system_url.register(r'operation_log', OperationLogViewSet)
system_url.register(r'dictionary', DictionaryViewSet)
system_url.register(r'area', AreaViewSet)
system_url.register(r'file', FileViewSet)
system_url.register(r'api_white_list', ApiWhiteListViewSet)
system_url.register(r'system_config', SystemConfigViewSet)
system_url.register(r'message_center', MessageCenterViewSet)
system_url.register(r'role_menu_button_permission', RoleMenuButtonPermissionViewSet)
system_url.register(r'role_menu_permission', RoleMenuPermissionViewSet)
system_url.register(r'column', MenuFieldViewSet)


urlpatterns = [
    path('user/export/', UserViewSet.as_view({'post': 'export_data', })),
    path('user/import/', UserViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('system_config/save_content/', SystemConfigViewSet.as_view({'put': 'save_content'})),
    path('system_config/get_association_table/', SystemConfigViewSet.as_view({'get': 'get_association_table'})),
    path('system_config/get_table_data/<int:pk>/', SystemConfigViewSet.as_view({'get': 'get_table_data'})),
    path('system_config/get_relation_info/', SystemConfigViewSet.as_view({'get': 'get_relation_info'})),
    path('login_log/', LoginLogViewSet.as_view({'get': 'list'})),
    path('login_log/<int:pk>/', LoginLogViewSet.as_view({'get': 'retrieve'})),
    path('dept_lazy_tree/', DeptViewSet.as_view({'get': 'dept_lazy_tree'})),
    path('clause/privacy.html', PrivacyView.as_view()),
    path('clause/terms_service.html', TermsServiceView.as_view()),
]
urlpatterns += system_url.urls
