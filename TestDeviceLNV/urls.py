from django.urls import path
from . import views
app_name = 'TestDeviceLNV'
urlpatterns = [


    path('TestDeviceListLNV/', views.TestDeviceListLNV, name='TestDeviceListLNV')
]