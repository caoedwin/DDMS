from django.urls import path
from . import views
app_name = 'TUMHistory'
urlpatterns = [

    path('SummaryTUM/', views.SummaryTUM, name='SummaryTUM'),
    path('SummaryMateria/', views.SummaryMateria, name='SummaryTUM'),
]