"""
TikTok API客户端测试用例
"""
import unittest
from datetime import datetime, timedelta
from django.test import TestCase

from server.order.tiktok_api_client import TiktokApiClient


class TiktokApiClientTests(TestCase):
    """TikTok API客户端测试"""
    
    def test_search_orders(self):
        """测试搜索订单"""
        client = TiktokApiClient()
        result = client.search_orders()
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertIn('orders', result['data'])
        self.assertIsInstance(result['data']['orders'], list)
    
    def test_search_orders_with_time_range(self):
        """测试按时间范围搜索订单"""
        client = TiktokApiClient()
        start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        
        result = client.search_orders(start_time, end_time)
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertIn('orders', result['data'])
    
    def test_get_order_detail(self):
        """测试获取订单详情"""
        client = TiktokApiClient()
        result = client.get_order_detail('TEST_ORDER_001')
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertEqual(result['data']['order_id'], 'TEST_ORDER_001')
    
    def test_sync_orders(self):
        """测试同步订单"""
        client = TiktokApiClient()
        orders = client.sync_orders()
        
        self.assertIsInstance(orders, list)


if __name__ == '__main__':
    unittest.main()
