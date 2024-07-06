from django.urls import path
from . import views
app_name = 'ComputerMS'
urlpatterns = [


    path('BorrowedComputer/', views.BorrowedComputer, name='BorrowedComputer'),
    # path('BorrowedPowerCode/', views.BorrowedPowerCode, name='BorrowedPowerCode'),
    path('R_Borrowed/', views.R_Borrowed, name='R_Borrowed'),

    path('R_Return/', views.R_Return, name='R_Return'),
    path('R_Destine/', views.R_Destine, name='R_Destine'),
    path('R_Receive/', views.R_Receive, name='R_Receive'),
    path('R_Transfer/', views.R_Transfer, name='R_Transfer'),
    path('M_edit/', views.M_edit, name='M_edit'),
    path('M_Borrow/', views.M_Borrow, name='M_Borrow'),
    path('M_Return/', views.M_Return, name='M_Return'),
    path('M_Transfer/', views.M_Transfer, name='M_Transfer'),
]