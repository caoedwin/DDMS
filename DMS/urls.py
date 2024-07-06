"""DMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include , re_path
from django.conf.urls.static import static
# from django.conf.urls import url, include
#留意上面这行比原来多了一个include
from django.views.static import serve
#导入静态文件模块
from django.conf import settings
#导入配置文件里的文件上传配置
from app01 import views
# import notifications.urls

urlpatterns = [
    # path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('admin/', admin.site.urls),
    # path('ueditor/', include('DjangoUeditor.urls')), #添加DjangoUeditor的URL
    path(r'login/', views.login),
    path(r'signinLNV/', views.signinLNV),
    path(r'signinABO/', views.signinABO),
    path(r'signinA31/', views.signinA31),
    path(r'signinCQT88/', views.signinCQT88),
    path(r'', views.login),
    path(r'logout/', views.logout),
    path(r'Change_Password/', views.Change_Password),
    path(r'Change_Skin/', views.Change_Skin),
    path(r'index/', views.index),
    path(r'Summary/', views.Summary),
    path(r'Summary_ABO/', views.Summary_ABO),
    path(r'SysAdmin/UserInfo-edit/', views.UserInfoedit),
    re_path('^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),#增加此行
    re_path('^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),#增加此行
    path('AdapterPowerCode/', include('AdapterPowerCode.urls', namespace='AdapterPowerCode')),
    path('DeviceLNV/', include('DeviceLNV.urls', namespace='DeviceLNV')),
    path('DeviceA39/', include('DeviceA39.urls', namespace='DeviceA39')),
    path('DeviceABO/', include('DeviceABO.urls', namespace='DeviceABO')),
    path('DeviceCQT88/', include('DeviceCQT88.urls', namespace='DeviceCQT88')),
    path('ComputerMS/', include('ComputerMS.urls', namespace='ComputerMS')),
    path('ChairCabinetMS/', include('ChairCabinetMS.urls', namespace='ChairCabinetMS')),
    path('WirelessAP/', include('WirelessAP.urls', namespace='WirelessAP')),
    path('TUMHistory/', include('TUMHistory.urls', namespace='TUMHistory')),
]#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    media_root = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT)
#     os.path.join()
#     函数：连接两个或更多的路径名组件
#
#     1.
#     如果各组件名首字母不包含’ / ’，则函数会自动加上
#
# 　　　　　　　　　2.
# 如果有一个组件是一个绝对路径，则在它之前的所有组件均会被舍弃
#
# 　　　　　　　　　3.
# 如果最后一个组件为空，则生成的路径以一个’ / ’分隔符结尾
#     print(media_root)
    urlpatterns += static(settings.MEDIA_URL, document_root=media_root)
    # print (urlpatterns)
