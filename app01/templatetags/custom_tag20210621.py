from django import template
from django.conf import settings
import re, os
from django.utils.safestring import mark_safe

register = template.Library()


def get_structure_data(request):
    """处理菜单结构"""
    menu = request.session[settings.SESSION_MENU_KEY]
    all_menu = menu[settings.ALL_MENU_KEY]
    permission_url = menu[settings.PERMISSION_MENU_KEY]
    # print (all_menu)
    # print(permission_url)
    # all_menu = [
    #     {'id': 1, 'title': '订单管理', 'parent_id': None},
    #     {'id': 2, 'title': '库存管理', 'parent_id': None},
    #     {'id': 3, 'title': '生产管理', 'parent_id': None},
    #     {'id': 4, 'title': '生产调查', 'parent_id': None}
    # ]

    # 定制数据结构
    all_menu_dict = {}
    # print("all menue:",all_menu)
    for item in all_menu:
        item['status'] = False#False,False表示不显示，True表示显示，初始默认不显示，后面判断有权限在改成True，要想不管有没有权限都显示，直接全设为True
        item['open'] = False
        item['children'] = []
        all_menu_dict[item['id']] = item
    # print(all_menu_dict)
    # print(permission_url)
    # all_menu_dict = {
    #     1: {'id': 1, 'title': '订单管理', 'parent_id': None, 'status': False, 'open': False, 'children': []},
    #     2: {'id': 2, 'title': '库存管理', 'parent_id': None, 'status': False, 'open': False, 'children': []},
    #     3: {'id': 3, 'title': '生产管理', 'parent_id': None, 'status': False, 'open': False, 'children': []},
    #     4: {'id': 4, 'title': '生产调查', 'parent_id': None, 'status': False, 'open': False, 'children': []}
    # }

    # permission_url = [
    #     {'title': '查看订单', 'url': '/order', 'menu_id': 1},
    #     {'title': '查看库存清单', 'url': '/stock/detail', 'menu_id': 2},
    #     {'title': '查看生产订单', 'url': '/produce/detail', 'menu_id': 3},
    #     {'title': '产出管理', 'url': '/survey/produce', 'menu_id': 4},
    #     {'title': '工时管理', 'url': '/survey/labor', 'menu_id': 4},
    #     {'title': '入库', 'url': '/stock/in', 'menu_id': 2},
    #     {'title': '排单', 'url': '/produce/new', 'menu_id': 3}
    # ]

    request_rul = request.path_info

    for url in permission_url:
        # 添加两个状态：显示 和 展开
        url['status'] = True
        pattern = url['url']
        if re.match(pattern, request_rul):
            url['open'] = True
        else:
            url['open'] = False

        # 将url添加到菜单下
        all_menu_dict[url['menu_id']]["children"].append(url)

        # 显示菜单：url 的菜单及上层菜单 status: true
        pid = url['menu_id']
        while pid:
            all_menu_dict[pid]['status'] = True
            pid = all_menu_dict[pid]['parent_id']

        # 展开url上层菜单：url['open'] = True, 其菜单及其父菜单open = True
        if url['open']:
            ppid = url['menu_id']
            while ppid:
                all_menu_dict[ppid]['open'] = True
                ppid = all_menu_dict[ppid]['parent_id']
    # print(permission_url)
    # 整理菜单层级结构：没有parent_id 的为根菜单， 并将有parent_id 的菜单项加入其父项的chidren内
    menu_data = []
    for i in all_menu_dict:
        if all_menu_dict[i]['parent_id']:
            pid = all_menu_dict[i]['parent_id']
            parent_menu = all_menu_dict[pid]
            parent_menu['children'].append(all_menu_dict[i])
        else:
            menu_data.append(all_menu_dict[i])
        # print(menu_data)#如果append括号里面的内容后面发生了变更，append前面的内容也会跟着发生变化
    # print(len(menu_data))
    # testdic = {"a":1,"b":2}
    # print(testdic.items())

    for i in menu_data:
        # print(len(i),i)
        # print(i["title"])
        # print(len(i["children"]), i["children"])
        #
        # for j in i["children"]:
        #     if "children" in j.keys():
        #         print(len(j['children']), j['children'])
        if i['children']:
            # print(i)
            if "children" in i['children'][0].keys():#edwin：对有三级菜单，按照第三季级菜单的个数对二级菜单排序，只有二级的不需要排序
                i["children"].sort(key=lambda x: len(x["children"]))
                # for m in i["children"]:
                #     print(len(m["children"]), m["children"])
                for j in i['children']:#第三级菜单则按照title字母顺序排序
                    j['children'].sort(key=lambda x: x["title"])
    menu_data.sort(key=lambda x: x["title"])  # 第一级菜单按照title字母顺序排序
    # print (menu_data)
    return menu_data


def get_menu_html(menu_data):
    """显示：菜单 + [子菜单] + 权限(url)"""
    option_str = """
          <li><a class="sidebar-sub-toggle"><i class={Class}></i>{menu_title}<span class="sidebar-collapse-icon ti-angle-down"></span></a>
                <ul>
                    {sub_menu}
                </ul>
            </li>
    """

    url_str = """
        <li><a  href="{permission_url}">{permission_title}</a></li>
    """#Class = "ti-arrow-circle-right"

    """
     menu_data = [
        {'id': 1, 'title': '订单管理', 'parent_id': None, 'status': True, 'open': False,
         'children': [{'title': '查看订单', 'url': '/order', 'menu_id': 1, 'status': True, 'open': False}]},
        {'id': 2, 'title': '库存管理', 'parent_id': None, 'status': True, 'open': True,
         'children': [{'title': '查看库存清单', 'url': '/stock/detail', 'menu_id': 2, 'status': True, 'open': False},
                      {'title': '入库', 'url': '/stock/in', 'menu_id': 2, 'status': True, 'open': True}]},
        {'id': 3, 'title': '生产管理', 'parent_id': None, 'status': True, 'open': False,
         'children': [{'title': '查看生产订单', 'url': '/produce/detail', 'menu_id': 3, 'status': True, 'open': False},
                      {'title': '排单', 'url': '/produce/new', 'menu_id': 3, 'status': True, 'open': False}]},
        {'id': 4, 'title': '生产调查', 'parent_id': None, 'status': True, 'open': False,
         'children': [{'title': '产出管理', 'url': '/survey/produce', 'menu_id': 4, 'status': True, 'open': False},
                      {'title': '工时管理', 'url': '/survey/labor', 'menu_id': 4, 'status': True, 'open': False}]}
    ]
    """
    # print("menu_data:",menu_data)
    menu_html = ''
    for item in menu_data:
        if not item['status']: # 如果用户权限不在某个菜单下，即item['status']=False, 不显示
            continue
        else:
            if item.get('url'): # 说明循环到了菜单最里层的url
                menu_html += url_str.format(permission_url=item['url'],
                                            # active="rbac-active" if item['open'] else "",
                                            permission_title=item['title'][4:])
                # print (menu_html)
                # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            else:
                if item.get('children'):
                    sub_menu = get_menu_html(item['children'])
                    Class=""
                    if item['title']=='Lesson Learn':
                        Class="ti-file"
                    elif item['title'] == 'SW&ME':
                        Class ="ti-agenda"
                    elif item['title'] == 'Compatibility':
                        Class ="ti-layout-grid4-alt"
                    elif item['title'] == 'QIL':
                        Class ="ti-layout-grid2-alt"
                    elif item['title'] == 'Reliability Test Data':
                        Class = "ti-archive"
                    elif item['title'] == 'Package G Value':
                        Class = "ti-layout"
                    if item['title'] == 'Bouncing':
                        Class = "ti-panel"
                    elif item['title'] == 'CDM':
                        Class = "ti-view-list-alt"
                    elif item['title'] == 'XQM':
                        Class ="ti-files"
                    elif item['title'] == 'CQM':
                        Class = "ti-target"
                    elif item['title'] == 'MQM':
                        Class = "ti-bar-chart-alt"
                    elif item['title'] == 'DriverToolList':
                        Class = "ti-layout-cta-right"
                    elif item['title'] == 'Others':
                        Class = "ti-map"
                    elif item['title'] == 'Known issue list':
                        Class = "ti-layout-column3"
                    elif item['title'] == 'Runin Report':
                        Class = "ti-layout-list-thumb"
                    elif item['title'] == 'Test Plan':
                        Class = "ti-bar-chart-alt"
                    elif item['title'] == 'ME':
                        Class = "ti-layout-media-overlay-alt"
                    elif item['title'] == 'SW':
                        Class ="ti-layout-width-default"
                    elif item['title'] == 'INV':
                        Class ="ti-layout-list-large-image"
                    elif item['title'] == 'SpecDownload':
                        Class ="ti-layout-accordion-list"
                    elif item['title'] == 'Issue Notes':
                        Class ="ti-layout-column3"
                    elif item['title'] == 'Issue List':
                        Class ="ti-bookmark"
                    elif item['title'] == 'Known Issue':
                        Class ="ti-envelope"
                    elif item['title'] == 'DepartmentManage':
                        Class ="ti-cloud"
                    elif item['title'] == 'PersonalInfo':
                        Class = "ti-id-badge"
                    elif item['title'] == 'Adapter&PowerCode-LNV':
                        Class = "ti-list"
                    elif item['title'] == '可借用':
                        Class = "ti-search"
                    elif item['title'] == '我的申请':
                        Class = "ti-marker"
                    elif item['title'] == '我的挂账':
                        Class = "ti-joomla"
                    elif item['title'] == '管理员':
                        Class = "ti-notepad"
                    elif item['title'] == '系统管理':
                        Class = "ti-panel"
                    # else:
                    #     Class = "ti-arrow-circle-right"

                    menu_html += option_str.format(Class=Class,menu_title=item['title'],
                                                   sub_menu=sub_menu)  # ,
                    # display="" if item['open'] else "rbac-hide",
                    # status="open" if item['open'] else "close")
                else:
                    sub_menu = ""


                # print(menu_html)
                # print('================================================================================================')
    # print(menu_html)
    # print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
    return menu_html


@register.simple_tag
def rbac_menu(request):
    """
    显示多级菜单：请求过来 -- 拿到session中的菜单，权限数据 -- 处理数据 -- 作显示
    返回多级菜单：数据处理部分抽象出来由单独的函数处理；渲染部分也抽象出来由单独函数处理
    :param request: 
    :return: 
    """
    menu_data = get_structure_data(request)
    menu_html = get_menu_html(menu_data)

    return mark_safe(menu_html)
    # 因为标签无法使用safe过滤器，这里用mark_safe函数来实现


@register.simple_tag
def rbac_css():
    """
    rabc要用到的css文件路径，并读取返回；注意返回字符串用mark_safe，否则传到模板会转义
    :return: 
    """
    css_path = os.path.join('app01', 'style_script','rbac.css')
    css = open(css_path,'r',encoding='utf-8').read()
    return mark_safe(css)


@register.simple_tag
def rbac_js():
    """
    rabc要用到的js文件路径，并读取返回
    :return: 
    """
    js_path = os.path.join('app01', 'style_script', 'rbac.js')
    js = open(js_path, 'r', encoding='utf-8').read()
    return mark_safe(js)



