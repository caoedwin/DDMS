from django.urls import path
from . import views
app_name = 'CabinetManage'
urlpatterns = [


    path('CabinetManage_edit/', views.CabinetManage_edit, name='CabinetManage_edit'),
]