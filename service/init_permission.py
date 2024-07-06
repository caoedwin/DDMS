from app01.models import UserInfo,Role,Permission,Imgs,Menu
def init_permission(request, user_obj):
    """
    初始化用户权限, 写入session
    :param request:
    :param user_obj:
    :return:
    """
    # print(user_obj)
    # print(user_obj.role.all())
    # permission_item_list = user_obj.role.values('perms__url',
    #                                             'perms__Menu_title',
    #                                             'perms__menu_id', 'perms__id').distinct()

    permission_item_list = user_obj.role.values('perms__url',
                                                 'perms__Menu_title',
                                                 'perms__menu_id').distinct()
    # print(permission_item_list)
    permission_url_list = []  # 用户权限url列表，--> 用于中间件验证用户权限
    permission_menu_list = []  # 用户权限url所属菜单列表 [{"title":xxx, "url":xxx, "menu_id": xxx},{},]
    # print(permission_item_list)
    for item in permission_item_list:
        # print(item)
        permission_url_list.append(item['perms__url'])
    #显示全部菜单第一步：permission_menu_list统计成所有菜单。
        if item['perms__menu_id']:
            temp = {"title": item['perms__Menu_title'],
                    "url": item["perms__url"],
                    "menu_id": item["perms__menu_id"]}
            permission_menu_list.append(temp)
    # for item in UserInfo.objects.filter(account="C1010S3").first().role.values('perms__url',
    #                                              'perms__Menu_title',
    #                                              'perms__menu_id').distinct():
    #     if item['perms__menu_id']:
    #         temp = {"title": item['perms__Menu_title'],
    #                 "url": item["perms__url"],
    #                 "menu_id": item["perms__menu_id"]}
    #         # print(item["perms__menu_id"])
    #         permission_menu_list.append(temp)

    menu_list = list(Menu.objects.values('id', 'title', 'parent_id'))
    # 注：session在存储时，会先对数据进行序列化，因此对于Queryset对象写入session， 加list()转为可序列化对象

    from django.conf import settings

    # 保存用户权限url列表
    # print('permission_url_list ------------------- ', permission_url_list)
    # print('permission_menu_list ------------------- ', permission_menu_list)
    # print('menu_list ------------------- ', menu_list)

    request.session[settings.SESSION_PERMISSION_URL_KEY] = permission_url_list#有权限的URL

    # 保存 权限菜单 和所有 菜单
    request.session[settings.SESSION_MENU_KEY] = {
        settings.ALL_MENU_KEY: menu_list,#所有的菜单
        settings.PERMISSION_MENU_KEY: permission_menu_list,#有权限的菜单，要想改成显示所有菜单，但是没权限提示没权限，需要将这个改成统计所有的菜单，但是结构跟上面的menu_list不同，所以不能用menu_list代替
    }

    # print('request.session[settings.SESSION_PERMISSION_URL_KEY] ------------------- ',
    #       request.session[settings.SESSION_PERMISSION_URL_KEY])

