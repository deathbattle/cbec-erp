"""
TikTok同步配置测试用例
"""
import unittest
from datetime import datetime, timedelta
from django.test import TestCase

from server.order.models import TiktokSyncConfig


class TiktokSyncConfigTests(TestCase):
    """TikTok同步配置测试"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = TiktokSyncConfig.objects.create(
            is_enabled=True,
            sync_interval=60,
            sync_days=7
        )
        
        self.assertTrue(config.is_enabled)
        self.assertEqual(config.sync_interval, 60)
        self.assertEqual(config.sync_days, 7)
        self.assertEqual(config.sync_status, 'idle')
    
    def test_update_next_sync_time(self):
        """测试更新下次同步时间"""
        config = TiktokSyncConfig.objects.create(
            is_enabled=True,
            sync_interval=60,
            sync_days=7,
            last_sync_time=datetime.now()
        )
        
        config.update_next_sync_time()
        
        self.assertIsNotNone(config.next_sync_time)
        expected_time = config.last_sync_time + timedelta(minutes=60)
        self.assertEqual(config.next_sync_time.replace(microsecond=0), expected_time.replace(microsecond=0))


if __name__ == '__main__':
    unittest.main()
