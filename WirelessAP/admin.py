from django.contrib import admin

# Register your models here.
from .models import WirelessAP
@admin.register(WirelessAP)
class WirlessAPAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("Room", "Owner_Num", "Owner_EN", "Category", "Net_Area", "AP_Model", "AP_SSID", "Channel_24G", "Channel_5G", "Channel_6G",
                       "AP_Psw", "AP_IP", "Brw_Owner_Num", "Brw_Owner_CN", "Start_Time", "End_Time", "Project", "Case",)
        }),
        ('Advanced options',{
            'classes': ('collapse',),
            'fields' : ('Comments',)
        }),
    )
    list_display = (
        "Room", "Owner_Num", "Owner_EN", "Category", "Net_Area", "AP_Model", "AP_SSID", "Channel_24G", "Channel_5G",
        "Channel_6G",
        "AP_Psw", "AP_IP", "Brw_Owner_Num", "Brw_Owner_CN", "Start_Time", "End_Time", "Project", "Case",
    )
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-AP_SSID', "-AP_IP",)
    # 后台数据列表排序方式
    list_display_links = ("Room", "Owner_Num", "Owner_EN", "Category", "Net_Area", "AP_Model", "AP_SSID", "Channel_24G", "Channel_5G",
        "Channel_6G",
        "AP_Psw", "AP_IP",)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ("Room", "Owner_Num", "Category", "AP_Model", "AP_SSID","AP_IP",)  # 过滤器
    search_fields = ("Room", "Owner_Num", "Category", "AP_Model", "AP_SSID","AP_IP",)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选