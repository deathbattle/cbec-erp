from datetime import timedelta, datetime
from django.db.models import Prefetch
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from server.order.models import (
    TiktokOrder, TiktokOrderItem, TiktokOrderInfluencer, TiktokOrderCommission,
    ShangmaOrder
)
from server.utils.json_response import SuccessResponse, DetailResponse
from server.utils.serializers import CustomModelSerializer
from server.utils.viewset import CustomModelViewSet

# 导入同步服务
try:
    from server.order.tiktok_sync_service import TiktokSyncService
    SYNC_SERVICE_AVAILABLE = True
except ImportError:
    SYNC_SERVICE_AVAILABLE = False


class TiktokOrderItemSerializer(CustomModelSerializer):
    """
    TikTok订单项序列化器
    """
    class Meta:
        model = TiktokOrderItem
        fields = ["product_id", "product_name", "sku_id", "product_price", "order_quantity"]

class TiktokOrderInfluencerSerializer(CustomModelSerializer):
    """
    TikTok订单达人序列化器
    """
    class Meta:
        model = TiktokOrderInfluencer
        fields = ["influencer_username", "content_type", "content_id"]

class TiktokOrderCommissionSerializer(CustomModelSerializer):
    """
    TikTok订单佣金序列化器
    """
    class Meta:
        model = TiktokOrderCommission
        fields = [
            "commission_model", "standard_commission_rate", "estimated_commission_amount",
            "estimated_standard_commission", "actual_commission_amount", "actual_commission",
            "store_ad_commission_rate", "estimated_store_ad_commission", "actual_store_ad_commission",
            "estimated_joint_influencer_bonus", "actual_joint_influencer_bonus"
        ]

class TiktokOrderAggregateSerializer(CustomModelSerializer):
    """
    TikTok订单聚合序列化器 - 保持前端显示不变
    """
    product_id = serializers.CharField(source='item.product_id', allow_null=True, required=False)
    product_name = serializers.CharField(source='item.product_name', allow_null=True, required=False)
    sku_id = serializers.CharField(source='item.sku_id', allow_null=True, required=False)
    product_price = serializers.DecimalField(source='item.product_price', max_digits=18, decimal_places=2, allow_null=True, required=False)
    order_quantity = serializers.IntegerField(source='item.order_quantity', allow_null=True, required=False)
    
    influencer_username = serializers.CharField(source='influencer.influencer_username', allow_null=True, required=False)
    content_type = serializers.CharField(source='influencer.content_type', allow_null=True, required=False)
    content_id = serializers.CharField(source='influencer.content_id', allow_null=True, required=False)
    
    commission_model = serializers.CharField(source='commission.commission_model', allow_null=True, required=False)
    standard_commission_rate = serializers.DecimalField(source='commission.standard_commission_rate', max_digits=10, decimal_places=4, allow_null=True, required=False)
    estimated_commission_amount = serializers.DecimalField(source='commission.estimated_commission_amount', max_digits=18, decimal_places=2, allow_null=True, required=False)
    estimated_standard_commission = serializers.DecimalField(source='commission.estimated_standard_commission', max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_commission_amount = serializers.DecimalField(source='commission.actual_commission_amount', max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_commission = serializers.DecimalField(source='commission.actual_commission', max_digits=18, decimal_places=2, allow_null=True, required=False)
    store_ad_commission_rate = serializers.DecimalField(source='commission.store_ad_commission_rate', max_digits=10, decimal_places=4, allow_null=True, required=False)
    estimated_store_ad_commission = serializers.DecimalField(source='commission.estimated_store_ad_commission', max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_store_ad_commission = serializers.DecimalField(source='commission.actual_store_ad_commission', max_digits=18, decimal_places=2, allow_null=True, required=False)
    estimated_joint_influencer_bonus = serializers.DecimalField(source='commission.estimated_joint_influencer_bonus', max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_joint_influencer_bonus = serializers.DecimalField(source='commission.actual_joint_influencer_bonus', max_digits=18, decimal_places=2, allow_null=True, required=False)

    class Meta:
        model = TiktokOrder
        fields = [
            "id", "order_id", "payment_amount", "currency_unit", "is_refunded",
            "payment_method", "order_status", "create_time", "payment_time",
            "delivery_time", "commission_settlement_time", "platform",
            "product_id", "product_name", "sku_id", "product_price", "order_quantity",
            "influencer_username", "content_type", "content_id",
            "commission_model", "standard_commission_rate", "estimated_commission_amount",
            "estimated_standard_commission", "actual_commission_amount", "actual_commission",
            "store_ad_commission_rate", "estimated_store_ad_commission", "actual_store_ad_commission",
            "estimated_joint_influencer_bonus", "actual_joint_influencer_bonus"
        ]
        read_only_fields = ["id"]


class TiktokOrderCreateUpdateSerializer(CustomModelSerializer):
    """
    TikTok订单创建/更新序列化器 - 接收前端格式数据
    """
    id = serializers.IntegerField(allow_null=True, required=False)
    # 商品信息
    product_id = serializers.CharField(allow_null=True, required=False)
    product_name = serializers.CharField(allow_null=True, required=False)
    sku_id = serializers.CharField(allow_null=True, required=False)
    product_price = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    order_quantity = serializers.IntegerField(allow_null=True, required=False)
    
    # 达人信息
    influencer_username = serializers.CharField(allow_null=True, required=False)
    content_type = serializers.CharField(allow_null=True, required=False)
    content_id = serializers.CharField(allow_null=True, required=False)
    
    # 佣金信息
    commission_model = serializers.CharField(allow_null=True, required=False)
    standard_commission_rate = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True, required=False)
    estimated_commission_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    estimated_standard_commission = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_commission_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_commission = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    store_ad_commission_rate = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True, required=False)
    estimated_store_ad_commission = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_store_ad_commission = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    estimated_joint_influencer_bonus = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)
    actual_joint_influencer_bonus = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True, required=False)

    class Meta:
        model = TiktokOrder
        fields = [
            "id", "order_id", "payment_amount", "currency_unit", "is_refunded",
            "payment_method", "order_status", "create_time", "payment_time",
            "delivery_time", "commission_settlement_time", "platform",
            "product_id", "product_name", "sku_id", "product_price", "order_quantity",
            "influencer_username", "content_type", "content_id",
            "commission_model", "standard_commission_rate", "estimated_commission_amount",
            "estimated_standard_commission", "actual_commission_amount", "actual_commission",
            "store_ad_commission_rate", "estimated_store_ad_commission", "actual_store_ad_commission",
            "estimated_joint_influencer_bonus", "actual_joint_influencer_bonus"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        # 提取关联数据
        item_data = {
            'product_id': validated_data.pop('product_id', None),
            'product_name': validated_data.pop('product_name', None),
            'sku_id': validated_data.pop('sku_id', None),
            'product_price': validated_data.pop('product_price', None),
            'order_quantity': validated_data.pop('order_quantity', None),
        }
        influencer_data = {
            'influencer_username': validated_data.pop('influencer_username', None),
            'content_type': validated_data.pop('content_type', None),
            'content_id': validated_data.pop('content_id', None),
        }
        commission_data = {
            'commission_model': validated_data.pop('commission_model', None),
            'standard_commission_rate': validated_data.pop('standard_commission_rate', None),
            'estimated_commission_amount': validated_data.pop('estimated_commission_amount', None),
            'estimated_standard_commission': validated_data.pop('estimated_standard_commission', None),
            'actual_commission_amount': validated_data.pop('actual_commission_amount', None),
            'actual_commission': validated_data.pop('actual_commission', None),
            'store_ad_commission_rate': validated_data.pop('store_ad_commission_rate', None),
            'estimated_store_ad_commission': validated_data.pop('estimated_store_ad_commission', None),
            'actual_store_ad_commission': validated_data.pop('actual_store_ad_commission', None),
            'estimated_joint_influencer_bonus': validated_data.pop('estimated_joint_influencer_bonus', None),
            'actual_joint_influencer_bonus': validated_data.pop('actual_joint_influencer_bonus', None),
        }
        
        # 创建主订单
        order = TiktokOrder.objects.create(**validated_data)
        
        # 创建订单项
        if any(item_data.values()):
            TiktokOrderItem.objects.create(order=order, **item_data)
        
        # 创建达人信息
        if any(influencer_data.values()):
            TiktokOrderInfluencer.objects.create(order=order, **influencer_data)
        
        # 创建佣金信息
        if any(commission_data.values()):
            TiktokOrderCommission.objects.create(order=order, **commission_data)
        
        return order

    def update(self, instance, validated_data):
        # 提取关联数据
        item_data = {
            'product_id': validated_data.pop('product_id', None),
            'product_name': validated_data.pop('product_name', None),
            'sku_id': validated_data.pop('sku_id', None),
            'product_price': validated_data.pop('product_price', None),
            'order_quantity': validated_data.pop('order_quantity', None),
        }
        influencer_data = {
            'influencer_username': validated_data.pop('influencer_username', None),
            'content_type': validated_data.pop('content_type', None),
            'content_id': validated_data.pop('content_id', None),
        }
        commission_data = {
            'commission_model': validated_data.pop('commission_model', None),
            'standard_commission_rate': validated_data.pop('standard_commission_rate', None),
            'estimated_commission_amount': validated_data.pop('estimated_commission_amount', None),
            'estimated_standard_commission': validated_data.pop('estimated_standard_commission', None),
            'actual_commission_amount': validated_data.pop('actual_commission_amount', None),
            'actual_commission': validated_data.pop('actual_commission', None),
            'store_ad_commission_rate': validated_data.pop('store_ad_commission_rate', None),
            'estimated_store_ad_commission': validated_data.pop('estimated_store_ad_commission', None),
            'actual_store_ad_commission': validated_data.pop('actual_store_ad_commission', None),
            'estimated_joint_influencer_bonus': validated_data.pop('estimated_joint_influencer_bonus', None),
            'actual_joint_influencer_bonus': validated_data.pop('actual_joint_influencer_bonus', None),
        }
        
        # 更新主订单字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新或创建订单项（过滤掉 None 值，只更新有实际数据的字段）
        filtered_item_data = {k: v for k, v in item_data.items() if v is not None}
        if filtered_item_data:
            item, created = TiktokOrderItem.objects.update_or_create(
                order=instance,
                defaults=filtered_item_data
            )
        
        # 更新或创建达人信息（过滤掉 None 值，只更新有实际数据的字段）
        filtered_influencer_data = {k: v for k, v in influencer_data.items() if v is not None}
        if filtered_influencer_data:
            influencer, created = TiktokOrderInfluencer.objects.update_or_create(
                order=instance,
                defaults=filtered_influencer_data
            )
        
        # 更新或创建佣金信息（过滤掉 None 值，只更新有实际数据的字段）
        filtered_commission_data = {k: v for k, v in commission_data.items() if v is not None}
        if filtered_commission_data:
            commission, created = TiktokOrderCommission.objects.update_or_create(
                order=instance,
                defaults=filtered_commission_data
            )
        
        return instance


class TiktokOrderViewSet(CustomModelViewSet):
    """
    TikTok订单接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = TiktokOrder.objects.prefetch_related('tiktokorderitem_set', 'tiktokorderinfluencer_set', 'tiktokordercommission_set')
    serializer_class = TiktokOrderAggregateSerializer
    create_serializer_class = TiktokOrderCreateUpdateSerializer
    update_serializer_class = TiktokOrderCreateUpdateSerializer
    export_serializer_class = TiktokOrderAggregateSerializer
    filter_fields = [
        "order_id", "payment_method", "order_status", "platform"
    ]
    search_fields = [
        "order_id"
    ]
    export_field_label = {
        "order_id": "订单 ID",
        "product_id": "商品 ID",
        "product_name": "商品名称",
        "sku_id": "SKU ID",
        "product_price": "商品价格",
        "payment_amount": "支付金额",
        "currency_unit": "货币单位",
        "order_quantity": "下单件数",
        "is_refunded": "已全部退货或全额退款",
        "payment_method": "付款方式",
        "order_status": "订单状态",
        "influencer_username": "达人用户名",
        "content_type": "内容形式",
        "content_id": "内容ID",
        "commission_model": "commission model",
        "standard_commission_rate": "标准佣金率",
        "estimated_commission_amount": "预估计佣金额",
        "estimated_standard_commission": "预计标准佣金付款",
        "actual_commission_amount": "实际计佣金额",
        "actual_commission": "实际佣金",
        "store_ad_commission_rate": "店铺广告佣金率",
        "estimated_store_ad_commission": "预计店铺广告佣金付款",
        "actual_store_ad_commission": "实际店铺广告佣金付款",
        "estimated_joint_influencer_bonus": "预估合资达人奖金",
        "actual_joint_influencer_bonus": "实际合资达人奖金",
        "create_time": "创建时间",
        "payment_time": "支付时间",
        "delivery_time": "订单送达时间",
        "commission_settlement_time": "佣金结算时间",
        "platform": "平台",
    }
    import_serializer_class = TiktokOrderCreateUpdateSerializer
    import_field_dict = {
        "order_id": "订单 ID",
        "product_id": "商品 ID",
        "product_name": "商品名称",
        "sku_id": "SKU ID",
        "product_price": "商品价格",
        "payment_amount": "支付金额",
        "currency_unit": "货币单位",
        "order_quantity": "下单件数",
        "is_refunded": {"title": "已全部退货或全额退款", "choices": {"data": {"是": True, "否": False}}},
        "payment_method": "付款方式",
        "order_status": "订单状态",
        "influencer_username": "达人用户名",
        "content_type": "内容形式",
        "content_id": "内容ID",
        "commission_model": "commission model",
        "standard_commission_rate": "标准佣金率",
        "estimated_commission_amount": "预估计佣金额",
        "estimated_standard_commission": "预计标准佣金付款",
        "actual_commission_amount": "实际计佣金额",
        "actual_commission": "实际佣金",
        "store_ad_commission_rate": "店铺广告佣金率",
        "estimated_store_ad_commission": "预计店铺广告佣金付款",
        "actual_store_ad_commission": "实际店铺广告佣金付款",
        "estimated_joint_influencer_bonus": "预估合资达人奖金",
        "actual_joint_influencer_bonus": "实际合资达人奖金",
        "create_time": {"title": "创建时间", "type": "datetime"},
        "payment_time": {"title": "支付时间", "type": "datetime"},
        "delivery_time": {"title": "订单送达时间", "type": "datetime"},
        "commission_settlement_time": {"title": "佣金结算时间", "type": "datetime"},
        "platform": "平台",
    }

    def get_queryset(self):
        """
        重写查询集，预加载关联数据
        """
        return TiktokOrder.objects.prefetch_related(
            Prefetch('tiktokorderitem_set', queryset=TiktokOrderItem.objects.all(), to_attr='item_list'),
            Prefetch('tiktokorderinfluencer_set', queryset=TiktokOrderInfluencer.objects.all(), to_attr='influencer_list'),
            Prefetch('tiktokordercommission_set', queryset=TiktokOrderCommission.objects.all(), to_attr='commission_list')
        ).all()

    def create(self, request, *args, **kwargs):
        """
        创建订单，同时创建关联的订单项、达人信息和佣金信息
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 使用 serializer.save() 创建订单（关联数据在 serializer.create 中处理）
        order = serializer.save()
        
        return DetailResponse(data=TiktokOrderAggregateSerializer(order).data)

    def update(self, request, *args, **kwargs):
        """
        更新订单，同时更新关联数据
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 更新主订单
        instance.payment_amount = request.data.get('payment_amount', instance.payment_amount)
        instance.currency_unit = request.data.get('currency_unit', instance.currency_unit)
        instance.is_refunded = request.data.get('is_refunded', instance.is_refunded)
        instance.payment_method = request.data.get('payment_method', instance.payment_method)
        instance.order_status = request.data.get('order_status', instance.order_status)
        instance.create_time = make_naive_datetime(request.data.get('create_time', instance.create_time))
        instance.payment_time = make_naive_datetime(request.data.get('payment_time', instance.payment_time))
        instance.delivery_time = make_naive_datetime(request.data.get('delivery_time', instance.delivery_time))
        instance.commission_settlement_time = make_naive_datetime(request.data.get('commission_settlement_time', instance.commission_settlement_time))
        instance.platform = request.data.get('platform', instance.platform)
        instance.save()
        
        # 更新或创建订单项
        item_data = {
            'product_id': request.data.get('product_id'),
            'product_name': request.data.get('product_name'),
            'sku_id': request.data.get('sku_id'),
            'product_price': request.data.get('product_price'),
            'order_quantity': request.data.get('order_quantity'),
        }
        item, _ = TiktokOrderItem.objects.get_or_create(order=instance)
        for key, value in item_data.items():
            if value is not None:
                setattr(item, key, value)
        item.save()
        
        # 更新或创建达人信息
        influencer_data = {
            'influencer_username': request.data.get('influencer_username'),
            'content_type': request.data.get('content_type'),
            'content_id': request.data.get('content_id'),
        }
        influencer, _ = TiktokOrderInfluencer.objects.get_or_create(order=instance)
        for key, value in influencer_data.items():
            if value is not None:
                setattr(influencer, key, value)
        influencer.save()
        
        # 更新或创建佣金信息
        commission_data = {
            'commission_model': request.data.get('commission_model'),
            'standard_commission_rate': request.data.get('standard_commission_rate'),
            'estimated_commission_amount': request.data.get('estimated_commission_amount'),
            'estimated_standard_commission': request.data.get('estimated_standard_commission'),
            'actual_commission_amount': request.data.get('actual_commission_amount'),
            'actual_commission': request.data.get('actual_commission'),
            'store_ad_commission_rate': request.data.get('store_ad_commission_rate'),
            'estimated_store_ad_commission': request.data.get('estimated_store_ad_commission'),
            'actual_store_ad_commission': request.data.get('actual_store_ad_commission'),
            'estimated_joint_influencer_bonus': request.data.get('estimated_joint_influencer_bonus'),
            'actual_joint_influencer_bonus': request.data.get('actual_joint_influencer_bonus'),
        }
        commission, _ = TiktokOrderCommission.objects.get_or_create(order=instance)
        for key, value in commission_data.items():
            if value is not None:
                setattr(commission, key, value)
        commission.save()
        
        return DetailResponse(data=TiktokOrderAggregateSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        """
        删除订单，同时删除关联数据
        """
        instance = self.get_object()
        # 删除关联数据
        TiktokOrderItem.objects.filter(order=instance).delete()
        TiktokOrderInfluencer.objects.filter(order=instance).delete()
        TiktokOrderCommission.objects.filter(order=instance).delete()
        # 删除主订单
        instance.delete()
        return SuccessResponse(msg="删除成功")

    @action(methods=["POST"], detail=False)
    def import_data(self, request):
        """
        导入TikTok订单数据，先清理关联表中指向不存在主表记录的数据
        
        请求参数:
        - url: Excel文件URL
        
        返回:
        - message: 导入结果信息
        """
        # 清理关联表中孤立的数据（外键指向不存在的主表记录）
        existing_order_ids = set(TiktokOrder.objects.values_list('id', flat=True))
        
        # 清理订单项中孤立的数据
        orphan_items = TiktokOrderItem.objects.exclude(order_id__in=existing_order_ids)
        orphan_item_count = orphan_items.count()
        if orphan_item_count > 0:
            orphan_items.delete()
        
        # 清理达人信息中孤立的数据
        orphan_influencers = TiktokOrderInfluencer.objects.exclude(order_id__in=existing_order_ids)
        orphan_influencer_count = orphan_influencers.count()
        if orphan_influencer_count > 0:
            orphan_influencers.delete()
        
        # 清理佣金信息中孤立的数据
        orphan_commissions = TiktokOrderCommission.objects.exclude(order_id__in=existing_order_ids)
        orphan_commission_count = orphan_commissions.count()
        if orphan_commission_count > 0:
            orphan_commissions.delete()
        
        # 调用父类的导入方法
        response = super().import_data(request)
        
        # 如果有清理过数据，在返回信息中添加提示
        if orphan_item_count > 0 or orphan_influencer_count > 0 or orphan_commission_count > 0:
            original_msg = response.data.get('msg', '')
            response.data['msg'] = f"{original_msg}（已清理孤立关联数据：订单项{orphan_item_count}条，达人信息{orphan_influencer_count}条，佣金信息{orphan_commission_count}条）"
        
        return response

    @action(methods=["POST"], detail=False)
    def batch_delete(self, request):
        """
        批量删除TikTok订单
        
        请求参数:
        - ids: 订单ID数组
        
        返回:
        - success: 是否成功
        - message: 提示信息
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'success': False, 'message': '请选择要删除的订单'},
                status=status.HTTP_BAD_REQUEST
            )
        
        try:
            # 删除关联数据
            TiktokOrderItem.objects.filter(order_id__in=ids).delete()
            TiktokOrderInfluencer.objects.filter(order_id__in=ids).delete()
            TiktokOrderCommission.objects.filter(order_id__in=ids).delete()
            # 删除主订单
            TiktokOrder.objects.filter(id__in=ids).delete()
            
            return SuccessResponse(msg=f"成功删除{len(ids)}条订单")
        
        except Exception as e:
            return Response(
                {'success': False, 'message': f'批量删除失败: {str(e)}'},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )

    @action(methods=["POST"], detail=False)
    def sync(self, request):
        """
        手动触发TikTok订单同步
        
        请求参数:
        - start_time: 开始时间 (可选, 格式: YYYY-MM-DD HH:MM:SS)
        - end_time: 结束时间 (可选, 格式: YYYY-MM-DD HH:MM:SS)
        - days: 最近天数 (可选, 与start_time/end_time互斥)
        
        返回:
        - success: 是否成功
        - total_fetched: 获取的订单总数
        - total_created: 新增订单数
        - total_updated: 更新订单数
        - message: 提示信息
        """
        if not SYNC_SERVICE_AVAILABLE:
            return Response(
                {'success': False, 'message': '同步服务不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            sync_service = TiktokSyncService()
            
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')
            days = request.data.get('days', 7)
            
            # 如果指定了days参数，则同步最近N天的数据
            if days and not start_time:
                result = sync_service.sync_recent_orders(days)
            else:
                result = sync_service.sync_orders(start_time, end_time)
            
            return SuccessResponse(data=result, msg=result.get('message'))
        
        except Exception as e:
            import traceback
            error_msg = f"同步失败: {str(e)}\n{traceback.format_exc()}"
            return Response(
                {'success': False, 'message': error_msg},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )

    @action(methods=["GET"], detail=False)
    def sync_status(self, request):
        """
        获取TikTok订单同步状态
        
        返回:
        - total_orders: 订单总数
        - last_sync_time: 最后同步时间
        - sync_enabled: 是否启用同步
        """
        if not SYNC_SERVICE_AVAILABLE:
            return Response(
                {'sync_enabled': False, 'message': '同步服务不可用'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            sync_service = TiktokSyncService()
            status_info = sync_service.get_sync_status()
            return SuccessResponse(data=status_info)
        
        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )


class ShangmaOrderSerializer(CustomModelSerializer):
    """
    上马订单序列化器
    """
    class Meta:
        model = ShangmaOrder
        fields = "__all__"
        read_only_fields = ["id"]


class ShangmaOrderCreateSerializer(CustomModelSerializer):
    """
    上马订单新增序列化器
    """
    class Meta:
        model = ShangmaOrder
        fields = "__all__"
        read_only_fields = ["id"]


class ShangmaOrderUpdateSerializer(CustomModelSerializer):
    """
    上马订单更新序列化器
    """
    class Meta:
        model = ShangmaOrder
        fields = "__all__"
        read_only_fields = ["id"]


class ShangmaOrderViewSet(CustomModelViewSet):
    """
    上马订单接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = ShangmaOrder.objects.all()
    serializer_class = ShangmaOrderSerializer
    create_serializer_class = ShangmaOrderCreateSerializer
    update_serializer_class = ShangmaOrderUpdateSerializer
    filter_fields = [
        "tenant_id", "category", "shop_id", "shop_name", "order_no",
        "third_order_no", "third_order_status", "payment_method",
        "logistics_no", "logistics_name", "replace_type", "order_status"
    ]
    search_fields = [
        "order_no", "third_order_no", "shop_name", "logistics_no"
    ]
    export_field_label = {
        "tenant_id": "租户ID",
        "category": "分类",
        "shop_id": "店铺ID",
        "shop_name": "店铺名称",
        "order_no": "订单号",
        "third_order_no": "第三方订单号",
        "third_order_time": "第三方订单时间",
        "third_order_status": "第三方订单状态",
        "payment_method": "支付方式",
        "logistics_no": "物流单号",
        "logistics_name": "物流公司名称",
        "replace_type": "换货类型",
        "order_amount": "订单金额",
        "order_income_amount": "订单收入金额",
        "goods_amount": "商品金额",
        "buyer_paid_shipping_fee": "买家支付运费",
        "platform_shipping_discount": "平台运费优惠",
        "third_shipping_discount": "第三方运费优惠",
        "seller_shipping_discount": "卖家运费优惠",
        "actual_shipping_fee": "实际运费",
        "final_shipping_fee": "最终运费",
        "voucher_from_platform": "平台优惠券",
        "voucher_from_seller": "卖家优惠券",
        "commission_fee": "佣金费用",
        "service_fee": "服务费用",
        "other_fee": "其他费用",
        "purchase_amount": "采购金额",
        "order_shipped_time": "订单发货时间",
        "order_completed_time": "订单完成时间",
        "order_status": "订单状态",
        "warehouse_id": "仓库ID",
        "order_profit": "订单利润",
        "shipping_difference": "运费差额",
    }
    import_serializer_class = ShangmaOrderCreateSerializer
    import_field_dict = {
        "tenant_id": "租户ID",
        "category": "分类",
        "shop_id": "店铺ID",
        "shop_name": "店铺名称",
        "order_no": "订单号",
        "third_order_no": "第三方订单号",
        "third_order_time": "第三方订单时间",
        "third_order_status": "第三方订单状态",
        "payment_method": "支付方式",
        "logistics_no": "物流单号",
        "logistics_name": "物流公司名称",
        "replace_type": "换货类型",
        "order_amount": "订单金额",
        "order_income_amount": "订单收入金额",
        "goods_amount": "商品金额",
        "buyer_paid_shipping_fee": "买家支付运费",
        "platform_shipping_discount": "平台运费优惠",
        "third_shipping_discount": "第三方运费优惠",
        "seller_shipping_discount": "卖家运费优惠",
        "actual_shipping_fee": "实际运费",
        "final_shipping_fee": "最终运费",
        "voucher_from_platform": "平台优惠券",
        "voucher_from_seller": "卖家优惠券",
        "commission_fee": "佣金费用",
        "service_fee": "服务费用",
        "other_fee": "其他费用",
        "purchase_amount": "采购金额",
        "order_shipped_time": "订单发货时间",
        "order_completed_time": "订单完成时间",
        "order_status": "订单状态",
        "warehouse_id": "仓库ID",
        "order_profit": "订单利润",
        "shipping_difference": "运费差额",
    }

    @action(methods=["POST"], detail=False)
    def batch_delete(self, request):
        """
        批量删除上马订单
        
        请求参数:
        - ids: 订单ID数组
        
        返回:
        - success: 是否成功
        - message: 提示信息
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'success': False, 'message': '请选择要删除的订单'},
                status=status.HTTP_BAD_REQUEST
            )
        
        try:
            ShangmaOrder.objects.filter(id__in=ids).delete()
            return SuccessResponse(msg=f"成功删除{len(ids)}条订单")
        
        except Exception as e:
            return Response(
                {'success': False, 'message': f'批量删除失败: {str(e)}'},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )


class OrderStatisticsViewSet(viewsets.ViewSet):
    """
    订单统计接口
    """

    @action(methods=["GET"], detail=False)
    def tiktok_statistics(self, request):
        """TikTok订单统计"""
        total = TiktokOrder.objects.count()
        total_amount = TiktokOrder.objects.aggregate(total=models.Sum('payment_amount'))['total'] or 0
        status_counts = TiktokOrder.objects.values('order_status').annotate(count=models.Count('id'))
        
        commission = []
        for status in status_counts:
            status_orders = TiktokOrder.objects.filter(order_status=status['order_status'])
            # 通过关联表获取佣金总和
            status_order_ids = list(status_orders.values_list('id', flat=True))
            total_commission = TiktokOrderCommission.objects.filter(
                order_id__in=status_order_ids
            ).aggregate(sum=models.Sum('actual_commission'))['sum'] or 0
            commission.append({
                'status': status['order_status'],
                'count': status['count'],
                'amount': float(total_commission)
            })
        
        return SuccessResponse(data={
            'total': total,
            'total_amount': float(total_amount),
            'commission': commission
        })

    @action(methods=["GET"], detail=False)
    def shangma_statistics(self, request):
        """上马订单统计"""
        total = ShangmaOrder.objects.count()
        total_amount = ShangmaOrder.objects.aggregate(total=models.Sum('order_amount'))['total'] or 0
        status_counts = ShangmaOrder.objects.values('order_status').annotate(count=models.Count('id'))
        
        profit = []
        for status in status_counts:
            status_orders = ShangmaOrder.objects.filter(order_status=status['order_status'])
            total_profit = status_orders.aggregate(sum=models.Sum('order_profit'))['sum'] or 0
            profit.append({
                'status': status['order_status'],
                'count': status['count'],
                'profit': float(total_profit)
            })
        
        return SuccessResponse(data={
            'total': total,
            'total_amount': float(total_amount),
            'profit': profit
        })

    @action(methods=["GET"], detail=False)
    def trend(self, request):
        """订单趋势统计"""
        days = int(request.query_params.get('days', 7))
        today = timezone.now().date()
        
        dates = []
        tiktok_counts = []
        shangma_counts = []
        
        for i in range(days-1, -1, -1):
            date = today - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            tiktok_count = TiktokOrder.objects.filter(create_time__date=date).count()
            tiktok_counts.append(tiktok_count)
            
            shangma_count = ShangmaOrder.objects.filter(create_time__date=date).count()
            shangma_counts.append(shangma_count)
        
        return SuccessResponse(data={
            'dates': dates,
            'tiktok': tiktok_counts,
            'shangma': shangma_counts
        })

    @action(methods=["GET"], detail=False)
    def summary(self, request):
        """订单汇总统计"""
        tiktok_total = TiktokOrder.objects.count()
        shangma_total = ShangmaOrder.objects.count()
        tiktok_amount = TiktokOrder.objects.aggregate(total=models.Sum('payment_amount'))['total'] or 0
        shangma_amount = ShangmaOrder.objects.aggregate(total=models.Sum('order_amount'))['total'] or 0
        
        return SuccessResponse(data={
            'tiktok_total': tiktok_total,
            'shangma_total': shangma_total,
            'tiktok_amount': float(tiktok_amount),
            'shangma_amount': float(shangma_amount)
        })


# ================================================= #
# ****************** TikTok OAuth 授权视图 ***************** #
# ================================================= #

class TiktokOAuthViewSet(viewsets.ViewSet):
    """
    TikTok OAuth 授权接口
    """
    
    def _get_client(self):
        """获取 TikTok API 客户端"""
        from server.order.tiktok_api_client import TiktokApiClient
        return TiktokApiClient()
    
    @action(methods=["GET"], detail=False)
    def get_auth_url(self, request):
        """
        获取授权链接
        
        返回:
        - auth_url: 授权链接
        - state: 状态参数（用于防止 CSRF）
        
        使用示例:
        GET /api/order/tiktok/oauth/get_auth_url/
        
        前端跳转到 auth_url 进行授权
        """
        import uuid
        state = str(uuid.uuid4())
        
        try:
            client = self._get_client()
            auth_url = client.get_authorization_url(state=state)
            
            return SuccessResponse(data={
                'auth_url': auth_url,
                'state': state
            })
        
        except Exception as e:
            return Response(
                {'success': False, 'message': f'获取授权链接失败: {str(e)}'},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )
    
    @action(methods=["GET"], detail=False)
    def callback(self, request):
        """
        授权回调处理
        
        请求参数:
        - code: 授权码
        - state: 状态参数
        
        返回:
        - success: 是否成功
        - access_token: 访问令牌
        - refresh_token: 刷新令牌
        - shop_id: 店铺ID
        - shop_cipher: 跨境店需要的 shop_cipher
        - message: 提示信息
        
        使用示例:
        GET /api/order/tiktok/oauth/callback/?code=xxx&state=yyy
        """
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        
        if not code:
            return Response(
                {'success': False, 'message': '缺少授权码(code)'},
                status=status.HTTP_BAD_REQUEST
            )
        
        try:
            client = self._get_client()
            
            # 使用授权码换取 access_token
            result = client.get_access_token(code=code)
            
            if result.get('code') == 0:
                data = result.get('data', {})
                
                return SuccessResponse(data={
                    'success': True,
                    'access_token': data.get('access_token'),
                    'refresh_token': data.get('refresh_token'),
                    'expires_in': data.get('expires_in'),
                    'shop_id': data.get('shop_id'),
                    'shop_cipher': data.get('shop_cipher'),
                    'message': '授权成功'
                })
            else:
                return Response(
                    {'success': False, 'message': result.get('message', '授权失败')},
                    status=status.HTTP_BAD_REQUEST
                )
        
        except Exception as e:
            import traceback
            error_msg = f'授权回调处理失败: {str(e)}\n{traceback.format_exc()}'
            return Response(
                {'success': False, 'message': error_msg},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )
    
    @action(methods=["POST"], detail=False)
    def refresh_token(self, request):
        """
        刷新 access_token
        
        请求参数:
        - refresh_token: 刷新令牌
        
        返回:
        - success: 是否成功
        - access_token: 新的访问令牌
        - refresh_token: 新的刷新令牌
        - expires_in: 有效期（秒）
        - message: 提示信息
        
        使用示例:
        POST /api/order/tiktok/oauth/refresh_token/
        {
            "refresh_token": "your_refresh_token"
        }
        """
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'success': False, 'message': '缺少 refresh_token'},
                status=status.HTTP_BAD_REQUEST
            )
        
        try:
            client = self._get_client()
            result = client.refresh_access_token(refresh_token=refresh_token)
            
            if result.get('code') == 0:
                data = result.get('data', {})
                
                return SuccessResponse(data={
                    'success': True,
                    'access_token': data.get('access_token'),
                    'refresh_token': data.get('refresh_token'),
                    'expires_in': data.get('expires_in'),
                    'message': 'Token 刷新成功'
                })
            else:
                return Response(
                    {'success': False, 'message': result.get('message', 'Token 刷新失败')},
                    status=status.HTTP_BAD_REQUEST
                )
        
        except Exception as e:
            import traceback
            error_msg = f'Token 刷新失败: {str(e)}\n{traceback.format_exc()}'
            return Response(
                {'success': False, 'message': error_msg},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )
    
    @action(methods=["POST"], detail=False)
    def get_shops(self, request):
        """
        获取授权的店铺列表（推荐方式）
        
        请求参数:
        - access_token: 访问令牌（可选，未提供则使用配置中的 token）
        
        返回:
        - success: 是否成功
        - shops: 店铺列表
        - message: 提示信息
        
        使用示例:
        POST /api/order/tiktok/oauth/get_shops/
        {
            "access_token": "your_access_token"
        }
        """
        access_token = request.data.get('access_token')
        
        try:
            client = self._get_client()
            
            if access_token:
                client.set_credentials(access_token=access_token, shop_id='')
            
            result = client.get_authorized_shops()
            
            if result.get('code') == 0:
                data = result.get('data', {})
                
                return SuccessResponse(data={
                    'success': True,
                    'shops': data.get('shops', []),
                    'message': '获取店铺列表成功'
                })
            else:
                return Response(
                    {'success': False, 'message': result.get('message', '获取店铺列表失败')},
                    status=status.HTTP_BAD_REQUEST
                )
        
        except Exception as e:
            import traceback
            error_msg = f'获取店铺列表失败: {str(e)}\n{traceback.format_exc()}'
            return Response(
                {'success': False, 'message': error_msg},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )
    
    @action(methods=["POST"], detail=False)
    def save_credentials(self, request):
        """
        保存 TikTok 凭证配置
        
        请求参数:
        - access_token: 访问令牌
        - refresh_token: 刷新令牌
        - shop_id: 店铺ID
        - shop_cipher: 跨境店需要的 shop_cipher（可选）
        
        返回:
        - success: 是否成功
        - message: 提示信息
        
        使用示例:
        POST /api/order/tiktok/oauth/save_credentials/
        {
            "access_token": "your_access_token",
            "refresh_token": "your_refresh_token",
            "shop_id": "your_shop_id",
            "shop_cipher": "your_shop_cipher"
        }
        """
        from server.order.models import TiktokSyncConfig
        
        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')
        shop_id = request.data.get('shop_id')
        shop_cipher = request.data.get('shop_cipher')
        
        if not access_token or not shop_id:
            return Response(
                {'success': False, 'message': '缺少必要参数（access_token 和 shop_id 为必填）'},
                status=status.HTTP_BAD_REQUEST
            )
        
        try:
            # 获取或创建配置
            config, created = TiktokSyncConfig.objects.get_or_create(id=1)
            
            # 更新配置
            config.access_token = access_token
            config.refresh_token = refresh_token
            config.shop_id = shop_id
            config.shop_cipher = shop_cipher
            config.save()
            
            return SuccessResponse(data={
                'success': True,
                'message': '凭证配置保存成功'
            })
        
        except Exception as e:
            import traceback
            error_msg = f'保存凭证配置失败: {str(e)}\n{traceback.format_exc()}'
            return Response(
                {'success': False, 'message': error_msg},
                status=status.HTTP_INTERNAL_SERVER_ERROR
            )
