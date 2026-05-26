"""
初始化 TikTok OAuth 授权配置命令

使用方式:
    python manage.py init_tiktok_auth

功能:
    1. 生成授权链接引导用户授权
    2. 获取授权码(code)
    3. 使用 code 换取 access_token 和 refresh_token
    4. 获取店铺信息(shop_id, shop_cipher)
    5. 更新数据库配置或输出配置信息
"""
import webbrowser
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from server.order.tiktok_api_client import TiktokApiClient
from server.order.models import TiktokSyncConfig


class Command(BaseCommand):
    help = '初始化 TikTok OAuth 授权配置，获取 access_token、refresh_token、shop_id、shop_cipher'
    
    def handle(self, *args, **options):
        # 检查配置
        app_key = getattr(settings, 'TIKTOK_APP_KEY', '')
        app_secret = getattr(settings, 'TIKTOK_APP_SECRET', '')
        redirect_uri = getattr(settings, 'TIKTOK_REDIRECT_URI', '')
        
        if not app_key or app_key == 'your_app_key_here':
            raise CommandError('请先在 settings.py 中配置 TIKTOK_APP_KEY')
        
        if not app_secret or app_secret == 'your_app_secret_here':
            raise CommandError('请先在 settings.py 中配置 TIKTOK_APP_SECRET')
        
        if not redirect_uri:
            raise CommandError('请先在 settings.py 中配置 TIKTOK_REDIRECT_URI')
        
        self.stdout.write(self.style.SUCCESS(f"已加载配置:"))
        self.stdout.write(f"  TIKTOK_APP_KEY: {app_key}")
        self.stdout.write(f"  TIKTOK_REDIRECT_URI: {redirect_uri}")
        
        # 创建 API 客户端
        client = TiktokApiClient()
        
        # 1. 生成授权链接
        state = f"init_{int(time.time())}"
        auth_url = client.get_authorization_url(state=state)
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING("步骤1: 授权获取 code"))
        self.stdout.write(f"授权链接: {auth_url}")
        self.stdout.write("="*60)
        
        # 询问是否自动打开浏览器
        try:
            open_browser = input("是否自动打开浏览器进行授权? (y/n): ").strip().lower()
            if open_browser in ['y', 'yes']:
                self.stdout.write(f"正在打开授权页面...")
                webbrowser.open(auth_url)
        except KeyboardInterrupt:
            self.stdout.write("\n操作已取消")
            return
        
        # 2. 获取授权码
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING("步骤2: 输入授权码"))
        self.stdout.write("请在浏览器中完成授权后，从回调URL中获取 'code' 参数")
        self.stdout.write("例如: http://localhost:8000/api/order/tiktok/callback/?code=YOUR_CODE&state=xxx")
        self.stdout.write("="*60)
        
        code = input("请输入授权码(code): ").strip()
        
        if not code:
            raise CommandError('授权码不能为空')
        
        # 3. 使用 code 换取 access_token
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING("步骤3: 换取 access_token"))
        self.stdout.write("="*60)
        
        token_result = client.get_access_token(code)
        
        if token_result.get('code') != 0:
            error_msg = token_result.get('message', '未知错误')
            raise CommandError(f"获取 access_token 失败: {error_msg}")
        
        token_data = token_result.get('data', {})
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        shop_id_from_token = token_data.get('shop_id')
        shop_cipher_from_token = token_data.get('shop_cipher')
        
        self.stdout.write(self.style.SUCCESS("成功获取 Token!"))
        self.stdout.write(f"  access_token: {access_token[:20]}...")
        self.stdout.write(f"  refresh_token: {refresh_token[:20]}...")
        if shop_id_from_token:
            self.stdout.write(f"  shop_id (来自Token响应): {shop_id_from_token}")
        if shop_cipher_from_token:
            self.stdout.write(f"  shop_cipher (来自Token响应): {shop_cipher_from_token}")
        
        # 4. 获取店铺信息（推荐方式）
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING("步骤4: 获取店铺信息"))
        self.stdout.write("="*60)
        
        shops_result = client.get_authorized_shops(access_token)
        
        if shops_result.get('code') != 0:
            error_msg = shops_result.get('message', '未知错误')
            self.stdout.write(self.style.WARNING(f"获取店铺信息失败(可忽略): {error_msg}"))
            shop_id = shop_id_from_token
            shop_cipher = shop_cipher_from_token
        else:
            data = shops_result.get('data', {})
            shops = data.get('shops', [])
            
            if shops:
                shop = shops[0]
                shop_id = shop.get('shop_id') or shop_id_from_token
                shop_cipher = shop.get('shop_cipher') or shop_cipher_from_token
                
                self.stdout.write(self.style.SUCCESS("成功获取店铺信息!"))
                self.stdout.write(f"  店铺名称: {shop.get('shop_name', '未知')}")
                self.stdout.write(f"  shop_id: {shop_id}")
                self.stdout.write(f"  shop_cipher: {shop_cipher}")
                self.stdout.write(f"  区域: {shop.get('region', '未知')}")
            else:
                shop_id = shop_id_from_token
                shop_cipher = shop_cipher_from_token
                self.stdout.write(self.style.WARNING("未获取到店铺列表，使用Token响应中的信息"))
        
        # 5. 更新数据库配置
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING("步骤5: 保存配置"))
        self.stdout.write("="*60)
        
        try:
            config, created = TiktokSyncConfig.objects.update_or_create(
                id=1,
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'shop_id': shop_id,
                    'shop_cipher': shop_cipher,
                    'app_key': app_key,
                    'app_secret': app_secret,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS("已创建新配置"))
            else:
                self.stdout.write(self.style.SUCCESS("已更新配置"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"保存配置失败: {str(e)}"))
        
        # 6. 输出配置信息
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("配置完成!"))
        self.stdout.write("="*60)
        self.stdout.write("\n请将以下配置添加到环境变量或 settings.py 中:")
        self.stdout.write("\n```python")
        self.stdout.write(f"TIKTOK_ACCESS_TOKEN = '{access_token}'")
        self.stdout.write(f"TIKTOK_REFRESH_TOKEN = '{refresh_token}'")
        self.stdout.write(f"TIKTOK_SHOP_ID = '{shop_id}'")
        self.stdout.write(f"TIKTOK_SHOP_CIPHER = '{shop_cipher}'")
        self.stdout.write("```")
        self.stdout.write("\n或者使用环境变量:")
        self.stdout.write(f"  TIKTOK_ACCESS_TOKEN={access_token}")
        self.stdout.write(f"  TIKTOK_REFRESH_TOKEN={refresh_token}")
        self.stdout.write(f"  TIKTOK_SHOP_ID={shop_id}")
        self.stdout.write(f"  TIKTOK_SHOP_CIPHER={shop_cipher}")
