from django.contrib import admin
from .models import UserInfo, Role, Permission, Menu, Imgs

from extraadminfilters.filters import UnionFieldListFilter

# Register your models here.
admin.site.site_url = '/index/'

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('title','parent',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('title',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-title',)
    #后台数据列表排序方式
    list_display_links = ('title',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('title',)  # 过滤器
    search_fields = ('title',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Menu_title','url','menu',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Menu_title','url',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-url',)
    #后台数据列表排序方式
    list_display_links = ('Menu_title','url',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Menu_title','url',)  # 过滤器
    search_fields = ('Menu_title','url',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('name','perms')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('name',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-name',)
    #后台数据列表排序方式
    list_display_links = ('name',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('name',)  # 过滤器
    search_fields = ('name',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选
    filter_horizontal = ('perms',)

@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('account','password','CNname','username','Tel','Seat', 'email','role',"Photo")
        }),
        ('Advanced options',{
            'classes': ('collapse',),
            'fields' : ('department','is_active','is_staff','is_SVPuser')
        }),
    )
    filter_horizontal = ('role',)
    list_display = ('account', 'password', 'CNname','username','Tel','Seat', 'email', 'show_role')
    '''展示show_role'''

    def show_role(self, obj):
        role_list = []
        for role in obj.role.all():
            role_list.append(role.name)
        return '， '.join(role_list)

    show_role.short_description = '角色'  # 设置表头
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-account',)
    #后台数据列表排序方式
    list_display_links = ('account','password','CNname','username','email')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('account','password','CNname','username','email','Seat', 'role')  # 过滤器
    search_fields = ('account','password','CNname','username','email','Seat', 'role__name')  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选
    filter_horizontal = ('role',)


