from django.db import models
from server.utils.models import CoreModel, table_prefix


class TiktokOrder(CoreModel):
    """
    TikTok订单主表 - 订单基本信息
    """
    order_id = models.CharField(max_length=64, verbose_name="订单ID", help_text="订单ID", db_index=True)
    payment_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="支付金额", help_text="支付金额", null=True, blank=True)
    currency_unit = models.CharField(max_length=10, verbose_name="货币单位", help_text="货币单位", null=True, blank=True)
    is_refunded = models.BooleanField(default=False, verbose_name="已全部退货或全额退款", help_text="已全部退货或全额退款")
    payment_method = models.CharField(max_length=50, verbose_name="付款方式", help_text="付款方式", null=True, blank=True)
    order_status = models.CharField(max_length=50, verbose_name="订单状态", help_text="订单状态", null=True, blank=True)
    create_time = models.DateTimeField(verbose_name="订单创建时间", help_text="订单创建时间", null=True, blank=True)
    payment_time = models.DateTimeField(verbose_name="支付时间", help_text="支付时间", null=True, blank=True)
    delivery_time = models.DateTimeField(verbose_name="订单送达时间", help_text="订单送达时间", null=True, blank=True)
    commission_settlement_time = models.DateTimeField(verbose_name="佣金结算时间", help_text="佣金结算时间", null=True, blank=True)
    platform = models.CharField(max_length=50, verbose_name="平台", help_text="平台", null=True, blank=True)

    @property
    def item(self):
        """获取关联的订单项，用于序列化器"""
        items = self.tiktokorderitem_set.all()
        if items:
            return items[0]
        return TiktokOrderItem()

    @property
    def influencer(self):
        """获取关联的达人信息，用于序列化器"""
        influencers = self.tiktokorderinfluencer_set.all()
        if influencers:
            return influencers[0]
        return TiktokOrderInfluencer()

    @property
    def commission(self):
        """获取关联的佣金信息，用于序列化器"""
        commissions = self.tiktokordercommission_set.all()
        if commissions:
            return commissions[0]
        return TiktokOrderCommission()

    class Meta:
        db_table = table_prefix + "order_tiktok"
        verbose_name = "TikTok订单主表"
        verbose_name_plural = verbose_name
        ordering = ("-create_time",)


class TiktokOrderItem(CoreModel):
    """
    TikTok订单项 - 商品信息
    """
    order = models.ForeignKey(to="TiktokOrder", on_delete=models.CASCADE, verbose_name="关联订单", help_text="关联订单", db_constraint=False)
    product_id = models.CharField(max_length=64, verbose_name="商品ID", help_text="商品ID", null=True, blank=True)
    product_name = models.CharField(max_length=500, verbose_name="商品名称", help_text="商品名称", null=True, blank=True)
    sku_id = models.CharField(max_length=64, verbose_name="SKU ID", help_text="SKU ID", null=True, blank=True)
    product_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="商品价格", help_text="商品价格", null=True, blank=True)
    order_quantity = models.IntegerField(verbose_name="下单件数", help_text="下单件数", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "order_tiktok_item"
        verbose_name = "TikTok订单项"
        verbose_name_plural = verbose_name


class TiktokOrderInfluencer(CoreModel):
    """
    TikTok订单达人信息
    """
    order = models.ForeignKey(to="TiktokOrder", on_delete=models.CASCADE, verbose_name="关联订单", help_text="关联订单", db_constraint=False)
    influencer_username = models.CharField(max_length=100, verbose_name="达人用户名", help_text="达人用户名", null=True, blank=True)
    content_type = models.CharField(max_length=50, verbose_name="内容形式", help_text="内容形式", null=True, blank=True)
    content_id = models.CharField(max_length=64, verbose_name="内容ID", help_text="内容ID", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "order_tiktok_influencer"
        verbose_name = "TikTok订单达人"
        verbose_name_plural = verbose_name


class TiktokOrderCommission(CoreModel):
    """
    TikTok订单佣金信息
    """
    order = models.ForeignKey(to="TiktokOrder", on_delete=models.CASCADE, verbose_name="关联订单", help_text="关联订单", db_constraint=False)
    commission_model = models.CharField(max_length=50, verbose_name="佣金模型", help_text="佣金模型", null=True, blank=True)
    standard_commission_rate = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="标准佣金率", help_text="标准佣金率", null=True, blank=True)
    estimated_commission_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="预估计佣金额", help_text="预估计佣金额", null=True, blank=True)
    estimated_standard_commission = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="预计标准佣金付款", help_text="预计标准佣金付款", null=True, blank=True)
    actual_commission_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际计佣金额", help_text="实际计佣金额", null=True, blank=True)
    actual_commission = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际佣金", help_text="实际佣金", null=True, blank=True)
    store_ad_commission_rate = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="店铺广告佣金率", help_text="店铺广告佣金率", null=True, blank=True)
    estimated_store_ad_commission = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="预计店铺广告佣金付款", help_text="预计店铺广告佣金付款", null=True, blank=True)
    actual_store_ad_commission = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际店铺广告佣金付款", help_text="实际店铺广告佣金付款", null=True, blank=True)
    estimated_joint_influencer_bonus = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="预估合资达人奖金", help_text="预估合资达人奖金", null=True, blank=True)
    actual_joint_influencer_bonus = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际合资达人奖金", help_text="实际合资达人奖金", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "order_tiktok_commission"
        verbose_name = "TikTok订单佣金"
        verbose_name_plural = verbose_name


class ShangmaOrder(CoreModel):
    """
    上马订单
    """
    tenant_id = models.CharField(max_length=50, verbose_name="租户ID", help_text="租户ID", null=True, blank=True)
    category = models.IntegerField(verbose_name="分类", help_text="分类", null=True, blank=True)
    shop_id = models.IntegerField(verbose_name="店铺ID", help_text="店铺ID", null=True, blank=True)
    shop_name = models.CharField(max_length=200, verbose_name="店铺名称", help_text="店铺名称", null=True, blank=True)
    order_no = models.CharField(max_length=64, verbose_name="订单号", help_text="订单号", db_index=True)
    third_order_no = models.CharField(max_length=64, verbose_name="第三方订单号", help_text="第三方订单号", null=True, blank=True)
    third_order_time = models.DateTimeField(verbose_name="第三方订单时间", help_text="第三方订单时间", null=True, blank=True)
    third_order_status = models.CharField(max_length=50, verbose_name="第三方订单状态", help_text="第三方订单状态", null=True, blank=True)
    payment_method = models.CharField(max_length=50, verbose_name="支付方式", help_text="支付方式", null=True, blank=True)
    logistics_no = models.CharField(max_length=100, verbose_name="物流单号", help_text="物流单号", null=True, blank=True)
    logistics_name = models.CharField(max_length=100, verbose_name="物流公司名称", help_text="物流公司名称", null=True, blank=True)
    replace_type = models.IntegerField(default=0, verbose_name="换货类型", help_text="换货类型", null=True, blank=True)
    order_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="订单金额", help_text="订单金额", null=True, blank=True)
    order_income_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="订单收入金额", help_text="订单收入金额", null=True, blank=True)
    goods_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="商品金额", help_text="商品金额", null=True, blank=True)
    buyer_paid_shipping_fee = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="买家支付运费", help_text="买家支付运费", null=True, blank=True)
    platform_shipping_discount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="平台运费优惠", help_text="平台运费优惠", null=True, blank=True)
    third_shipping_discount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="第三方运费优惠", help_text="第三方运费优惠", null=True, blank=True)
    seller_shipping_discount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="卖家运费优惠", help_text="卖家运费优惠", null=True, blank=True)
    actual_shipping_fee = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际运费", help_text="实际运费", null=True, blank=True)
    final_shipping_fee = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="最终运费", help_text="最终运费", null=True, blank=True)
    voucher_from_platform = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="平台优惠券", help_text="平台优惠券", null=True, blank=True)
    voucher_from_seller = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="卖家优惠券", help_text="卖家优惠券", null=True, blank=True)
    commission_fee = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="佣金费用", help_text="佣金费用", null=True, blank=True)
    service_fee = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="服务费用", help_text="服务费用", null=True, blank=True)
    other_fee = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="其他费用", help_text="其他费用", null=True, blank=True)
    other_fee_json = models.TextField(verbose_name="其他费用JSON", help_text="其他费用JSON", null=True, blank=True)
    purchase_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="采购金额", help_text="采购金额", null=True, blank=True)
    order_shipped_time = models.DateTimeField(verbose_name="订单发货时间", help_text="订单发货时间", null=True, blank=True)
    order_completed_time = models.DateTimeField(verbose_name="订单完成时间", help_text="订单完成时间", null=True, blank=True)
    order_status = models.IntegerField(default=0, verbose_name="订单状态", help_text="订单状态", null=True, blank=True)
    warehouse_id = models.CharField(max_length=64, verbose_name="仓库ID", help_text="仓库ID", null=True, blank=True)
    order_profit = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="订单利润", help_text="订单利润", null=True, blank=True)
    shipping_difference = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="运费差额", help_text="运费差额", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "order_shangma"
        verbose_name = "上马订单"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
