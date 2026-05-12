"""
TikTok订单同步定时任务
"""
import logging
from celery import shared_task
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from server.order.tiktok_sync_service import TiktokSyncService
    SYNC_SERVICE_AVAILABLE = True
except ImportError:
    SYNC_SERVICE_AVAILABLE = False


@shared_task(name='sync_tiktok_orders')
def sync_tiktok_orders_task(days: int = 7):
    """
    同步TikTok订单定时任务
    
    Args:
        days: 同步最近N天的订单
    """
    if not SYNC_SERVICE_AVAILABLE:
        logger.error("TikTok同步服务不可用")
        return {'success': False, 'message': '同步服务不可用'}
    
    try:
        logger.info(f"开始执行TikTok订单同步任务，同步最近{days}天数据")
        
        sync_service = TiktokSyncService()
        result = sync_service.sync_recent_orders(days)
        
        logger.info(f"TikTok订单同步任务完成: {result}")
        return result
    
    except Exception as e:
        logger.error(f"TikTok订单同步任务失败: {str(e)}", exc_info=True)
        return {'success': False, 'message': str(e)}


@shared_task(name='sync_tiktok_orders_full')
def sync_tiktok_orders_full_task(start_time: str = None, end_time: str = None):
    """
    全量同步TikTok订单任务
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
    """
    if not SYNC_SERVICE_AVAILABLE:
        logger.error("TikTok同步服务不可用")
        return {'success': False, 'message': '同步服务不可用'}
    
    try:
        logger.info(f"开始执行TikTok订单全量同步任务，时间范围: {start_time} - {end_time}")
        
        sync_service = TiktokSyncService()
        result = sync_service.sync_orders(start_time, end_time)
        
        logger.info(f"TikTok订单全量同步任务完成: {result}")
        return result
    
    except Exception as e:
        logger.error(f"TikTok订单全量同步任务失败: {str(e)}", exc_info=True)
        return {'success': False, 'message': str(e)}


def schedule_sync_tiktok_orders(days: int = 7):
    """
    调度TikTok订单同步任务
    
    Args:
        days: 同步最近N天的订单
    """
    from application.celery import app
    
    # 立即执行同步任务
    result = sync_tiktok_orders_task.delay(days)
    return result


def get_sync_task_status(task_id: str):
    """
    获取同步任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
    """
    from application.celery import app
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=app)
    
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None
    }