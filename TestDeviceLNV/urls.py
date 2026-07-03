from django.urls import path
from . import views
app_name = 'TestDeviceLNV'
urlpatterns = [
    path('TestDeviceListLNV/', views.TestDeviceListLNV, name='TestDeviceListLNV'),
    # JSON 接口（已提供）
    path('device-score/', views.device_score_view, name='device_score_api'),
    path('device-demand-week/', views.device_demand_week_view, name='device_demand_week_api'),
    # 页面路由
    path('device-score-page/', views.device_score_page, name='device_score_page'),
    path('device-demand-week-page/', views.device_demand_week_page, name='device_demand_week_page'),
]