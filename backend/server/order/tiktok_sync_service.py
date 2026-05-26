import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.utils import timezone

from .models import TiktokOrder, TiktokOrderItem, TiktokOrderInfluencer, TiktokOrderCommission
from .tiktok_api_client import TiktokApiClient

logger = logging.getLogger(__name__)


class TiktokSyncService:
    """
    TikTok订单同步服务
    
    负责从TikTok官方API同步订单数据到本地数据库
    """
    
    def __init__(self):
        self.api_client = TiktokApiClient()
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not datetime_str:
            return None
        
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"无法解析日期时间: {datetime_str}")
        return None
    
    def _create_or_update_order(self, order_data: Dict) -> Tuple[TiktokOrder, bool]:
        """创建或更新订单 - 使用 update_or_create 保证原子性
        
        Returns:
            (order, created): 订单对象和是否为新创建的布尔值
        """
        order_id = order_data.get('order_id')
        
        defaults = {
            'payment_amount': order_data.get('payment_amount'),
            'currency_unit': order_data.get('currency_unit'),
            'is_refunded': order_data.get('is_refunded', False),
            'payment_method': order_data.get('payment_method'),
            'order_status': order_data.get('order_status'),
            'create_time': self._parse_datetime(order_data.get('create_time')),
            'payment_time': self._parse_datetime(order_data.get('payment_time')),
            'delivery_time': self._parse_datetime(order_data.get('delivery_time')),
            'commission_settlement_time': self._parse_datetime(order_data.get('commission_settlement_time')),
            'platform': order_data.get('platform', 'TikTok'),
        }
        
        order, created = TiktokOrder.objects.update_or_create(
            order_id=order_id,
            defaults=defaults
        )
        
        # 处理订单项
        items = order_data.get('items', [])
        if items:
            item_data = items[0]
            self._create_or_update_order_item(order, item_data)
        
        # 处理达人信息
        influencer_data = order_data.get('influencer', {})
        if influencer_data:
            self._create_or_update_influencer(order, influencer_data)
        
        # 处理佣金信息
        commission_data = order_data.get('commission', {})
        if commission_data:
            self._create_or_update_commission(order, commission_data)
        
        if created:
            logger.debug(f"创建新订单: {order_id}")
        else:
            logger.debug(f"更新订单: {order_id}")
        
        return order, created
    
    def _create_or_update_order_item(self, order: TiktokOrder, item_data: Dict):
        """创建或更新订单项 - 使用 update_or_create 保证原子性"""
        defaults = {
            'product_id': item_data.get('product_id'),
            'product_name': item_data.get('product_name'),
            'sku_id': item_data.get('sku_id'),
            'product_price': item_data.get('product_price'),
            'order_quantity': item_data.get('order_quantity'),
        }
        
        TiktokOrderItem.objects.update_or_create(
            order=order,
            defaults=defaults
        )
    
    def _create_or_update_influencer(self, order: TiktokOrder, influencer_data: Dict):
        """创建或更新达人信息 - 使用 update_or_create 保证原子性"""
        defaults = {
            'influencer_username': influencer_data.get('influencer_username'),
            'content_type': influencer_data.get('content_type'),
            'content_id': influencer_data.get('content_id'),
        }
        
        TiktokOrderInfluencer.objects.update_or_create(
            order=order,
            defaults=defaults
        )
    
    def _create_or_update_commission(self, order: TiktokOrder, commission_data: Dict):
        """创建或更新佣金信息 - 使用 update_or_create 保证原子性"""
        defaults = {
            'commission_model': commission_data.get('commission_model'),
            'standard_commission_rate': commission_data.get('standard_commission_rate'),
            'estimated_commission_amount': commission_data.get('estimated_commission_amount'),
            'estimated_standard_commission': commission_data.get('estimated_standard_commission'),
            'actual_commission_amount': commission_data.get('actual_commission_amount'),
            'actual_commission': commission_data.get('actual_commission'),
            'store_ad_commission_rate': commission_data.get('store_ad_commission_rate'),
            'estimated_store_ad_commission': commission_data.get('estimated_store_ad_commission'),
            'actual_store_ad_commission': commission_data.get('actual_store_ad_commission'),
            'estimated_joint_influencer_bonus': commission_data.get('estimated_joint_influencer_bonus'),
            'actual_joint_influencer_bonus': commission_data.get('actual_joint_influencer_bonus'),
        }
        
        TiktokOrderCommission.objects.update_or_create(
            order=order,
            defaults=defaults
        )
    
    def _get_credentials(self) -> Tuple[str, str]:
        """
        获取有效的 access_token 和 shop_id
        
        从数据库读取配置，尝试刷新 token，获取店铺信息
        
        Returns:
            (access_token, shop_id)
        """
        from .models import TiktokSyncConfig
        
        access_token = None
        shop_id = None
        
        try:
            # 从数据库获取配置
            config = TiktokSyncConfig.objects.first()
            if not config:
                logger.warning("未找到TikTok同步配置，使用默认配置")
                return access_token, shop_id
            
            access_token = config.access_token
            refresh_token = config.refresh_token
            shop_id = config.shop_id
            
            # 如果有 refresh_token，尝试刷新 access_token
            if refresh_token:
                logger.info("尝试刷新 access_token...")
                refresh_result = self.api_client.refresh_access_token(refresh_token)
                
                if refresh_result.get('code') == 0:
                    data = refresh_result.get('data', {})
                    new_token = data.get('access_token')
                    new_refresh_token = data.get('refresh_token')
                    
                    if new_token:
                        access_token = new_token
                        logger.info("access_token 刷新成功")
                        
                        # 更新数据库中的凭证
                        config.access_token = new_token
                        if new_refresh_token:
                            config.refresh_token = new_refresh_token
                        config.save()
                else:
                    logger.warning(f"access_token 刷新失败，使用原token: {refresh_result.get('message')}")
            
            # 如果没有 shop_id，尝试从 API 获取
            if access_token and not shop_id:
                logger.info("尝试获取店铺信息...")
                shops_result = self.api_client.get_authorized_shops(access_token)
                
                if shops_result.get('code') == 0:
                    data = shops_result.get('data', {})
                    shops = data.get('shops', [])
                    
                    if shops:
                        shop_id = shops[0].get('shop_id')
                        shop_cipher = shops[0].get('shop_cipher')
                        logger.info(f"获取店铺信息成功，shop_id: {shop_id}")
                        
                        # 更新数据库配置
                        config.shop_id = shop_id
                        if shop_cipher:
                            config.shop_cipher = shop_cipher
                        config.save()
            
            return access_token, shop_id
            
        except Exception as e:
            logger.error(f"获取凭证失败: {str(e)}")
            return access_token, shop_id
    
    @transaction.atomic
    def sync_orders(self, 
                    start_time: Optional[str] = None, 
                    end_time: Optional[str] = None) -> Dict:
        """
        同步订单数据
        
        Args:
            start_time: 同步起始时间
            end_time: 同步结束时间
            
        Returns:
            同步结果统计
        """
        logger.info(f"开始同步TikTok订单，时间范围: {start_time} - {end_time}")
        
        # ===== 新增：先获取/刷新凭证 =====
        access_token, shop_id = self._get_credentials()
        
        if not access_token:
            logger.error("无法获取有效的 access_token")
            return {
                'success': False,
                'total_fetched': 0,
                'total_created': 0,
                'total_updated': 0,
                'message': '无法获取有效的 access_token，请先完成授权'
            }
        
        if not shop_id:
            logger.error("无法获取有效的 shop_id")
            return {
                'success': False,
                'total_fetched': 0,
                'total_created': 0,
                'total_updated': 0,
                'message': '无法获取有效的 shop_id'
            }
        
        logger.info(f"使用凭证: access_token={access_token[:10]}..., shop_id={shop_id}")
        
        start_datetime = None
        if start_time:
            start_datetime = self._parse_datetime(start_time)
        
        # 如果没有指定时间范围，默认同步最近7天的数据
        if not start_time:
            start_datetime = datetime.now() - timedelta(days=7)
            start_time = start_datetime.strftime("%Y-%m-%d 00:00:00")
        
        if not end_time:
            end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        
        # 从API获取订单数据（传入动态凭证）
        orders_data = self.api_client.sync_orders(start_time, end_time, 
                                                   access_token=access_token, 
                                                   shop_id=shop_id)
        
        if not orders_data:
            logger.info("没有获取到TikTok订单数据")
            return {
                'success': True,
                'total_fetched': 0,
                'total_created': 0,
                'total_updated': 0,
                'message': '没有获取到订单数据'
            }
        
        # 保存订单到数据库
        created_count = 0
        updated_count = 0
        
        for order_data in orders_data:
            order_id = order_data.get('order_id')
            
            try:
                order, created = self._create_or_update_order(order_data)
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.error(f"保存订单失败 {order_id}: {str(e)}")
        
        logger.info(f"TikTok订单同步完成: 新增 {created_count} 条，更新 {updated_count} 条")
        
        return {
            'success': True,
            'total_fetched': len(orders_data),
            'total_created': created_count,
            'total_updated': updated_count,
            'message': f'同步完成，新增 {created_count} 条，更新 {updated_count} 条'
        }
    
    def sync_recent_orders(self, days: int = 7) -> Dict:
        """
        同步最近N天的订单
        
        Args:
            days: 天数
            
        Returns:
            同步结果统计
        """
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
        
        return self.sync_orders(start_time, end_time)
    
    def get_sync_status(self) -> Dict:
        """
        获取同步状态信息
        
        Returns:
            状态信息
        """
        total_orders = TiktokOrder.objects.count()
        
        # 获取最近同步时间（取最新订单的创建时间）
        latest_order = TiktokOrder.objects.order_by('-create_time').first()
        last_sync_time = latest_order.create_time if latest_order else None
        
        return {
            'total_orders': total_orders,
            'last_sync_time': last_sync_time.strftime("%Y-%m-%d %H:%M:%S") if last_sync_time else None,
            'sync_enabled': True
        }