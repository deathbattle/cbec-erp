# -*- coding: utf-8 -*-

"""
@author: 猿小�?@contact: QQ:1638245306
@Created on: 2021/5/31 031 22:08
@Remark: 公共基础model�?"""
from importlib import import_module

from django.apps import apps
from django.db import models
from django.conf import settings

from application import settings

table_prefix = settings.TABLE_PREFIX  # 数据库表名前缀


class SoftDeleteQuerySet(models.QuerySet):
    pass


class SoftDeleteManager(models.Manager):
    """支持软删�?""

    def __init__(self, *args, **kwargs):
        self.__add_is_del_filter = False
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        # 考虑是否主动传入is_deleted
        if not kwargs.get('is_deleted') is None:
            self.__add_is_del_filter = True
        return super(SoftDeleteManager, self).filter(*args, **kwargs)

    def get_queryset(self):
        if self.__add_is_del_filter:
            return SoftDeleteQuerySet(self.model, using=self._db).exclude(is_deleted=False)
        return SoftDeleteQuerySet(self.model).exclude(is_deleted=True)

    def get_by_natural_key(self, name):
        return SoftDeleteQuerySet(self.model).get(username=name)


class SoftDeleteModel(models.Model):
    """
    软删除模�?    一旦继�?就将开启软删除
    """
    is_deleted = models.BooleanField(verbose_name="是否软删�?, help_text='是否软删�?, default=False, db_index=True)
    objects = SoftDeleteManager()

    class Meta:
        abstract = True
        verbose_name = '软删除模�?
        verbose_name_plural = verbose_name

    def delete(self, using=None, soft_delete=True, *args, **kwargs):
        """
        重写删除方法,直接开启软删除
        """
        self.is_deleted = True
        self.save(using=using)


class CoreModel(models.Model):
    """
    核心标准抽象模型模型,可直接继承使�?    增加审计字段, 覆盖字段�? 字段名称请勿修改, 必须统一审计字段名称
    """
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    description = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='creator_query', null=True,
                                verbose_name='创建�?, help_text="创建�?, on_delete=models.SET_NULL,
                                db_constraint=False)
    modifier = models.CharField(max_length=255, null=True, blank=True, help_text="修改�?, verbose_name="修改�?)
    dept_belong_id = models.CharField(max_length=255, help_text="数据归属部门", null=True, blank=True,
                                      verbose_name="数据归属部门")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间",
                                           verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间")

    class Meta:
        abstract = True
        verbose_name = '核心模型'
        verbose_name_plural = verbose_name


def get_all_models_objects(model_name=None):
    """
    获取所�?models 对象
    :return: {}
    """
    settings.ALL_MODELS_OBJECTS = {}
    if not settings.ALL_MODELS_OBJECTS:
        all_models = apps.get_models()
        for item in list(all_models):
            table = {
                "tableName": item._meta.verbose_name,
                "table": item.__name__,
                "tableFields": []
            }
            for field in item._meta.fields:
                fields = {
                    "title": field.verbose_name,
                    "field": field.name
                }
                table['tableFields'].append(fields)
            settings.ALL_MODELS_OBJECTS.setdefault(item.__name__, {"table": table, "object": item})
    if model_name:
        return settings.ALL_MODELS_OBJECTS[model_name] or {}
    return settings.ALL_MODELS_OBJECTS or {}


def get_model_from_app(app_name):
    """获取模型里的字段"""
    model_module = import_module(app_name + '.models')
    filter_model = [
        getattr(model_module, item) for item in dir(model_module)
        if item != 'CoreModel' and issubclass(getattr(model_module, item).__class__, models.base.ModelBase)
    ]
    model_list = []
    for model in filter_model:
        if model.__name__ == 'AbstractUser':
            continue
        fields = [
            {'title': field.verbose_name, 'name': field.name, 'object': field}
            for field in model._meta.fields
        ]
        model_list.append({
            'app': app_name,
            'verbose': model._meta.verbose_name,
            'model': model.__name__,
            'object': model,
            'fields': fields
        })
    return model_list


def get_custom_app_models(app_name=None):
    """
    获取所有项目下的app里的models
    """
    if app_name:
        return get_model_from_app(app_name)
    all_apps = apps.get_app_configs()
    res = []
    for app in all_apps:
        if app.name.startswith('django'):
            continue
        if app.name in settings.COLUMN_EXCLUDE_APPS:
            continue
        try:
            all_models = get_model_from_app(app.name)
            if all_models:
                for model in all_models:
                    res.append(model)
        except Exception as e:
            pass
    return res
