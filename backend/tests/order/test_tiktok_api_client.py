"""
TikTok API客户端测试用例
"""
import unittest
from datetime import datetime, timedelta
from django.test import TestCase

from server.order.tiktok_api_client import TiktokApiClient


class TiktokApiClientTests(TestCase):
    """TikTok API 客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = TiktokApiClient(
            access_token='test_access_token',
            shop_id='test_shop_id'
        )
    
    def test_search_orders(self):
        """测试搜索订单"""
        result = self.client.search_orders()
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertIn('orders', result['data'])
        self.assertIsInstance(result['data']['orders'], list)
    
    def test_search_orders_with_time_range(self):
        """测试按时间范围搜索订单"""
        start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        
        result = self.client.search_orders(start_time, end_time)
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertIn('orders', result['data'])
    
    def test_get_order_detail(self):
        """测试获取订单详情"""
        result = self.client.get_order_detail('TEST_ORDER_001')
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertEqual(result['data']['order_id'], 'TEST_ORDER_001')
    
    def test_sync_orders(self):
        """测试同步订单"""
        orders = self.client.sync_orders()
        
        self.assertIsInstance(orders, list)
    
    def test_dynamic_credentials(self):
        """测试动态凭证设置"""
        client = TiktokApiClient()
        client.set_credentials('new_token', 'new_shop_id')
        
        self.assertEqual(client.access_token, 'new_token')
        self.assertEqual(client.shop_id, 'new_shop_id')


if __name__ == '__main__':
    unittest.main()
