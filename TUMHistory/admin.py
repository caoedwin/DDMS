from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from .models import *
@admin.register(Unitbudget)
class UnitbudgetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("Customer", "Year", "Category", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                       "Oct", "Nov", "Dec",)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Comments',)
        # }),
    )
    list_display = (
        "Customer", "Year", "Category", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                       "Oct", "Nov", "Dec",
    )
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-Year',)
    # 后台数据列表排序方式
    list_display_links = ("Customer", "Year", "Category", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                       "Oct", "Nov", "Dec",)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ("Customer", "Year", "Category",)  # 过滤器
    search_fields = ("Customer", "Year", "Category",)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(UnitInDQA_Tum)
class UnitInDQA_TumAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("ItemID", "SiteName", "FunctionName", "CustomerCode", "SN", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "TUMsystemCode", "CostCenter", "ProjectCode", "Description",
                       "QTY", "Phase", "EOPDate",)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Comments',)
        # }),
    )
    list_display = (
        "ItemID", "SiteName", "FunctionName", "CustomerCode", "SN", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "TUMsystemCode", "CostCenter", "ProjectCode", "Description",
                       "QTY", "Phase", "EOPDate",
    )
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-ItemID',)
    # 后台数据列表排序方式
    list_display_links = ("ItemID", "SiteName", "FunctionName", "CustomerCode", "SN", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "TUMsystemCode", "CostCenter", "ProjectCode", "Description",
                       "QTY", "Phase", "EOPDate",)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ("CustomerCode", "SN", "PN", "Status", "DeptNo", "ProjectCode",)  # 过滤器
    search_fields = ("ItemID", "CustomerCode", "SN", "PN", "Status", "DeptNo", "ProjectCode",)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DQAUnit_TUMHistory)
class DQAUnit_TUMHistoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("ItemID", "SiteName", "FunctionName", "CustomerCode", "SN", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "TUMsystemCode", "CostCenter", "ProjectCode", "Description",
                       "QTY", "Phase", "EOPDate",)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Comments',)
        # }),
    )
    list_display = (
        "ItemID", "SiteName", "FunctionName", "CustomerCode", "SN", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "TUMsystemCode", "CostCenter", "ProjectCode", "Description",
                       "QTY", "Phase", "EOPDate",
    )
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-ItemID',)
    # 后台数据列表排序方式
    list_display_links = ("ItemID", "SiteName", "FunctionName", "CustomerCode", "SN", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "TUMsystemCode", "CostCenter", "ProjectCode", "Description",
                       "QTY", "Phase", "EOPDate",)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ("CustomerCode", "SN", "PN", "Status", "DeptNo", "ProjectCode",)  # 过滤器
    search_fields = ("ItemID", "CustomerCode", "SN", "PN", "Status", "DeptNo", "ProjectCode",)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(MateriaInDQA_Tum)
class MateriaInDQA_TumAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("SiteName", "FunctionName", "CustomerCode", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "ItemNo", "CostCenter", "ProjectCode", "Description",
                       "QTY", "PhaseName", "EOPDate",)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Comments',)
        # }),
    )
    list_display = (
        "SiteName", "FunctionName", "CustomerCode", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "ItemNo", "CostCenter", "ProjectCode", "Description",
                       "QTY", "PhaseName", "EOPDate",
    )
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-PN',)
    # 后台数据列表排序方式
    list_display_links = ("SiteName", "FunctionName", "CustomerCode", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "ItemNo", "CostCenter", "ProjectCode", "Description",
                       "QTY", "PhaseName", "EOPDate",)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ("CustomerCode", "PN", "Status", "DeptNo", "ProjectCode",)  # 过滤器
    search_fields = ("CustomerCode", "PN", "Status", "DeptNo", "ProjectCode",)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DQAMateria_TUMHistory)
class DQAMateria_TUMHistoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("ReturnID", "SiteName", "FunctionName", "CustomerCode", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "ItemNo", "CostCenter", "ProjectCode", "Description",
                       "QTY", "PhaseName", "EOPDate",)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Comments',)
        # }),
    )
    list_display = (
        "ReturnID", "SiteName", "FunctionName", "CustomerCode", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "ItemNo", "CostCenter", "ProjectCode", "Description",
                       "QTY", "PhaseName", "EOPDate",
    )
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-ReturnID',)
    # 后台数据列表排序方式
    list_display_links = ("SiteName", "FunctionName", "CustomerCode", "PN", "CurrentKeeper", "CurrentKeeper_CN", "ApplyReasonCategory", "ApplyReason",
                       "InData", "ReturnOffline", "ReturnData", "Status", "DeptNo", "ItemNo", "CostCenter", "ProjectCode", "Description",
                       "QTY", "PhaseName", "EOPDate",)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ("CustomerCode", "PN", "Status", "DeptNo", "ProjectCode",)  # 过滤器
    search_fields = ("ReturnID", "CustomerCode", "PN", "Status", "DeptNo", "ProjectCode",)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选