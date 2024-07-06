from django.urls import path
from . import views
app_name = 'DeviceLNV'
urlpatterns = [


    path('Borrowed/', views.Borrowed, name='Borrowed'),
]