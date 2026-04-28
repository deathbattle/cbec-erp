import base64
import hashlib
import logging
from datetime import datetime, timedelta
from captcha.views import CaptchaStore, captcha_image
from django.contrib import auth
from django.contrib.auth import login
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from application import dispatch
from trade_api_server.system.models import Users
from trade_api_server.utils.json_response import ErrorResponse, DetailResponse
from trade_api_server.utils.request_util import save_login_log
from trade_api_server.utils.serializers import CustomModelSerializer
from trade_api_server.utils.validator import CustomValidationError

logger = logging.getLogger(__name__)

class CaptchaView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        responses={"200": openapi.Response("获取成功")},
        security=[],
        operation_id="captcha-get",
        operation_description="验证码获取",
    )
    def get(self, request):
        data = {}
        if dispatch.get_system_config_values("base.captcha_state"):
            hashkey = CaptchaStore.generate_key()
            id = CaptchaStore.objects.filter(hashkey=hashkey).first().id
            imgage = captcha_image(request, hashkey)
            # 将图片转换为base64
            image_base = base64.b64encode(imgage.content)
            data = {
                "key": id,
                "image_base": "data:image/png;base64," + image_base.decode("utf-8"),
            }
        return DetailResponse(data=data)


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """
    captcha = serializers.CharField(
        max_length=6, required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {"no_active_account": _("账号/密码错误")}

    def validate(self, attrs):
        captcha = self.initial_data.get("captcha", None)
        if dispatch.get_system_config_values("base.captcha_state"):
            if captcha is None:
                raise CustomValidationError("验证码不能为空")
            self.image_code = CaptchaStore.objects.filter(
                id=self.initial_data["captchaKey"]
            ).first()
            five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if self.image_code and five_minute_ago > self.image_code.expiration:
                self.image_code and self.image_code.delete()
                raise CustomValidationError("验证码过期")
            else:
                if self.image_code and (
                    self.image_code.response == captcha
                    or self.image_code.challenge == captcha
                ):
                    self.image_code and self.image_code.delete()
                else:
                    self.image_code and self.image_code.delete()
                    raise CustomValidationError("图片验证码错误")

        user = Users.objects.get(username=attrs['username'])
        if not user.is_active:
            raise CustomValidationError("账号已被锁定,联系管理员解锁")
        try:
            data = super().validate(attrs)
            data["name"] = self.user.name
            data["userId"] = self.user.id
            data["avatar"] = self.user.avatar
            data['user_type'] = self.user.user_type
            dept = getattr(self.user, 'dept', None)
            if dept:
                data['dept_info'] = {
                    'dept_id': dept.id,
                    'dept_name': dept.name,

                }
            role = getattr(self.user, 'role', None)
            if role:
                data['role_info'] = role.values('id', 'name', 'key')
            request = self.context.get("request")
            request.user = self.user
            # 记录登录日志
            save_login_log(request=request)
            user.login_error_count = 0
            user.save()
            return {"code": 2000, "msg": "请求成功", "data": data}
        except Exception as e:
            user.login_error_count += 1
            if user.login_error_count >= 5:
                user.is_active = False
                raise CustomValidationError("账号已被锁定,联系管理员解锁")
            user.save()
            count = 5 - user.login_error_count
            raise CustomValidationError(f"账号/密码错误;重试{count}次后将被锁定~")


class LoginView(TokenObtainPairView):
    """
    登录接口
    """
    serializer_class = LoginSerializer
    permission_classes = []

    # def post(self, request, *args, **kwargs):
    #     # username可能携带的不止是用户名，可能还是用户的其它唯一标识 手机号 邮箱
    #     username = request.data.get('username',None)
    #     if username is None:
    #         return ErrorResponse(msg="参数错误")
    #     password = request.data.get('password',None)
    #     if password is None:
    #         return ErrorResponse(msg="参数错误")
    #     captcha = request.data.get('captcha',None)
    #     if captcha is None:
    #         return ErrorResponse(msg="参数错误")
    #     captchaKey = request.data.get('captchaKey',None)
    #     if captchaKey is None:
    #         return ErrorResponse(msg="参数错误")
    #     if dispatch.get_system_config_values("base.captcha_state"):
    #         if captcha is None:
    #             raise CustomValidationError("验证码不能为空")
    #         self.image_code = CaptchaStore.objects.filter(
    #             id=captchaKey
    #         ).first()
    #         five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
    #         if self.image_code and five_minute_ago > self.image_code.expiration:
    #             self.image_code and self.image_code.delete()
    #             raise CustomValidationError("验证码过期")
    #         else:
    #             if self.image_code and (
    #                     self.image_code.response == captcha
    #                     or self.image_code.challenge == captcha
    #             ):
    #                 self.image_code and self.image_code.delete()
    #             else:
    #                 self.image_code and self.image_code.delete()
    #                 raise CustomValidationError("图片验证码错误")
    #     try:
    #         # 手动通过 user 签发 jwt-token
    #         user = Users.objects.get(username=username)
    #     except:
    #         return DetailResponse(msg='该账号未注册')
    #     # 获得用户后，校验密码并签发token
    #     print(make_password(password),user.password)
    #     if check_password(make_password(password),user.password):
    #         return DetailResponse(msg='密码错误')
    #     result = {
    #        "name":user.name,
    #         "userId":user.id,
    #         "avatar":user.avatar,
    #     }
    #     dept = getattr(user, 'dept', None)
    #     if dept:
    #         result['dept_info'] = {
    #             'dept_id': dept.id,
    #             'dept_name': dept.name,
    #             'dept_key': dept.key
    #         }
    #     role = getattr(user, 'role', None)
    #     if role:
    #         result['role_info'] = role.values('id', 'name', 'key')
    #     refresh = LoginSerializer.get_token(user)
    #     result["refresh"] = str(refresh)
    #     result["access"] = str(refresh.access_token)
    #     # 记录登录日志
    #     request.user = user
    #     save_login_log(request=request)
    #     return DetailResponse(data=result,msg="获取成功")


class LoginTokenSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    """

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {"no_active_account": _("账号/密码不正确")}

    def validate(self, attrs):
        if not getattr(settings, "LOGIN_NO_CAPTCHA_AUTH", False):
            return {"code": 4000, "msg": "该接口暂未开通!", "data": None}
        data = super().validate(attrs)
        data["name"] = self.user.name
        data["userId"] = self.user.id
        return {"code": 2000, "msg": "请求成功", "data": data}


class LoginTokenView(TokenObtainPairView):
    """
    登录获取token接口
    """

    serializer_class = LoginTokenSerializer
    permission_classes = []


class LogoutView(APIView):
    def post(self, request):
        logger.debug("注销成功")
        return DetailResponse(msg="注销成功")


class ApiLoginSerializer(CustomModelSerializer):
    """接口文档登录-序列化器"""

    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = Users
        fields = ["username", "password"]


class ApiLogin(APIView):
    """接口文档的登录接口"""

    serializer_class = ApiLoginSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user_obj = auth.authenticate(
            request,
            username=username,
            password=hashlib.md5(password.encode(encoding="UTF-8")).hexdigest(),
        )
        if user_obj:
            login(request, user_obj)
            return redirect("/")
        else:
            return ErrorResponse(msg="账号/密码错误")
