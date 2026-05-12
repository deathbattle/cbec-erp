import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.conf import settings

logger = __import__('logging').getLogger(__name__)


class TiktokApiClient:
    """
    TikTok API客户端 - 模拟对接TikTok官方API
    
    注：这是一个模拟实现，实际生产环境需要对接TikTok官方开放平台API：
    https://developers.tiktok.com/doc/order-management-api
    """
    
    def __init__(self):
        # TikTok官方API基础配置（模拟）
        self.base_url = "https://open-api.tiktokglobalshop.com"
        self.app_key = getattr(settings, 'TIKTOK_APP_KEY', 'test_app_key')
        self.app_secret = getattr(settings, 'TIKTOK_APP_SECRET', 'test_app_secret')
        self.access_token = getattr(settings, 'TIKTOK_ACCESS_TOKEN', 'test_access_token')
        self.shop_id = getattr(settings, 'TIKTOK_SHOP_ID', 'test_shop_id')
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成签名（模拟）"""
        return f"signature_{hash(frozenset(params.items()))}"
    
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None, data: Dict = None) -> Dict:
        """
        发送API请求（模拟）
        实际生产环境需要实现真实的TikTok API签名和请求逻辑
        """
        url = f"{self.base_url}{endpoint}"
        
        # 模拟网络延迟
        time.sleep(random.uniform(0.1, 0.3))
        
        # 模拟返回数据
        if endpoint == '/api/orders/search':
            return self._mock_order_search_response(params)
        elif endpoint == '/api/orders/detail':
            return self._mock_order_detail_response(params)
        
        return {"code": 0, "message": "success", "data": {}}
    
    def _mock_order_search_response(self, params: Dict) -> Dict:
        """模拟订单搜索响应"""
        page_size = params.get('page_size', 20)
        page_num = params.get('page_num', 1)
        start_time = params.get('create_time_from')
        end_time = params.get('create_time_to')
        
        # 生成模拟订单数据
        orders = []
        for i in range(page_size):
            order_id = f"ORDER_{page_num}_{i}_{int(time.time())}"
            create_time = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            
            orders.append({
                "order_id": order_id,
                "order_no": f"TTD{order_id}",
                "payment_amount": round(random.uniform(10, 500), 2),
                "currency_unit": "USD",
                "is_refunded": random.choice([True, False]),
                "payment_method": random.choice(["PayPal", "CreditCard", "TikTokPay"]),
                "order_status": random.choice(["PAID", "SHIPPED", "DELIVERED", "COMPLETED", "REFUNDED"]),
                "create_time": create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "payment_time": (create_time + timedelta(minutes=random.randint(5, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                "delivery_time": (create_time + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
                "commission_settlement_time": (create_time + timedelta(days=random.randint(7, 14))).strftime("%Y-%m-%d %H:%M:%S"),
                "platform": "TikTok",
                "items": [
                    {
                        "product_id": f"PROD_{random.randint(1000, 9999)}",
                        "product_name": f"Product {random.randint(1, 100)}",
                        "sku_id": f"SKU_{random.randint(100, 999)}",
                        "product_price": round(random.uniform(10, 200), 2),
                        "order_quantity": random.randint(1, 5)
                    }
                ],
                "influencer": {
                    "influencer_username": f"Influencer_{random.randint(1000, 9999)}",
                    "content_type": random.choice(["VIDEO", "LIVE", "FEED"]),
                    "content_id": f"CONTENT_{random.randint(10000, 99999)}"
                },
                "commission": {
                    "commission_model": "STANDARD",
                    "standard_commission_rate": round(random.uniform(0.05, 0.2), 4),
                    "estimated_commission_amount": round(random.uniform(1, 50), 2),
                    "estimated_standard_commission": round(random.uniform(1, 50), 2),
                    "actual_commission_amount": round(random.uniform(1, 50), 2),
                    "actual_commission": round(random.uniform(1, 50), 2),
                    "store_ad_commission_rate": round(random.uniform(0, 0.05), 4),
                    "estimated_store_ad_commission": round(random.uniform(0, 10), 2),
                    "actual_store_ad_commission": round(random.uniform(0, 10), 2),
                    "estimated_joint_influencer_bonus": round(random.uniform(0, 5), 2),
                    "actual_joint_influencer_bonus": round(random.uniform(0, 5), 2)
                }
            })
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "orders": orders,
                "total": 100,
                "page_num": page_num,
                "page_size": page_size,
                "total_pages": 5
            }
        }
    
    def _mock_order_detail_response(self, params: Dict) -> Dict:
        """模拟订单详情响应"""
        order_id = params.get('order_id')
        create_time = datetime.now() - timedelta(days=random.randint(0, 7))
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "order_id": order_id,
                "order_no": f"TTD{order_id}",
                "payment_amount": round(random.uniform(10, 500), 2),
                "currency_unit": "USD",
                "is_refunded": random.choice([True, False]),
                "payment_method": random.choice(["PayPal", "CreditCard", "TikTokPay"]),
                "order_status": random.choice(["PAID", "SHIPPED", "DELIVERED", "COMPLETED", "REFUNDED"]),
                "create_time": create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "payment_time": (create_time + timedelta(minutes=random.randint(5, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                "delivery_time": (create_time + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"),
                "commission_settlement_time": (create_time + timedelta(days=random.randint(7, 14))).strftime("%Y-%m-%d %H:%M:%S"),
                "platform": "TikTok",
                "items": [
                    {
                        "product_id": f"PROD_{random.randint(1000, 9999)}",
                        "product_name": f"Product {random.randint(1, 100)}",
                        "sku_id": f"SKU_{random.randint(100, 999)}",
                        "product_price": round(random.uniform(10, 200), 2),
                        "order_quantity": random.randint(1, 5)
                    }
                ],
                "influencer": {
                    "influencer_username": f"Influencer_{random.randint(1000, 9999)}",
                    "content_type": random.choice(["VIDEO", "LIVE", "FEED"]),
                    "content_id": f"CONTENT_{random.randint(10000, 99999)}"
                },
                "commission": {
                    "commission_model": "STANDARD",
                    "standard_commission_rate": round(random.uniform(0.05, 0.2), 4),
                    "estimated_commission_amount": round(random.uniform(1, 50), 2),
                    "estimated_standard_commission": round(random.uniform(1, 50), 2),
                    "actual_commission_amount": round(random.uniform(1, 50), 2),
                    "actual_commission": round(random.uniform(1, 50), 2),
                    "store_ad_commission_rate": round(random.uniform(0, 0.05), 4),
                    "estimated_store_ad_commission": round(random.uniform(0, 10), 2),
                    "actual_store_ad_commission": round(random.uniform(0, 10), 2),
                    "estimated_joint_influencer_bonus": round(random.uniform(0, 5), 2),
                    "actual_joint_influencer_bonus": round(random.uniform(0, 5), 2)
                }
            }
        }
    
    def search_orders(self, 
                      start_time: Optional[str] = None, 
                      end_time: Optional[str] = None,
                      page_num: int = 1, 
                      page_size: int = 20) -> Dict:
        """
        搜索订单
        
        Args:
            start_time: 订单创建起始时间 (格式: YYYY-MM-DD HH:MM:SS)
            end_time: 订单创建结束时间 (格式: YYYY-MM-DD HH:MM:SS)
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            订单列表数据
        """
        params = {
            'shop_id': self.shop_id,
            'page_num': page_num,
            'page_size': page_size
        }
        
        if start_time:
            params['create_time_from'] = start_time
        if end_time:
            params['create_time_to'] = end_time
        
        return self._make_request('/api/orders/search', method='GET', params=params)
    
    def get_order_detail(self, order_id: str) -> Dict:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
            
        Returns:
            订单详情数据
        """
        params = {
            'shop_id': self.shop_id,
            'order_id': order_id
        }
        
        return self._make_request('/api/orders/detail', method='GET', params=params)
    
    def sync_orders(self, 
                    start_time: Optional[str] = None, 
                    end_time: Optional[str] = None) -> List[Dict]:
        """
        同步订单数据（分页获取所有订单）
        
        Args:
            start_time: 订单创建起始时间
            end_time: 订单创建结束时间
            
        Returns:
            所有订单列表
        """
        all_orders = []
        page_num = 1
        page_size = 50
        
        while True:
            response = self.search_orders(start_time, end_time, page_num, page_size)
            
            if response.get('code') != 0:
                logger.error(f"获取订单失败: {response.get('message')}")
                break
            
            data = response.get('data', {})
            orders = data.get('orders', [])
            
            if not orders:
                break
            
            all_orders.extend(orders)
            
            total_pages = data.get('total_pages', 1)
            if page_num >= total_pages:
                break
            
            page_num += 1
        
        logger.info(f"成功同步 {len(all_orders)} 条TikTok订单")
        return all_orders