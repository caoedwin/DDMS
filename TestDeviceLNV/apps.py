# apps.py
from django.apps import AppConfig
import threading

class TestDeviceLNVConfig(AppConfig):
    name = 'TestDeviceLNV'

    def ready(self):
        # 异步预热缓存（不阻塞启动）
        def warmup():
            from django.core.cache import cache
            from .views import fetch_testprojects, get_requirement_items
            try:
                # 检查缓存是否存在，不存在则预热
                if not cache.get('testprojects_data'):
                    fetch_testprojects()
                if not cache.get('requirement_items_v2'):
                    get_requirement_items()
            except Exception as e:
                print(f"预热缓存失败: {e}")

        # 启动后台线程
        thread = threading.Thread(target=warmup)
        thread.daemon = True  # 主进程退出时自动结束
        thread.start()