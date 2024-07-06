from django.urls import path
from . import views
app_name = 'DeviceCQT88'
urlpatterns = [

    path('BorrowedDeviceCQT88/', views.BorrowedDeviceCQT88, name='BorrowedDeviceLNV'),
    # path('BorrowedPowerCode/', views.BorrowedPowerCode, name='BorrowedPowerCode'),
    path('R_Borrowed/', views.R_Borrowed, name='R_Borrowed'),
    path('R_Return/', views.R_Return, name='R_Return'),
    path('R_Keep/', views.R_Keep, name='R_Keep'),
    path('R_Destine/', views.R_Destine, name='R_Destine'),
    path('M_Borrow/', views.M_Borrow, name='M_Borrow'),
    path('M_Return/', views.M_Return, name='M_Return'),
    path('M_Category/', views.M_Category, name='M_Category'),
    path('M_edit/', views.M_edit, name='M_edit'),
    path('M_Keep/', views.M_Keep, name='M_Keep'),
]