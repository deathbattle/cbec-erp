from application.settings import BASE_DIR
import os

# 动态库路径
LINUX_LIB_PATH = os.path.join(BASE_DIR, "../trade_lib/esunny/lib/v10/linux/lib_test_api.so")
WIN_LIB_PATH = os.path.join(BASE_DIR, "..\\trade_lib\esunny\lib\\v10\windows\\lib_test_api.dll")