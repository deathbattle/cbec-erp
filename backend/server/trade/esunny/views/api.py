import multiprocessing
import queue
import select
import subprocess
import sys
import hashlib
import logging
import platform
import io
import threading
import time

from django.contrib.auth.hashers import make_password, check_password
from django_restql.fields import DynamicSerializerMethodField
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import connection
from django.db.models import Q
from application import dispatch
from server.trade.esunny.settings import *
from server.system.models import Users, Role, Dept
from server.system.views.role import RoleSerializer
from server.utils.json_response import ErrorResponse, DetailResponse, SuccessResponse
from server.utils.serializers import CustomModelSerializer
from server.utils.validator import CustomUniqueValidator
from server.utils.viewset import CustomModelViewSet
from contextlib import contextmanager
from multiprocessing.connection import Connection
from ctypes import *

logger = logging.getLogger(__name__)

def singleeton_func(cls):
    instance={}
    def _singleton(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]
    return _singleton

@singleeton_func
class TradeLibLoader(object):
    def __init__(self):
        os_name = platform.system().lower()
        if os_name == "windows":
            self.loader = cdll.LoadLibrary(WIN_LIB_PATH)
        elif os_name == "linux":
            self.loader = cdll.LoadLibrary(LINUX_LIB_PATH)
    def get_loader(self):
        return self.loader

class DstarApiReqOrderInsertField(Structure):
    _fields_ = [("Direct", c_char),
                ("Offset", c_char),
                ("Hedge", c_char),
                ("OrderType", c_char),
                ("ValidType", c_char),
                ("SeatIndex", c_ubyte),
                ("AccountIndex", c_uint),
                ("ContractIndex", c_uint),
                ("ContractNo", c_char),
                ("OrderQty", c_uint),
                ("MinQty", c_uint),
                ("OrderPrice", c_double),
                ("ClientReqId", c_uint),
                ("Reference", c_longlong),
                ("UdpAuthCode", c_uint)]

class Capturing(list):

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self
        return self
    
    def __exit__(self, *args):
        sys.stdout = self._stdout

    def write(self, msg):
        self.append(msg)

    def flush(self):
        pass

class RedirectStdout:  #import os, sys, StringIO
    def __init__(self):
        self.content = ''
        self.savedStdout = sys.stdout
        self.memObj, self.fileObj, self.nulObj = None, None, None

    #外部的print语句将执行本write()方法，并由当前sys.stdout输出
    def write(self, outStr):
        #self.content.append(outStr)
        self.content += outStr

    def toCons(self):  #标准输出重定向至控制�?
        sys.stdout = self.savedStdout #sys.__stdout__

    def toMemo(self):  #标准输出重定向至内存
        self.memObj = io.StringIO()
        sys.stdout = self.memObj

    def toFile(self, file='out.txt'):  #标准输出重定向至文件
        self.fileObj = open(file, 'a+', 1) #改为行缓�?
        sys.stdout = self.fileObj
    
    def toMute(self):  #抑制输出
        self.nulObj = open(os.devnull, 'w')
        sys.stdout = self.nulObj
        
    def restore(self):
        self.content = ''
        if self.memObj.closed != True:
            self.memObj.close()
        if self.fileObj.closed != True:
            self.fileObj.close()
        if self.nulObj.closed != True:
            self.nulObj.close()
        sys.stdout = self.savedStdout #sys.__stdout__

class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
    def run(self):
        time.sleep(2)
        self.result = self.func(*self.args)
    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

class MyProcess(multiprocessing.Process):
    def __init__(self, func, args=()):
        super(multiprocessing.Process, self).__init__()
        self.func = func
        self.args = args
    def run(self):
        self.result = self.func(*self.args)
    def get_result(self):
        multiprocessing.Process.join(self)  # 等待进程执行完毕
        try:
            return self.result
        except Exception:
            return None

class CtypesStdoutCapture(object):
    def __enter__(self):
        self._pipe_out, self._pipe_in = os.pipe()
        self._err_pipe_out, self._err_pipe_in = os.pipe()
        self._stdout = os.dup(1)
        self._stderr = os.dup(2)
        self.text = ""
        self.err = ""
        # replace stdout with our write pipe
        os.dup2(self._pipe_in, 1)
        os.dup2(self._err_pipe_in, 2)
        self._stop = False
        self._read_thread = threading.Thread(target=self._read, args=["text", self._pipe_out])
        self._read_err_thread = threading.Thread(target=self._read, args=["err", self._err_pipe_out])
        self._read_thread.start()
        self._read_err_thread.start()
        return self

    def __exit__(self, *args):
        time.sleep(0.5)
        self._stop = True
        self._read_thread.join()
        self._read_err_thread.join()
        # put stdout back in place
        os.dup2(self._stdout, 1)
        os.dup2(self._stderr, 2)
        self.text += self.read_pipe(self._pipe_out)
        self.err += self.read_pipe(self._err_pipe_out)

    # check if we have more to read from the pipe
    def more_data(self, pipe):
        r, _, _ = select.select([pipe], [], [], 0)
        return bool(r)

    # read the whole pipe
    def read_pipe(self, pipe):
        out = ''
        while self.more_data(pipe):
            out += str(os.read(pipe, 1024).decode('utf-8'))

        return out

    def _read(self, type, pipe):
        while not self._stop:
            setattr(self, type, getattr(self, type) + self.read_pipe(pipe))
            time.sleep(0.001)

    def __str__(self):
        return self.text

@contextmanager
def RedirectStdout(newStdout):
    savedStdout, sys.stdout = sys.stdout, newStdout
    try:
        yield
    finally:
        sys.stdout = savedStdout

class OrderViewSet(CustomModelViewSet):
    """
    接口
    insert:报单
    """
    queryset = Users.objects.exclude(is_superuser=1).all()
    serializer_class = RoleSerializer
    # create_serializer_class = UserCreateSerializer
    # update_serializer_class = UserUpdateSerializer
    # filter_fields = ["name", "username", "gender", "is_active", "dept", "user_type"]
    # search_fields = ["username", "name", "dept__name", "role__name"]
    # # 导出
    # export_field_label = {
    #     "username": "用户账号",
    #     "name": "用户名称",
    #     "email": "用户邮箱",
    #     "mobile": "手机号码",
    #     "gender": "用户性别",
    #     "is_active": "帐号状�?,
    #     "last_login": "最后登录时�?,
    #     "dept_name": "部门名称",
    #     "dept_owner": "部门负责�?,
    # }
    # export_serializer_class = ExportUserProfileSerializer
    # # 导入
    # import_serializer_class = UserProfileImportSerializer
    # import_field_dict = {
    #     "username": "登录账号",
    #     "name": "用户名称",
    #     "email": "用户邮箱",
    #     "mobile": "手机号码",
    #     "gender": {
    #         "title": "用户性别",
    #         "choices": {
    #             "data": {"未知": 2, "�?: 1, "�?: 0},
    #         }
    #     },
    #     "is_active": {
    #         "title": "帐号状�?,
    #         "choices": {
    #             "data": {"启用": True, "禁用": False},
    #         }
    #     },
    #     "dept": {"title": "部门", "choices": {"queryset": Dept.objects.filter(status=True), "values_name": "name"}},
    #     "role": {"title": "角色", "choices": {"queryset": Role.objects.filter(status=True), "values_name": "name"}},
    # }


    @action(methods=["PUT"], detail=False, permission_classes=[])
    def insert(self, request):
        """易盛报单请求""" 
        res = 0
        try:
            "方法一（不能捕获动态库打印�?
            # with Capturing() as output:
            #     print('这是重定向后的输�?)
            #     trade_lib = load_trade_lib()
            #     trade_lib.TcpTestInit()
            #     trade_lib.InsertOrder.restype = c_int
            #     res = trade_lib.TcpInsertOrder()
            # print('Captured:', output)
            "方法�?
            # from contextlib import redirect_stdout
            # f = io.StringIO()
            # with redirect_stdout(f):
            #     print('这是重定向后的输�?)
            #     trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
            #     trade_lib.TcpTestInit()
            #     trade_lib.InsertOrder.restype = c_int
            #     res = trade_lib.TcpInsertOrder()
            "方法�?
            # with open('log.txt', "w+") as file:
            #     with RedirectStdout(file):
            #         print('这是重定向后的输�?)
            #         trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
            #         trade_lib.TcpTestInit()
            #         trade_lib.InsertOrder.restype = c_int
            #         res = trade_lib.TcpInsertOrder()
            # output = file.getvalue()
            # print('Got stdout:', output)
            "方法�?
            # pipe_out, pipe_in = os.pipe()
            # stdout = os.dup(1)
            # print("标准输出重定�?)
            # # 标准输出到文�?
            # os.dup2(pipe_in, 1)
            # def more_data():
            #         r, _, _ = select.select([pipe_out], [], [], 0)
            #         return bool(r)

            # # read the whole pipe
            # def read_pipe():
            #         out = ''
            #         while more_data():
            #                 out += str(os.read(pipe_out, 1024))

            #         return out
            # # print("pipe log")
            # print('这是重定向后的输�?)
            # trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
            # trade_lib.TcpTestInit()
            # trade_lib.InsertOrder.restype = c_int
            # res = trade_lib.TcpInsertOrder()
            # # 标准输出还原
            # output = read_pipe()
            # print("标准输出还原")
            # os.dup2(stdout, 1)
            # # os.close(pipe_in)
            # # print(output)
            # print('pipe out:', output)
            "方法�?
            # def test(stdout):
            #     sys.stdout = stdout
            #     trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
            #     trade_lib.TcpTestInit()
            #     trade_lib.InsertOrder.restype = c_int
            #     res = trade_lib.TcpInsertOrder()
            #     return res
            # pipe_out, pipe_in = os.pipe()
            # # stdout = os.dup(1)
            # print("标准输出重定�?)
            # # 标准输出到文�?
            # os.dup2(pipe_in, 1)
            # print('这是重定向后的输�?)
            # # stdout = sys.stdout
            # print("标准输出重定�?)
            # # 标准输出到文�?
            # os.dup2(pipe_in, 1)
            # print('这是重定向后的输�?)
            # th1 = MyThread(test, (stdout,))
            # th1.start()
            # th1.join()
            # res = th1.get_result()
            # # 标准输出还原
            # # os.dup2(stdout, 1)
            # sys.stdout = stdout
            # print("标准输出还原")

            # os.close(pipe_in)
            # r = os.fdopen(pipe_out)
            # # 输出重定向日�?
            # output = r.read()
            # r.close()
            # print('pipe out:', output)
            # "方法�?
            # def test(recv_conn: Connection, send_conn: Connection):
            #     # sys.stdout = send_conn
            #     stdout = os.dup(1)
            #     os.dup2(send_conn.fileno(), 1)
            #     # send_conn.send("Hello from the child process1!")
            #     # print("Hello from the child process2!")
            #     # os.dup2(recv_conn, 1)
            #     trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
            #     # trade_lib.TcpTestInit()
            #     # trade_lib.InsertOrder.restype = c_int
            #     # res = trade_lib.TcpInsertOrder()
            #     os.dup2(stdout, 1)
            #     return res
            # recv_conn, send_conn = multiprocessing.Pipe()
            # reader = os.fdopen(recv_conn.fileno(), 'r')
            # p1 = MyProcess(test, args=(recv_conn, send_conn))
            # p1.start()
            # # 输出重定向日�?
            # output = ""
            # # output = reader.readline()
            # # reader.close()
            # # sys.stdout.flush()
            # # while True:
            # p1.join()
            # if recv_conn.poll(timeout=2):
            #     # output = recv_conn.recv()
            #     output = reader.readline()

            # reader.close()
            # send_conn.close()
            # # recv_conn.close()
            # res = p1.get_result()
            # print('pipe out:', output)
            "方法�?
            # def test(trade_lib):
            #     trade_lib.TcpTestInit()
            #     trade_lib.InsertOrder.restype = c_int
            #     res = trade_lib.TcpInsertOrder()
            # # pipe_out, pipe_in = os.pipe()

            # # 获取当前标准输出文件描述�?
            # trade_lib = CDLL(LINUX_LIB_PATH)
            # orig_stdout = c_int.in_dll(cdll.LoadLibrary("libc.so.6"), "stdout")

            # # 创建一个新的文件描述符，用于重定向输出
            # new_stdout = open("tmp", "w+")
            # handler = new_stdout.fileno()
            # # 将stdout文件描述符改为新的文件描述符
            # dup2 = cdll.LoadLibrary("libc.so.6").dup
            # dup2(handler, orig_stdout)
            # # 调用C函数
            # trade_lib.TcpTestInit()
            # trade_lib.InsertOrder.restype = c_int
            # res = trade_lib.TcpInsertOrder()

            # output = new_stdout.read()
            # # 恢复标准输出
            # # os.dup2(orig_stdout.value, handler)
            
            # # 关闭新的文件描述符和库句�?
            # # os.close(pipe_in)
            # # r = os.fdopen(new_stdout)
            # # 输出重定向日�?
            # new_stdout.close()
            # lib = None
            # print(output)
            "方法�?成功)"
            res = ""
            with CtypesStdoutCapture() as capture:
                loader = TradeLibLoader().get_loader()
                # trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
                loader.TcpTestInit()
                loader.TcpInsertOrder.restype = c_int
                loader.TcpInsertOrder.argtypes = [c_char, c_char, c_char, c_char, c_char, c_ubyte, c_uint, c_char_p, c_uint, c_uint, c_double]
                direct = request.data.get('Direct', 'B').encode("utf-8")
                offset = request.data.get('Offset', 'O').encode("utf-8")
                hedge = request.data.get('Hedge', 'T').encode("utf-8")
                orderType = request.data.get('OrderType', '2').encode("utf-8")
                validType = request.data.get('ValidType', '3').encode("utf-8")
                seatIndex = request.data.get('SeatIndex', 1)
                contractIndex = request.data.get('ContractIndex', 33)
                contractNo = request.data.get('ContractNo', 'CF903').encode("utf-8")
                orderQty = request.data.get('OrderQty', 1)
                minQty = request.data.get('MinQty', 0)
                orderPrice = request.data.get('OrderPrice', 15000)
                res = loader.TcpInsertOrder(c_char(direct), c_char(offset), c_char(hedge), c_char(orderType), c_char(validType), c_ubyte(seatIndex), c_uint(contractIndex), c_char_p(contractNo), c_uint(orderQty), c_uint(minQty), c_double(orderPrice))
            output = capture.text
            logger.info("报单请求结果:\n" + output)
            if res == 0:
                ret = DetailResponse(data=None, msg="报单请求结果:\n" + output)
                # r.close()
                return ret
            else:
                ret = ErrorResponse(msg="报单请求结果:\n" + output)
                # r.close()
                return ret
        except Exception as e:
            logger.exception(e)
            return ErrorResponse(msg="报单请求失败:"+ str(e))
        finally:
            # sys.stdout = saved_stdout
            pass

    @action(methods=["DELTE"], detail=False, permission_classes=[])
    def delete(self, request):
        """易盛撤单请求""" 
        res = 0
        try:
            res = ""
            with CtypesStdoutCapture() as capture:
                loader = TradeLibLoader().get_loader()
                # trade_lib = cdll.LoadLibrary(LINUX_LIB_PATH)
                loader.TcpTestInit()
                loader.TcpDeleteOrder.restype = c_int
                loader.TcpDeleteOrder.argtypes = [ c_ubyte, c_longlong, c_char_p]
                seatIndex = request.data.get('SeatIndex', 0)
                orderId = request.data.get('OrderId', 33)
                systemNo = request.data.get('SystemNo', None).encode("utf-8")
                res = loader.TcpDeleteOrder( c_ubyte(seatIndex), c_longlong(orderId), c_char_p(systemNo))
            output = capture.text
            logger.info("撤单请求结果:\n" + output)
            if res == 0:
                ret = DetailResponse(data=None, msg="撤单请求成功:\n" + output)
                # r.close()
                return ret
            else:
                ret = ErrorResponse(msg="撤单请求失败:\n" + output)
                # r.close()
                return ret
        except Exception as e:
            logger.exception(e)
            return ErrorResponse(msg="撤单请求失败:"+ str(e))
        finally:
            # sys.stdout = saved_stdout
            pass
class UserInfoUpdateSerializer(CustomModelSerializer):
    """
    用户修改-序列化器
    """
    mobile = serializers.CharField(
        max_length=50,
        validators=[
            CustomUniqueValidator(queryset=Users.objects.all(), message="手机号必须唯一")
        ],
        allow_blank=True
    )

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = Users
        fields = ['email', 'mobile', 'avatar', 'name', 'gender']
        extra_kwargs = {
            "post": {"required": False, "read_only": True},
            "mobile": {"required": False},
        }

class OrderSerializer(CustomModelSerializer):
    """
    用户管理-序列化器
    """
    dept_name = serializers.CharField(source='dept.name', read_only=True)
    role_info = DynamicSerializerMethodField()
    dept_name_all = serializers.SerializerMethodField()

    class Meta:
        model = Users
        read_only_fields = ["id"]
        exclude = ["password"]
        extra_kwargs = {
            "post": {"required": False},
            "mobile": {"required": False},
        }

    def get_dept_name_all(self, instance):
        dept_name_all = recursion(instance.dept, "parent", "name")
        dept_name_all.reverse()
        return "/".join(dept_name_all)

    def get_role_info(self, instance, parsed_query):
        roles = instance.role.all()
        # You can do what ever you want in here
        # `parsed_query` param is passed to BookSerializer to allow further querying
        serializer = RoleSerializer(
            roles,
            many=True,
            parsed_query=parsed_query
        )
        return serializer.data
