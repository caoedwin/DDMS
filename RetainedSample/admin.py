from django.contrib import admin
from .models import RetainedSample



@admin.register(RetainedSample)
class RetainedSampleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('Project','Owner','SampleName','Manufacturer','SampleBatch','SampleQuantity','Retainer','RetainStart',
                       'RetainPeriod','RetainPosition','BorrowedQuantity','RemainedQuantity','UnderApprovalQuantity')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Project','Owner','SampleName','Manufacturer','SampleBatch','SampleQuantity','Retainer','RetainStart',
                       'RetainPeriod','RetainPosition','BorrowedQuantity','RemainedQuantity','UnderApprovalQuantity',)
    # 列表里显示想要显示的字段

    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-Project',)
    #后台数据列表排序方式
    list_display_links = ('Project','Owner','SampleName','Manufacturer','SampleBatch','SampleQuantity')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Project','Owner','SampleName','Manufacturer','SampleBatch','SampleQuantity',)  # 过滤器
    search_fields = ('Project','Owner','SampleName','Manufacturer','SampleBatch','SampleQuantity',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选