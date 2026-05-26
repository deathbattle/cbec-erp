"""
TikTok同步服务测试用例
"""
import unittest
from datetime import datetime, timedelta
from django.test import TestCase
from unittest.mock import patch

from server.order.models import TiktokOrder
from server.order.tiktok_api_client import TiktokApiClient
from server.order.tiktok_sync_service import TiktokSyncService


class TiktokSyncServiceTests(TestCase):
    """TikTok同步服务测试"""
    
    def setUp(self):
        self.sync_service = TiktokSyncService()
    
    def test_parse_datetime(self):
        """测试日期时间解析"""
        test_cases = [
            ("2024-01-01 12:00:00", datetime(2024, 1, 1, 12, 0, 0)),
            ("2024-01-01T12:00:00", datetime(2024, 1, 1, 12, 0, 0)),
            ("2024-01-01", datetime(2024, 1, 1, 0, 0, 0)),
            (None, None),
            ("invalid", None),
        ]
        
        for input_val, expected in test_cases:
            result = self.sync_service._parse_datetime(input_val)
            self.assertEqual(result, expected)
    
    @patch.object(TiktokApiClient, 'sync_orders')
    @patch.object(TiktokSyncService, '_get_credentials')
    def test_sync_orders(self, mock_get_credentials, mock_sync_orders):
        """测试同步订单功能"""
        # Mock 凭证获取
        mock_get_credentials.return_value = ('test_access_token', 'test_shop_id')
        
        mock_sync_orders.return_value = [
            {
                'order_id': 'TEST_ORDER_001',
                'payment_amount': 100.0,
                'currency_unit': 'USD',
                'is_refunded': False,
                'payment_method': 'PayPal',
                'order_status': 'PAID',
                'create_time': '2024-01-01 12:00:00',
                'payment_time': '2024-01-01 12:05:00',
                'delivery_time': '2024-01-03 10:00:00',
                'commission_settlement_time': '2024-01-10 00:00:00',
                'platform': 'TikTok',
                'items': [{
                    'product_id': 'PROD_001',
                    'product_name': 'Test Product',
                    'sku_id': 'SKU_001',
                    'product_price': 50.0,
                    'order_quantity': 2
                }],
                'influencer': {
                    'influencer_username': 'TestInfluencer',
                    'content_type': 'VIDEO',
                    'content_id': 'CONTENT_001'
                },
                'commission': {
                    'commission_model': 'STANDARD',
                    'standard_commission_rate': 0.1,
                    'estimated_commission_amount': 10.0,
                    'estimated_standard_commission': 10.0,
                    'actual_commission_amount': 10.0,
                    'actual_commission': 10.0,
                    'store_ad_commission_rate': 0.0,
                    'estimated_store_ad_commission': 0.0,
                    'actual_store_ad_commission': 0.0,
                    'estimated_joint_influencer_bonus': 0.0,
                    'actual_joint_influencer_bonus': 0.0
                }
            }
        ]
        
        result = self.sync_service.sync_orders()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_fetched'], 1)
        self.assertEqual(result['total_created'], 1)
        self.assertEqual(result['total_updated'], 0)
        
        order = TiktokOrder.objects.get(order_id='TEST_ORDER_001')
        self.assertEqual(order.payment_amount, 100.0)
        self.assertEqual(order.currency_unit, 'USD')
        self.assertFalse(order.is_refunded)
    
    @patch.object(TiktokApiClient, 'sync_orders')
    @patch.object(TiktokSyncService, '_get_credentials')
    def test_sync_orders_update(self, mock_get_credentials, mock_sync_orders):
        """测试更新已存在的订单"""
        # Mock 凭证获取
        mock_get_credentials.return_value = ('test_access_token', 'test_shop_id')
        
        TiktokOrder.objects.create(
            order_id='TEST_ORDER_002',
            payment_amount=50.0,
            currency_unit='USD',
            order_status='PAID'
        )
        
        mock_sync_orders.return_value = [
            {
                'order_id': 'TEST_ORDER_002',
                'payment_amount': 200.0,
                'currency_unit': 'USD',
                'is_refunded': False,
                'payment_method': 'CreditCard',
                'order_status': 'SHIPPED',
                'create_time': '2024-01-01 12:00:00',
                'payment_time': '2024-01-01 12:05:00',
                'delivery_time': '2024-01-03 10:00:00',
                'commission_settlement_time': '2024-01-10 00:00:00',
                'platform': 'TikTok',
                'items': [],
                'influencer': {},
                'commission': {}
            }
        ]
        
        result = self.sync_service.sync_orders()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_fetched'], 1)
        self.assertEqual(result['total_created'], 0)
        self.assertEqual(result['total_updated'], 1)
        
        order = TiktokOrder.objects.get(order_id='TEST_ORDER_002')
        self.assertEqual(order.payment_amount, 200.0)
        self.assertEqual(order.order_status, 'SHIPPED')
    
    def test_sync_recent_orders(self):
        """测试同步最近N天订单"""
        result = self.sync_service.sync_recent_orders(days=3)
        
        self.assertIn('success', result)
    
    def test_get_sync_status(self):
        """测试获取同步状态"""
        status_info = self.sync_service.get_sync_status()
        
        self.assertIn('total_orders', status_info)
        self.assertIn('last_sync_time', status_info)
        self.assertIn('sync_enabled', status_info)


if __name__ == '__main__':
    unittest.main()
