"""
TikTok API Mock 工具 - 用于测试环境模拟 TikTok API 响应
"""
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


class TiktokApiMock:
    """TikTok API Mock 工具类"""
    
    @staticmethod
    def _generate_signature(params: Dict[str, Any]) -> str:
        """生成签名（模拟）"""
        return f"signature_{hash(frozenset(params.items()))}"
    
    @staticmethod
    def mock_order_search_response(params: Dict) -> Dict:
        """模拟订单搜索响应"""
        page_size = params.get('page_size', 20)
        page_num = params.get('page_num', 1)
        start_time = params.get('create_time_from')
        end_time = params.get('create_time_to')
        
        # 模拟网络延迟
        time.sleep(random.uniform(0.05, 0.15))
        
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
    
    @staticmethod
    def mock_order_detail_response(params: Dict) -> Dict:
        """模拟订单详情响应"""
        order_id = params.get('order_id')
        create_time = datetime.now() - timedelta(days=random.randint(0, 7))
        
        # 模拟网络延迟
        time.sleep(random.uniform(0.05, 0.15))
        
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
