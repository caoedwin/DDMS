from django.contrib import admin
from .models import DeviceCQT88, DeviceCQT88His, DeviceIntfCtgryList, DeviceDevCtgryList, DeviceDevpropertiesList, DeviceDevVendorList, DeviceDevsizeList

# Register your models here.
@admin.register(DeviceCQT88)
class DeviceCQT88Admin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Customer', 'Plant', 'NID', 'DevID', 'IntfCtgry', 'DevCtgry', 'Devproperties', 'DevVendor',
                        'Devsize', 'DevModel', 'DevName', 'HWVer', 'FWVer', 'DevDescription', 'PckgIncludes', 'expirdate',
                        'DevPrice', 'Source', 'Pchsdate', 'PN', 'LSTA', 'ApplicationNo', 'DeclarationNo',
                        'AssetNum', 'addnewname', 'addnewdate', 'EOL', 'Comment', 'uscyc', 'UsrTimes', 'DevStatus', 'BrwStatus',
                        'Usrname', 'BR_per_code', 'ProjectCode', 'Phase', 'useday', 'Plandate', 'Btime', 'Rtime',
                        'Last_BR_per', 'Last_BR_per_code', 'Last_Predict_return', 'Last_Borrow_date', 'Last_Return_date',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Customer', 'Plant', 'NID', 'DevID', 'IntfCtgry', 'DevCtgry', 'Devproperties', 'DevVendor',
                        'Devsize', 'DevModel', 'DevName', 'HWVer', 'FWVer', 'DevDescription', 'PckgIncludes', 'expirdate',
                        'DevPrice', 'Source', 'Pchsdate', 'PN', 'LSTA', 'ApplicationNo', 'DeclarationNo',
                        'AssetNum', 'addnewname', 'addnewdate', 'Comment', 'uscyc', 'UsrTimes', 'DevStatus', 'BrwStatus',
                        'Usrname', 'BR_per_code', 'ProjectCode', 'Phase', 'useday', 'Plandate', 'Btime', 'Rtime',
                        'Last_BR_per', 'Last_BR_per_code', 'Last_Predict_return', 'Last_Borrow_date', 'Last_Return_date',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-NID',)
    #后台数据列表排序方式
    list_display_links = ('Customer', 'Plant', 'NID', 'DevID', 'IntfCtgry', 'DevCtgry', 'Devproperties', 'DevVendor',
                        'Devsize', 'DevModel',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Customer', 'Plant', 'NID', 'DevID', 'IntfCtgry', 'DevCtgry', 'Devproperties', 'DevVendor',
                        'Devsize', 'DevModel',)  # 过滤器
    search_fields = ('Customer', 'Plant', 'NID', 'DevID', 'IntfCtgry', 'DevCtgry', 'Devproperties', 'DevVendor',
                        'Devsize', 'DevModel',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DeviceCQT88His)
class DeviceCQT88HisAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('NID', 'DevID', 'DevModel', 'DevName', 'uscyc', 'Btime', 'Plandate', 'Rtime', 'Usrname',
                        'BR_per_code', 'ProjectCode', 'Phase',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('NID', 'DevID', 'DevModel', 'DevName', 'uscyc', 'Btime', 'Plandate', 'Rtime', 'Usrname',
                        'BR_per_code', 'ProjectCode', 'Phase',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-NID',)
    #后台数据列表排序方式
    list_display_links = ('NID', 'DevID', 'DevModel', 'DevName', 'uscyc', 'Btime', 'Rtime', 'Usrname',
                        'BR_per_code',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('NID', 'DevID', 'DevModel', 'DevName', 'uscyc', 'Btime', 'Rtime', 'Usrname',
                        'BR_per_code',)  # 过滤器
    search_fields = ('NID', 'DevID', 'DevModel', 'DevName', 'uscyc', 'Btime', 'Rtime', 'Usrname',
                        'BR_per_code',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DeviceIntfCtgryList)
class DeviceIntfCtgryListAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('IntfCtgry',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('IntfCtgry',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-IntfCtgry',)
    #后台数据列表排序方式
    list_display_links = ('IntfCtgry',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('IntfCtgry',)  # 过滤器
    search_fields = ('IntfCtgry',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DeviceDevCtgryList)
class DeviceDevCtgryListAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('DevCtgry', 'IntfCtgry_P')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('DevCtgry', 'IntfCtgry_P')
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-DevCtgry',)
    #后台数据列表排序方式
    list_display_links = ('DevCtgry',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('DevCtgry',)  # 过滤器
    search_fields = ('DevCtgry',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DeviceDevpropertiesList)
class DeviceDevpropertiesListAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Devproperties', 'DevCtgry_P')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Devproperties', 'DevCtgry_P')
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-Devproperties',)
    #后台数据列表排序方式
    list_display_links = ('Devproperties',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Devproperties',)  # 过滤器
    search_fields = ('Devproperties',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DeviceDevVendorList)
class DeviceDevVendorListAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('DevVendor', 'Devproperties_P')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('DevVendor', 'Devproperties_P')
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-DevVendor',)
    #后台数据列表排序方式
    list_display_links = ('DevVendor',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('DevVendor',)  # 过滤器
    search_fields = ('DevVendor',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(DeviceDevsizeList)
class DeviceDevsizeListAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Devsize', 'DevVendor_P')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Devsize', 'DevVendor_P')
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-Devsize',)
    #后台数据列表排序方式
    list_display_links = ('Devsize',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Devsize',)  # 过滤器
    search_fields = ('Devsize',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选