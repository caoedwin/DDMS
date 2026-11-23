from django.contrib import admin
from .models import TestDeviceLNV

# Register your models here.
@admin.register(TestDeviceLNV)
class TestDeviceLNVAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Category', 'Class', 'Type', 'Covered_range_for_case', 'Require_State', 'Comments', 'Remark', 'ODM_status',
                        'Purchase_Plan', 'Device_Price', 'Act_Status', 'Device_Know_Issue', 'Device1', 'Device2', 'Device3', 'Device4', 'Device5', 'Device6',
                        'Device7', 'Device8', 'Device9', 'Device10', )
        }),
        # ===== 2026-11 新增：設備明細 8 列 =====
        ('設備明細', {
            'fields' : ('Interface_Type', 'Device_Category', 'Device_Attribute', 'Device_Capacity',
                        'Device_Brand', 'Device_Model', 'Device_Name', 'Device_Description', )
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Category', 'Class', 'Type', 'Covered_range_for_case', 'Require_State', 'Comments', 'Remark', 'ODM_status',
                        'Purchase_Plan', 'Device_Price', 'Act_Status', 'Device_Know_Issue', 'Device1', 'Device2', 'Device3', 'Device4', 'Device5', 'Device6',
                        'Device7', 'Device8', 'Device9', 'Device10',
                        'Interface_Type', 'Device_Category', 'Device_Attribute', 'Device_Capacity',
                        'Device_Brand', 'Device_Model', 'Device_Name', 'Device_Description')
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-Category',)
    #后台数据列表排序方式
    list_display_links = ('Category', 'Class', 'Type', 'Covered_range_for_case', 'Require_State', 'Comments', 'Remark', 'ODM_status',
                        'Purchase_Plan', 'Device_Price', 'Act_Status', 'Device1', 'Device2', 'Device3', 'Device4', 'Device5', 'Device6',
                        'Device7', 'Device8', 'Device9', 'Device10',
                        'Interface_Type', 'Device_Category', 'Device_Attribute', 'Device_Brand', 'Device_Model')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Category', 'Class',)  # 过滤器
    search_fields = ('Category', 'Class', 'Device_Brand', 'Device_Model')  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

