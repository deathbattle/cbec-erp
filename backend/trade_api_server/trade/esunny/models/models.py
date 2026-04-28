import hashlib
import os

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from application import dispatch
from trade_api_server.utils.models import CoreModel, table_prefix, get_custom_app_models


class Users(CoreModel, AbstractUser):
    username = models.CharField(max_length=150, unique=True, db_index=True, verbose_name="用户账号",
                                help_text="用户账号")
    email = models.EmailField(max_length=255, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.CharField(max_length=255, verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    GENDER_CHOICES = (
        (0, "未知"),
        (1, "男"),
        (2, "女"),
    )
    gender = models.IntegerField(
        choices=GENDER_CHOICES, default=0, verbose_name="性别", null=True, blank=True, help_text="性别"
    )
    USER_TYPE = (
        (0, "后台用户"),
        (1, "前台用户"),
    )
    user_type = models.IntegerField(
        choices=USER_TYPE, default=0, verbose_name="用户类型", null=True, blank=True, help_text="用户类型"
    )
    post = models.ManyToManyField(to="Post", blank=True, verbose_name="关联岗位", db_constraint=False,
                                  help_text="关联岗位")
    role = models.ManyToManyField(to="Role", blank=True, verbose_name="关联角色", db_constraint=False,
                                  help_text="关联角色")
    dept = models.ForeignKey(
        to="Dept",
        verbose_name="所属部门",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="关联部门",
    )
    login_error_count = models.IntegerField(default=0, verbose_name="登录错误次数", help_text="登录错误次数")
    objects = CustomUserManager()

    def set_password(self, raw_password):
        super().set_password(hashlib.md5(raw_password.encode(encoding="UTF-8")).hexdigest())

    class Meta:
        db_table = table_prefix + "system_users"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class MessageCenterTargetUser(CoreModel):
    users = models.ForeignKey(Users, related_name="target_user", on_delete=models.CASCADE, db_constraint=False,
                              verbose_name="关联用户表", help_text="关联用户表")
    messagecenter = models.ForeignKey(MessageCenter, on_delete=models.CASCADE, db_constraint=False,
                                      verbose_name="关联消息中心表", help_text="关联消息中心表")
    is_read = models.BooleanField(default=False, blank=True, null=True, verbose_name="是否已读", help_text="是否已读")

    class Meta:
        db_table = table_prefix + "message_center_target_user"
        verbose_name = "消息中心目标用户表"
        verbose_name_plural = verbose_name
