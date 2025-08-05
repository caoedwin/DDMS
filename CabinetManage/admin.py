from django.contrib import admin
from .models import Cabinet, CabinetGrid, GridRecord

# Register your models here.
@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('name', 'location', 'description', 'rows', 'cols')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('name', 'location', 'description', 'rows', 'cols', 'created_at', 'updated_at')
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-name',)
    #后台数据列表排序方式
    list_display_links = ('name', 'location', 'description', 'rows', 'cols', 'created_at', 'updated_at')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('name',)  # 过滤器
    search_fields = ('name',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(CabinetGrid)
class CabinetGridAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('cabinet', 'row', 'col', 'position', 'status', 'Customer', 'ProCode', 'CampalCode', 'Brow_at',
                        'BrowReson', 'Take_at', 'TakeReson', 'Back_at', 'user', 'phone', 'notes', 'creator',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('cabinet', 'row', 'col', 'position', 'status', 'Customer', 'ProCode', 'CampalCode', 'Brow_at',
                        'BrowReson', 'Take_at', 'TakeReson', 'Back_at', 'user', 'phone', 'notes', 'creator', 'created_at', 'updated_at',)
    # 列表里显示想要显示的字段


    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-cabinet',)
    #后台数据列表排序方式
    list_display_links = ('cabinet', 'row', 'col', 'position', 'status', 'Customer', 'ProCode', 'CampalCode', 'Brow_at',
                        'BrowReson', 'Take_at', 'TakeReson', 'Back_at')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('cabinet',)  # 过滤器
    search_fields = ('cabinet',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(GridRecord)
class GridRecordAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('grid','action','old_status','new_status','Customer','ProCode','CampalCode','Brow_at',
                       'BrowReson','Take_at','TakeReson','Back_at','user', 'phone', 'notes',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('grid','action','old_status','new_status','Customer','ProCode','CampalCode','Brow_at',
                       'BrowReson','Take_at','TakeReson','Back_at','user', 'phone', 'notes', 'created_at',)
    # 列表里显示想要显示的字段

    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-grid',)
    #后台数据列表排序方式
    list_display_links = ('grid',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('grid',)  # 过滤器
    search_fields = ('grid',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选
