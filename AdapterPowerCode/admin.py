from django.contrib import admin

# Register your models here.
from .models import PICS, AdapterPowerCodeBR

admin.site.register(PICS)

@admin.register(AdapterPowerCodeBR)
class AdapterPowerCodeBRAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Customer','Changjia','MaterialPN','Description','Power','Number',"Location",)
        }),
        ('Advanced options',{
            'classes': ('collapse',),#折叠
            'fields' : ('Project_Code','Phase','OAP', "OAPcode", "Device_Status", 'Pinming',
                        'BR_Status','BR_per','BR_per_code', 'Predict_return','Borrow_date',"Return_date",'Last_BR_per','Last_BR_per_code','Last_Predict_return','Last_Borrow_date','Last_Return_date','Photo',)
        }),
    )
    list_display = ('Changjia','MaterialPN','Description','Power','Number',"Location",'Customer','Project_Code','Phase','OAP', "OAPcode","Device_Status", 'Pinming',
                        'BR_Status','BR_per','BR_per_code', 'Predict_return','Borrow_date',"Return_date",'Last_BR_per','Last_BR_per_code','Last_Predict_return','Last_Borrow_date','Last_Return_date')
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-Number',)
    #后台数据列表排序方式
    list_display_links = ('Changjia','MaterialPN','Description','Power','Number',"Location",'Customer','Project_Code','Phase','OAP',"Device_Status", 'Pinming',
                        'BR_Status','BR_per','Predict_return','Borrow_date',"Return_date",'Last_BR_per','Last_Predict_return','Last_Borrow_date','Last_Return_date')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Changjia','MaterialPN','Power','Number',"Device_Status",'BR_per'
                        ,'BR_Status', "OAPcode",)  # 过滤器
    search_fields = ('Changjia','MaterialPN','Power','Number',"Device_Status",'BR_per'
                        ,'BR_Status', "OAPcode",'Pinming',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选