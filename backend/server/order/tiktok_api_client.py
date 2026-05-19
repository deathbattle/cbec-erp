"""
TikTok API 客户端 - 对接 TikTok Shop 开放平台

官方文档: https://developers.tiktok.com/doc/order-management-api

OAuth 授权流程:
1. 获取授权链接 → 引导用户授权 → 获取 code
2. 用 code 换取 access_token 和 refresh_token
3. 使用 access_token 调用业务 API
4. access_token 过期后使用 refresh_token 刷新
"""
import requests
import time
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings

logger = __import__('logging').getLogger(__name__)


class TiktokApiClient:
    """
    TikTok API 客户端 - 支持 OAuth 授权、动态凭证和自动 Token 刷新
    """
    
    # OAuth 相关常量
    AUTH_BASE_URL = "https://auth.tiktok-shops.com"
    TOKEN_BASE_URL = "https://auth.tiktok-shops.com/api/v2"
    
    def __init__(self, access_token: str = None, shop_id: str = None, shop_cipher: str = None):
        """
        初始化 TikTok API 客户端
        
        Args:
            access_token: 动态传入的 access_token（可选）
            shop_id: 动态传入的 shop_id（可选）
            shop_cipher: 跨境店需要的 shop_cipher（可选）
        """
        self.base_url = getattr(settings, 'TIKTOK_API_BASE_URL', 'https://open-api.tiktokglobalshop.com')
        self.app_key = getattr(settings, 'TIKTOK_APP_KEY', '')
        self.app_secret = getattr(settings, 'TIKTOK_APP_SECRET', '')
        self.redirect_uri = getattr(settings, 'TIKTOK_REDIRECT_URI', '')
        
        self.access_token = access_token
        self.shop_id = shop_id
        self.shop_cipher = shop_cipher
        
        self._token_cache = {}
        self._refresh_token = None
    
    def set_credentials(self, access_token: str, shop_id: str, shop_cipher: str = None):
        """
        动态设置凭证（支持多店铺场景）
        
        Args:
            access_token: 店铺授权 token
            shop_id: 店铺 ID
            shop_cipher: 跨境店需要的 shop_cipher（可选）
        """
        self.access_token = access_token
        self.shop_id = shop_id
        self.shop_cipher = shop_cipher
    
    def set_refresh_token(self, refresh_token: str):
        """
        设置刷新令牌
        
        Args:
            refresh_token: 用于刷新 access_token 的令牌
        """
        self._refresh_token = refresh_token
    
    def get_authorization_url(self, state: str = None, scope: str = None) -> str:
        """
        获取授权链接，引导用户进行授权
        
        Args:
            state: 状态参数，用于防止 CSRF 攻击（可选）
            scope: 授权范围，多个用逗号分隔（可选）
            
        Returns:
            授权链接 URL
            
        使用示例:
            client = TiktokApiClient()
            url = client.get_authorization_url(state='random_state')
            # 跳转此 URL 引导用户授权
        """
        params = {
            'app_key': self.app_key,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
        }
        
        if state:
            params['state'] = state
        if scope:
            params['scope'] = scope
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.AUTH_BASE_URL}/oauth/authorize?{query_string}"
    
    def get_access_token(self, code: str) -> Dict:
        """
        使用授权码（code）换取访问令牌（access_token）
        
        Args:
            code: 用户授权后返回的授权码
            
        Returns:
            包含 access_token、refresh_token、shop_id 等信息的字典
            
        使用示例:
            client = TiktokApiClient()
            result = client.get_access_token(code='auth_code_from_callback')
            # result = {
            #     'code': 0,
            #     'message': 'success',
            #     'data': {
            #         'access_token': 'xxx',
            #         'refresh_token': 'yyy',
            #         'expires_in': 86400,
            #         'shop_id': 'zzz',
            #         'shop_cipher': 'aaa'  # 跨境店返回
            #     }
            # }
        """
        url = f"{self.TOKEN_BASE_URL}/token/get?grant_type=authorized_code"
        
        payload = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'auth_code': code,
            'grant_type': 'authorized_code'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                data = result.get('data', {})
                
                # 保存凭证
                self.access_token = data.get('access_token')
                self._refresh_token = data.get('refresh_token')
                self.shop_id = data.get('shop_id')
                self.shop_cipher = data.get('shop_cipher')
                
                # 更新缓存过期时间
                if self.access_token:
                    expires_in = data.get('expires_in', 86400)
                    cache_key = f"token_{self.access_token}"
                    self._token_cache[cache_key] = time.time() + expires_in
                
                logger.info(f"成功获取 access_token，店铺ID: {self.shop_id}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取 access_token 失败：{str(e)}")
            return {"code": 500, "message": f"网络请求失败：{str(e)}", "data": None}
    
    def refresh_access_token(self, refresh_token: str = None) -> Dict:
        """
        使用 refresh_token 刷新 access_token
        
        Args:
            refresh_token: 刷新令牌（可选，默认为实例中的 refresh_token）
            
        Returns:
            包含新的 access_token、refresh_token 的字典
            
        使用示例:
            client = TiktokApiClient()
            client.set_refresh_token('old_refresh_token')
            result = client.refresh_access_token()
        """
        token = refresh_token if refresh_token else self._refresh_token
        
        if not token:
            logger.error("缺少 refresh_token")
            return {"code": 400, "message": "缺少 refresh_token", "data": None}
        
        url = f"{self.TOKEN_BASE_URL}/token/refresh"
        
        payload = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'refresh_token': token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                data = result.get('data', {})
                
                # 更新凭证
                self.access_token = data.get('access_token')
                self._refresh_token = data.get('refresh_token')
                
                # 更新缓存过期时间
                if self.access_token:
                    expires_in = data.get('expires_in', 86400)
                    cache_key = f"token_{self.access_token}"
                    self._token_cache[cache_key] = time.time() + expires_in
                
                logger.info("成功刷新 access_token")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"刷新 access_token 失败：{str(e)}")
            return {"code": 500, "message": f"网络请求失败：{str(e)}", "data": None}
    
    def get_authorized_shops(self, access_token: str = None) -> Dict:
        """
        获取授权的店铺信息（推荐方式）
        
        Args:
            access_token: 访问令牌（可选）
            
        Returns:
            包含店铺列表的字典
            
        使用示例:
            result = client.get_authorized_shops()
            # result = {
            #     'code': 0,
            #     'message': 'success',
            #     'data': {
            #         'shops': [
            #             {
            #                 'shop_id': 'xxx',
            #                 'shop_name': '店铺名称',
            #                 'shop_cipher': 'yyy',
            #                 'region': 'US'
            #             }
            #         ]
            #     }
            # }
        """
        token = access_token if access_token else self.access_token
        
        if not token:
            logger.error("缺少 access_token")
            return {"code": 401, "message": "缺少 access_token", "data": None}
        
        url = f"{self.TOKEN_BASE_URL}/shop/get"
        
        headers = {
            'access-token': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                data = result.get('data', {})
                shops = data.get('shops', [])
                
                if shops:
                    first_shop = shops[0]
                    self.shop_id = first_shop.get('shop_id')
                    self.shop_cipher = first_shop.get('shop_cipher')
                    logger.info(f"获取店铺信息成功，店铺ID: {self.shop_id}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取店铺信息失败：{str(e)}")
            return {"code": 500, "message": f"网络请求失败：{str(e)}", "data": None}
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成 TikTok API 签名
        
        Args:
            params: 请求参数字典
            
        Returns:
            签名后的字符串（MD5 大写）
        """
        sorted_params = sorted(params.items())
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str = f"{sign_str}&app_secret={self.app_secret}"
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
    
    def _is_token_expired(self, access_token: str = None) -> bool:
        """
        检查 Token 是否过期
        
        Args:
            access_token: 要检查的 token（可选）
            
        Returns:
            True 表示已过期或即将过期
        """
        token = access_token or self.access_token
        if not token:
            return True
        
        cache_key = f"token_{token}"
        expire_time = self._token_cache.get(cache_key)
        
        if not expire_time:
            return False
        
        return time.time() >= expire_time - 300
    
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None, 
                      data: Dict = None, access_token: str = None, shop_id: str = None) -> Dict:
        """
        发送 API 请求（支持动态凭证）
        
        Args:
            endpoint: API 端点
            method: 请求方法（GET/POST/PUT/DELETE）
            params: URL 参数
            data: 请求体数据
            access_token: 动态传入的 access_token（可选）
            shop_id: 动态传入的 shop_id（可选）
            
        Returns:
            API 响应数据
        """
        token = access_token if access_token else self.access_token
        shop = shop_id if shop_id else self.shop_id
        
        if not token:
            logger.error("缺少 access_token")
            return {"code": 401, "message": "缺少 access_token", "data": None}
        
        if not shop:
            logger.error("缺少 shop_id")
            return {"code": 400, "message": "缺少 shop_id", "data": None}
        
        params = params or {}
        params['access_token'] = token
        params['shop_id'] = shop
        params['timestamp'] = int(time.time())
        params['app_key'] = self.app_key
        
        params['sign'] = self._generate_signature(params)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=data if data else None,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求失败：{str(e)}")
            return {"code": 500, "message": f"网络请求失败：{str(e)}", "data": None}
    
    def search_orders(self, 
                      start_time: Optional[str] = None, 
                      end_time: Optional[str] = None,
                      page_num: int = 1, 
                      page_size: int = 20,
                      access_token: str = None,
                      shop_id: str = None) -> Dict:
        """
        搜索订单
        
        Args:
            start_time: 订单创建起始时间 (格式：YYYY-MM-DD HH:MM:SS)
            end_time: 订单创建结束时间 (格式：YYYY-MM-DD HH:MM:SS)
            page_num: 页码
            page_size: 每页数量
            access_token: 动态传入的 access_token（可选）
            shop_id: 动态传入的 shop_id（可选）
            
        Returns:
            订单列表数据
        """
        params = {
            'page_num': page_num,
            'page_size': page_size
        }
        
        if start_time:
            params['create_time_from'] = start_time
        if end_time:
            params['create_time_to'] = end_time
        
        return self._make_request('/api/orders/search', method='GET', params=params,
                                  access_token=access_token, shop_id=shop_id)
    
    def get_order_detail(self, order_id: str, access_token: str = None, shop_id: str = None) -> Dict:
        """
        获取订单详情
        
        Args:
            order_id: 订单 ID
            access_token: 动态传入的 access_token（可选）
            shop_id: 动态传入的 shop_id（可选）
            
        Returns:
            订单详情数据
        """
        params = {
            'order_id': order_id
        }
        
        return self._make_request('/api/orders/detail', method='GET', params=params,
                                  access_token=access_token, shop_id=shop_id)
    
    def sync_orders(self, 
                    start_time: Optional[str] = None, 
                    end_time: Optional[str] = None,
                    access_token: str = None,
                    shop_id: str = None) -> List[Dict]:
        """
        同步订单数据（分页获取所有订单）
        
        Args:
            start_time: 订单创建起始时间
            end_time: 订单创建结束时间
            access_token: 动态传入的 access_token（可选）
            shop_id: 动态传入的 shop_id（可选）
            
        Returns:
            所有订单列表
        """
        all_orders = []
        page_num = 1
        page_size = 50
        
        while True:
            response = self.search_orders(start_time, end_time, page_num, page_size,
                                          access_token=access_token, shop_id=shop_id)
            
            if response.get('code') != 0:
                logger.error(f"获取订单失败：{response.get('message')}")
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
        
        logger.info(f"成功同步 {len(all_orders)} 条 TikTok 订单")
        return all_orders
