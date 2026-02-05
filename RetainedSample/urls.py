from django.urls import path
from . import views
app_name = 'RetainedSample'
urlpatterns = [


    path('RetainedSample_summary/', views.RetainedSample_summary, name='RetainedSample_summary'),
    # path('RetainedSample_MyBorrow/', views.RetainedSample_MyBorrow, name='RetainedSample_MyBorrow'),
    # path('RetainedSample_MyApproval/', views.RetainedSample_MyApproval, name='RetainedSample_MyApproval'),
    # path('RetainedSample_BRRecord/', views.RetainedSample_BRRecord, name='RetainedSample_BRRecord'),
    # path('RetainedSample_ScrapRecord/', views.RetainedSample_ScrapRecord, name='RetainedSample_ScrapRecord'),
]