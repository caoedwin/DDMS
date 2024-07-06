from django.contrib import admin
from .models import ComputerLNV, ComputerLNVHis

# Register your models here.
@admin.register(ComputerLNV)
class ComputerLNVAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('NID', 'MaterialPN', 'CPU', 'RAM', 'HDD', 'Wireless',
                        'LCD', 'OCR', 'Battery', 'Adaptor', 'Area', 'Carryif', 'Plant', 'Purpose',
                        'Category', 'BrwStatus', 'linshi_BrwStatus', 'IdleStatus', 'EFormNo',
                        'Usrname', 'BR_per_code', 'Btime', 'Rtime',
                        'Last_BR_per', 'Last_BR_per_code', 'Last_Borrow_date', 'Last_Return_date',
                        'Transefer_per_code', 'Receive_per_code', 'Sign_per_code',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('NID', 'MaterialPN', 'CPU', 'RAM', 'HDD', 'Wireless',
                        'LCD', 'OCR', 'Battery', 'Adaptor', 'Area', 'Carryif', 'Plant', 'Purpose',
                        'Category', 'BrwStatus', 'IdleStatus', 'EFormNo',
                        'Usrname', 'BR_per_code', 'Btime', 'Rtime',
                        'Last_BR_per', 'Last_BR_per_code', 'Last_Borrow_date', 'Last_Return_date',
                        'Transefer_per_code', 'Receive_per_code', 'Sign_per_code',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-NID',)
    #后台数据列表排序方式
    list_display_links = ('NID', 'MaterialPN', 'CPU', 'RAM', 'HDD', 'Wireless',
                        'LCD', 'OCR', 'Battery', 'Adaptor', 'Area', 'Carryif', 'Plant', 'Purpose',
                        'Category', 'BrwStatus', 'IdleStatus', 'EFormNo',
                        'Usrname', 'BR_per_code', 'Btime', 'Rtime',
                        'Last_BR_per', 'Last_BR_per_code', 'Last_Borrow_date', 'Last_Return_date',
                        'Transefer_per_code', 'Receive_per_code', 'Sign_per_code',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('NID', 'Usrname',)  # 过滤器
    search_fields = ('NID', 'Usrname',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(ComputerLNVHis)
class DeviceLNVHisAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('NID', 'EFormNo', 'Carryif',  'Usrname',
                        'BR_per_code', 'Btime', 'Rtime', 'Transefer_per_code', 'Receive_per_code', 'Comments',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('NID', 'EFormNo', 'Carryif',  'Usrname',
                        'BR_per_code', 'Btime', 'Rtime', 'Transefer_per_code', 'Receive_per_code', 'Comments',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-NID',)
    #后台数据列表排序方式
    list_display_links = ('NID', 'EFormNo', 'Carryif', 'Usrname',
                        'BR_per_code', 'Btime', 'Rtime', 'Transefer_per_code', 'Receive_per_code', 'Comments',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('NID', 'Usrname',)  # 过滤器
    search_fields = ('NID', 'Usrname',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选
