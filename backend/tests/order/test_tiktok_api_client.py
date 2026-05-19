"""
TikTok API客户端测试用例
"""
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase

from server.order.tiktok_api_client import TiktokApiClient
from .mock_tiktok_api import TiktokApiMock


class TiktokApiClientTests(TestCase):
    """TikTok API 客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = TiktokApiClient(
            access_token='test_access_token',
            shop_id='test_shop_id'
        )
    
    @patch.object(TiktokApiClient, '_make_request')
    def test_search_orders(self, mock_request):
        """测试搜索订单"""
        mock_request.return_value = TiktokApiMock.mock_order_search_response({})
        
        result = self.client.search_orders()
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertIn('orders', result['data'])
        self.assertIsInstance(result['data']['orders'], list)
        mock_request.assert_called_once()
    
    @patch.object(TiktokApiClient, '_make_request')
    def test_search_orders_with_time_range(self, mock_request):
        """测试按时间范围搜索订单"""
        mock_request.return_value = TiktokApiMock.mock_order_search_response({})
        
        start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        
        result = self.client.search_orders(start_time, end_time)
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertIn('orders', result['data'])
        mock_request.assert_called_once()
    
    @patch.object(TiktokApiClient, '_make_request')
    def test_get_order_detail(self, mock_request):
        """测试获取订单详情"""
        mock_request.return_value = TiktokApiMock.mock_order_detail_response({'order_id': 'TEST_ORDER_001'})
        
        result = self.client.get_order_detail('TEST_ORDER_001')
        
        self.assertEqual(result.get('code'), 0)
        self.assertIn('data', result)
        self.assertEqual(result['data']['order_id'], 'TEST_ORDER_001')
        mock_request.assert_called_once()
    
    @patch.object(TiktokApiClient, '_make_request')
    def test_sync_orders(self, mock_request):
        """测试同步订单"""
        # 模拟多页数据
        mock_request.side_effect = [
            TiktokApiMock.mock_order_search_response({'page_num': 1, 'page_size': 50}),
            TiktokApiMock.mock_order_search_response({'page_num': 2, 'page_size': 50}),
            TiktokApiMock.mock_order_search_response({'page_num': 3, 'page_size': 50}),
            TiktokApiMock.mock_order_search_response({'page_num': 4, 'page_size': 50}),
            TiktokApiMock.mock_order_search_response({'page_num': 5, 'page_size': 50}),
        ]
        
        orders = self.client.sync_orders()
        
        self.assertIsInstance(orders, list)
        self.assertEqual(len(orders), 250)  # 5页 * 50条
    
    def test_dynamic_credentials(self):
        """测试动态凭证设置"""
        client = TiktokApiClient()
        client.set_credentials('new_token', 'new_shop_id')
        
        self.assertEqual(client.access_token, 'new_token')
        self.assertEqual(client.shop_id, 'new_shop_id')
    
    def test_missing_access_token(self):
        """测试缺少 access_token"""
        client = TiktokApiClient(shop_id='test_shop_id')
        result = client.search_orders()
        
        self.assertEqual(result.get('code'), 401)
        self.assertEqual(result.get('message'), '缺少 access_token')
    
    def test_missing_shop_id(self):
        """测试缺少 shop_id"""
        client = TiktokApiClient(access_token='test_token')
        result = client.search_orders()
        
        self.assertEqual(result.get('code'), 400)
        self.assertEqual(result.get('message'), '缺少 shop_id')


if __name__ == '__main__':
    unittest.main()
