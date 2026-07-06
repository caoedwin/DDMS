from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import os, json
from django.db.models import Max,Min,Sum,Count,Q
from django.http import JsonResponse
from service.init_permission import init_permission
from DMS import settings
from django.core.mail import send_mail, send_mass_mail
from django.core.mail import EmailMultiAlternatives
from app01 import tasks
from app01.models import UserInfo
from .models import TestDeviceLNV
from DeviceLNV.models import DeviceLNV

headermodel_TestDevice = {
    'Category': 'Category', 'Class': 'Class', 'Type': 'Type',
    # '設備編號': 'DevID',
    'Covered range for case': 'Covered_range_for_case',
    'Require State': 'Require_State', 'Comments': 'Comments', 'Remark': 'Remark', 'ODM status': 'ODM_status',
    'Purchase Plan': 'Purchase_Plan', 'Device Price': 'Device_Price', 'Act_Status': 'Act_Status',
    'Device Know Issue': 'Device_Know_Issue',
    'Device #1': 'Device1',
    'Device #2': 'Device2',
    'Device #3': 'Device3',
    'Device #4': 'Device4',
    'Device #5': 'Device5',
    'Device #6': 'Device6',
    'Device #7': 'Device7',
    'Device #8': 'Device8',
    'Device #9': 'Device9',
    'Device #10': 'Device10',
}

from django.db import models


def map_field_type(field):
    """映射 Django 字段类型到前端显示类型"""
    if isinstance(field, models.BooleanField):
        return 'switch'
    elif isinstance(field, (models.DateField, models.DateTimeField)):
        return 'date'
    elif isinstance(field, models.ForeignKey):
        return 'relation'
    elif isinstance(field, models.TextField):
        return 'long-text'
    elif isinstance(field, models.FileField):
        return 'file'
    elif isinstance(field, models.CharField):
        return 'text'
    else:
        return 'text'  # 默认类型


def calculate_field_width(field):
    """计算字段建议宽度"""
    # 基于 max_length 的宽度计算
    if hasattr(field, 'max_length') and field.max_length:
        # 每字符约 8px，最小宽度 100px，最大 300px
        return min(max(field.max_length * 8, 100), 300)

    # 基于字段类型的默认宽度
    field_type = map_field_type(field)
    type_widths = {
        'switch': 100,
        'date': 150,
        'datetime': 180,
        'relation': 200,
        'file': 220,
        'long-text': 300,
        'text': 180
    }
    return type_widths.get(field_type, 180)  # 默认 180px


def get_table_columns(model):
    columns = []
    for field in model._meta.fields:
        # 跳过不需要的字段（如 ID）
        if field.name == 'id' or field.name.endswith('_ptr'):
            continue

        # 基本字段配置
        field_config = {
            'field': field.name,
            'title': field.verbose_name,  # 使用 verbose_name 作为标题
            'type': map_field_type(field),
            'width': calculate_field_width(field),
            'align': "center",
        }

        # 添加字段特定属性
        if hasattr(field, 'choices') and field.choices:
            field_config['choices'] = dict(field.choices)

        columns.append(field_config)
    return columns




@csrf_exempt
def TestDeviceListLNV(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "TestDeviceLNV/TestDeviceListLNV"

    # # 1. 始终为动态列设置唯一的: key属性
    # #
    # # 2. 固定列（fixed）可在配置中添加fixed: 'left' / 'right'属性
    # #
    # # 3. 排序功能可通过添加sortable属性实现
    # #
    # # 4. 表头分组需嵌套使用el - table - column（ElementUI不支持单层动态分组）
    # # < el - table - column
    # #     v-for ="col in tableColumns"
    # #     :key = "col.prop"
    # #     :prop = "col.prop"
    # #     :label = "col.label"
    # #     :width = "col.width"
    # #     :align = "col.align"
    # #
    # # >
    # #     //自定义内容，如果只要默认的，直接去点下面的template这一段
    #         < !-- 根据字段类型使用不同的渲染方式 -->
    #         < template  # default="scope">
    #         < !-- 布尔值显示开关 -->
    #         < el - switch
    #         v - if = "col.type === 'switch'"
    #         v - model = "scope.row[col.prop]"
    #         disabled
    #
    #         / >
    #
    #         < !-- 日期格式化 -->
    #         < span
    #         v - else - if = "col.type === 'date'" >
    #         ${formatDate(scope.row[col.prop])}
    #         < / span >
    #
    #         < !-- 外键关系显示关联对象名称 -->
    #         < span
    #         v - else - if = "col.type === 'relation'" >
    #         ${scope.row[col.prop + '_name']} <!-- 假设返回了关联对象名称 -->
    #         < / span >
    #
    #         < !-- 长文本使用
    #         tooltip
    #         显示 -->
    #         < el - tooltip
    #         v - else - if = "col.type === 'long-text'"
    #         :content = "scope.row[col.prop]"
    #         placement = "top"
    #         >
    #         < span
    #
    #
    #         class ="text-truncate" >
    #
    #
    #         ${truncateText(scope.row[col.prop], 30)}
    #         < / span >
    #         < / el - tooltip >
    #
    #         < !-- 默认文本显示 -->
    #         < span
    #         v - else >
    #         ${scope.row[col.prop]}
    #         < / span >
    #         < / template >
    # # < / el - table - column >

    # 提取字段名和 verbose_name（过滤关系字段）
    tableColumns = [
        # {'id': 1, 'prop': 'status', 'lable': '状态', 'type': 'tag', 'width': '120', 'align': 'center'},
        #             {'id': 2, 'prop': 'createTime', 'lable': '创建时间', 'type': 'text', 'width': '180', 'align': 'center'}
    ]
    tableColumns = get_table_columns(TestDeviceLNV)
    # print(tableColumns)

    categoryOptions = [
        # "Sensor", "USB Function", "Thonderbolt"
    ]
    for i in TestDeviceLNV.objects.all().values("Category").distinct().order_by("Category"):
        categoryOptions.append(i['Category'])

    classOptions = [
        # "Sensor test device", "USB Keyboard", "USB Mouse"
    ]
    for i in TestDeviceLNV.objects.all().values("Class").distinct().order_by("Class"):
        classOptions.append(i['Class'])

    DeviceOptions = [
        # {"value": "keyboard", "Status": "in use", "Purchase_period": "5"},
        # {"value": "mouse", "Status": "block", "Purchase_period": "6"},
    ]
    for i in DeviceLNV.objects.all():# NID是唯一不需要去重
        Purchase_period = ''
        if i.Pchsdate:
            if datetime.now().date() > i.Pchsdate:
                Purchase_period = round(
                    float(
                        str((datetime.now().date() - i.Pchsdate)).split(' ')[
                            0]) / 365,
                    1)
        DeviceOptions.append(
            {
                "value": i.NID, "Status": i.DevStatus + "/" + i.BrwStatus, "Purchase_period": Purchase_period
            }
        )

    mock_data = [
        # {"id": "1", "Category": "Sensor", "Class": "Sensor test device", "Type": "Desk lamp",
        #  "Covered_range_for_case": "SFA078_CF_01 ALS Performance test", "Require_State": "Must", "Comments": "",
        #  "Remark": "", "ODM_status": "", "Purchase_Plan": "", "Act_Status": "Active", "Device1": "", "Status1": "",
        #  "Purchase_period1": "",
        #  "Device2": "", "Status2": "", "Purchase_period2": "", "Device3": "", "Status3": "", "Purchase_period3": "",
        #  "Device4": "",
        #  "Status4": "", "Purchase_period4": "", "Device5": "", "Status5": "", "Purchase_period5": "", "Device6": "",
        #  "Status6": "", "Purchase_period6": "",
        #  "Device7": "", "Status7": "", "Purchase_period7": "", "Device8": "", "Status8": "", "Purchase_period8": "",
        #  "Device9": "", "Status9": "", "Purchase_period9": "", "Device10": "", "Status10": "", "Purchase_period10": "",
        #  },
        # {"id": "2", "Category": "Sensor", "Class": "Sensor test device", "Type": "Light Meter_TES1336A",
        #  "Covered_range_for_case": "SFA011_CF_01 ALS Performance test", "Require_State": "Optional", "Comments": "",
        #  "Remark": "", "ODM_status": "", "Purchase_Plan": "", "Act_Status": "Active", "Device1": "", "Status1": "",
        #  "Purchase_period1": "",
        #  "Device2": "", "Status2": "", "Purchase_period2": "", "Device3": "", "Status3": "", "Purchase_period3": "",
        #  "Device4": "",
        #  "Status4": "", "Purchase_period4": "", "Device5": "", "Status5": "", "Purchase_period5": "", "Device6": "",
        #  "Status6": "", "Purchase_period6": "",
        #  "Device7": "", "Status7": "", "Purchase_period7": "", "Device8": "", "Status8": "", "Purchase_period8": "",
        #  "Device9": "", "Status9": "", "Purchase_period9": "", "Device10": "", "Status10": "", "Purchase_period10": "",
        #  },
        # {"id": "3", "Category": "Sensor1", "Class": "Sensor test device", "Type": "Desk lamp",
        #  "Covered_range_for_case": "SFA011_CF_01 ALS Performance test", "Require_State": "Must", "Comments": "",
        #  "Remark": "", "ODM_status": "", "Purchase_Plan": "", "Act_Status": "Active", "Device1": "", "Status1": "",
        #  "Purchase_period1": "",
        #  "Device2": "", "Status2": "", "Purchase_period2": "", "Device3": "", "Status3": "", "Purchase_period3": "",
        #  "Device4": "",
        #  "Status4": "", "Purchase_period4": "", "Device5": "", "Status5": "", "Purchase_period5": "", "Device6": "",
        #  "Status6": "", "Purchase_period6": "",
        #  "Device7": "", "Status7": "", "Purchase_period7": "", "Device8": "", "Status8": "", "Purchase_period8": "",
        #  "Device9": "", "Status9": "", "Purchase_period9": "", "Device10": "", "Status10": "", "Purchase_period10": "",
        #  },

    ]

    errMsg = ''

    permission = 0
    roles = []
    onlineuser = request.session.get('account_DMS')
    # print(onlineuser)
    # print(UserInfo.objects.filter(account=onlineuser))
    if UserInfo.objects.filter(account=onlineuser).first():
        for i in UserInfo.objects.filter(account=onlineuser).first().role.all():
            roles.append(i.name)
    # print(roles)
    # editPpriority = 100
    for i in roles:
        if 'Sys_Admin' in i or 'Device_C38LNV_Admin' in i:
            permission = 1
    # print(request.method)

    num_fields = 10 # DeviceN的个数

    TestDeviceLNV_obj = TestDeviceLNV.objects.all()

    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if request.POST:
            if request.POST.get('isGetData') == 'SEARCH':
                check_dic = {}
                if request.POST.get('Category'):
                    check_dic['Category'] = request.POST.get('Category')
                if request.POST.get('Class'):
                    check_dic['Class'] = request.POST.get('Class')
                if check_dic:
                    TestDeviceLNV_obj = TestDeviceLNV.objects.filter(**check_dic)
            if request.POST.get('action') == 'update':
                ID = request.POST.get('ID')
                update_dic = {
                    "Category": request.POST.get('Category') if request.POST.get('Category') else '', #从有值变成空值的更新
                    "Class": request.POST.get('Class') if request.POST.get('Class') else '',
                    "Type": request.POST.get('Type') if request.POST.get('Type') else '',
                    "Covered_range_for_case": request.POST.get('Covered_range_for_case') if request.POST.get('Covered_range_for_case') else '',
                    "Require_State": request.POST.get('Require_State') if request.POST.get('Require_State') else '',
                    "Comments": request.POST.get('Comments') if request.POST.get('Comments') else '',
                    "Remark": request.POST.get('Remark') if request.POST.get('Remark') else '',
                    "ODM_status": request.POST.get('ODM_status') if request.POST.get('ODM_status') else '',
                    "Purchase_Plan": request.POST.get('Purchase_Plan') if request.POST.get('Purchase_Plan') else '',
                    "Device_Price": request.POST.get('Device_Price') if request.POST.get('Device_Price') and request.POST.get('Device_Price') != 'null' else None, #从有值变成空值的更新,整型，浮点型，日期都是None
                    "Act_Status": request.POST.get('Act_Status') if request.POST.get('Act_Status') else '',
                    "Device_Know_Issue": request.POST.get('Device_Know_Issue') if request.POST.get('Device_Know_Issue') else '',
                    "Device1": request.POST.get('Device1') if request.POST.get('Device1') else '',
                    "Device2": request.POST.get('Device2') if request.POST.get('Device2') else '',
                    "Device3": request.POST.get('Device3') if request.POST.get('Device3') else '',
                    "Device4": request.POST.get('Device4') if request.POST.get('Device4') else '',
                    "Device5": request.POST.get('Device5') if request.POST.get('Device5') else '',
                    "Device6": request.POST.get('Device6') if request.POST.get('Device6') else '',
                    "Device7": request.POST.get('Device7') if request.POST.get('Device7') else '',
                    "Device8": request.POST.get('Device8') if request.POST.get('Device8') else '',
                    "Device9": request.POST.get('Device9') if request.POST.get('Device9') else '',
                    "Device10": request.POST.get('Device10') if request.POST.get('Device10') else '',
                }
                try:
                    with transaction.atomic():
                        TestDeviceLNV.objects.filter(id=ID).update(**update_dic)
                except Exception as e:
                    # alert = '此数据正被其他使用者编辑中...'
                    errMsg = alert = str(e)
                    print(alert)

                # mock_data
                check_dic = {}
                if request.POST.get('searchCategory'):
                    check_dic['Category'] = request.POST.get('searchCategory')
                if request.POST.get('searchClass'):
                    check_dic['Class'] = request.POST.get('searchClass')
                if check_dic:
                    TestDeviceLNV_obj = TestDeviceLNV.objects.filter(**check_dic)


        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                if 'MUTIDELETE' in str(request.body):
                    responseData = json.loads(request.body)
                    # CustomerSearch = responseData['Customer']
                    # ProjectSearch = responseData['Projectcode']
                    #
                    # Check_dic_Project = {'Customer': CustomerSearch, 'Project': ProjectSearch, }
                    # Projectinfo = TestDeviceLNV.objects.filter(**Check_dic_Project).first()
                    # print(Projectinfo)
                    # current_user = request.session.get('user_name')
                    # if Projectinfo:
                    #     for k in Projectinfo.Owner.all():
                    #         # print(k.username,current_user)
                    #         # print(type(k.username),type(current_user))
                    #         if k.username == current_user:
                    #             canEdit = 1
                    #             break
                    #
                    # del_dic_IssueBreakdown = {'Customer': CustomerSearch, 'Project': ProjectSearch}
                    # print(dic_Project)

                    if TestDeviceLNV.objects.all():
                        # print(1)
                        TestDeviceLNV.objects.all().delete()
                # print('2')
                if 'ExcelData' in str(request.body):
                    responseData = json.loads(request.body)
                    # print(responseData)
                    # print(responseData['historyYear'],type(responseData['historyYear']))
                    xlsxlist = json.loads(responseData['ExcelData'])
                    # searchCategory = responseData['searchCategory']
                    # searchClass = responseData['searchClass']
                    # Adapterlist = [
                    #     {
                    #         'Number': '編號', }
                    # ]
                    rownum = 0
                    startupload = 0
                    # print(xlsxlist)
                    uploadxlsxlist = []
                    for i in xlsxlist:
                        # print(type(i),i)
                        rownum += 1
                        # print(rownum)
                        modeldata = {}
                        for key, value in i.items():
                            if key in headermodel_TestDevice.keys():
                                modeldata[headermodel_TestDevice[key]] = value
                        if 'Category' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Category不能爲空
                                                                            """ % rownum
                            break
                        if 'Class' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Class不能爲空
                                                                            """ % rownum
                            break
                        if 'Type' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Type不能爲空
                                                                            """ % rownum
                            break
                        if 'Covered_range_for_case' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Covered_range_for_case不能爲空
                                                                            """ % rownum
                            break
                        if 'Require_State' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Require_State不能爲空
                                                                            """ % rownum
                            break

                        uploadxlsxlist.append(modeldata)
                    # print(startupload)
                    #让数据可以从有值更新为无值，空值
                    TestDevieModelfiedlist = []
                    for i in TestDeviceLNV._meta.fields:
                        if i.name != 'id':
                            TestDevieModelfiedlist.append([i.name,i.get_internal_type()])
                    for i in uploadxlsxlist:
                        for j in TestDevieModelfiedlist:
                            if j[0] not in i.keys():
                                # print(j)
                                if j[1] == "DateField" or j[1] == "FloatField" or j[1] == "IntegerField":
                                    i[j[0]] = None
                                else:
                                    i[j[0]] = ''
                    num1 = 0
                    if startupload:
                        create_list = []
                        for i in uploadxlsxlist:
                            # print(i)
                            num1 += 1
                            create_list.append(TestDeviceLNV(**i))
                        try:
                            with transaction.atomic():
                                TestDeviceLNV.objects.bulk_create(create_list)
                        except Exception as e:
                            # alert = '此数据正被其他使用者编辑中...'
                            errMsg = alert = str(e)
                            print(alert)
                        errMsg = '上傳成功'

                    # mock_data
                    check_dic = {}
                    # if searchCategory:
                    #     check_dic['Category'] = searchCategory
                    # if searchClass:
                    #     check_dic['Class'] = searchClass
                    if check_dic:
                        TestDeviceLNV_obj = TestDeviceLNV.objects.filter(**check_dic)

        # mock_data
        for i in TestDeviceLNV_obj:
            Useyears_dict = {f'Useyears{j}': '' for j in range(1, num_fields + 1)}
            Status_dict = {f'Status{j}': '' for j in range(1, num_fields + 1)}
            # 循环获取每个字段的值
            for j in range(1, num_fields + 1):
                keyUse = f"Useyears{j}"  # 动态生成键名
                # valueUse = Useyears_dict.get(keyUse)  # 使用 get 避免 KeyError
                keyStatus = f"Status{j}"  # 动态生成键名
                # valueStatus = Status_dict.get(keyStatus)  # 使用 get 避免 KeyError
                field_name = f'Device{j}'
                # print(field_name)
                value = getattr(i, field_name)
                # print(value)
                if value:
                    Device_obj = DeviceLNV.objects.filter(NID=value).first()
                    Status_dict[keyStatus] = Device_obj.DevStatus + "/" + Device_obj.BrwStatus
                    if Device_obj.Pchsdate:
                        if datetime.now().date() > Device_obj.Pchsdate:
                            Useyears_dict[keyUse] = round(
                                float(
                                    str((datetime.now().date() - Device_obj.Pchsdate)).split(' ')[
                                        0]) / 365,
                                1)
            mock_dic = {"id": i.id, "Category": i.Category, "Class": i.Class,
                        "Type": i.Type, "Covered_range_for_case": i.Covered_range_for_case,
                        "Require_State": i.Require_State,
                        "Comments": i.Comments, "Remark": i.Remark, "ODM_status": i.ODM_status,
                        "Purchase_Plan": i.Purchase_Plan, "Device_Price": i.Device_Price,
                        "Act_Status": i.Act_Status,
                        "Device_Know_Issue": i.Device_Know_Issue,
                        # "Device1": i.Device1, "Status1": Status_dict['Status1'],
                        # "Purchase_period1": Useyears_dict['Useyears1'],
                        # "Device2": i.Device2, "Status2": Status_dict['Status2'],
                        # "Purchase_period2": Useyears_dict['Useyears2'],
                        # "Device3": i.Device3, "Status3": Status_dict['Status3'],
                        # "Purchase_period3": Useyears_dict['Useyears3'],
                        # "Device4": i.Device4, "Status4": Status_dict['Status4'],
                        # "Purchase_period4": Useyears_dict['Useyears4'],
                        # "Device5": i.Device5, "Status5": Status_dict['Status5'],
                        # "Purchase_period5": Useyears_dict['Useyears5'],
                        # "Device6": i.Device6, "Status6": Status_dict['Status6'],
                        # "Purchase_period6": Useyears_dict['Useyears6'],
                        # "Device7": i.Device7, "Status7": Status_dict['Status7'],
                        # "Purchase_period7": Useyears_dict['Useyears7'],
                        # "Device8": i.Device8, "Status8": Status_dict['Status8'],
                        # "Purchase_period8": Useyears_dict['Useyears8'],
                        # "Device9": i.Device9, "Status9": Status_dict['Status9'],
                        # "Purchase_period9": Useyears_dict['Useyears9'],
                        # "Device10": i.Device10, "Status10": Status_dict['Status10'],
                        # "Purchase_period10": Useyears_dict['Useyears10'],
                        }
            for j in range(1, num_fields + 1):
                keyDev = f"Device{j}"  # 动态生成键名
                keyperiod = f"Purchase_period{j}"  # 动态生成键名
                keyUse = f"Useyears{j}"  # 动态生成键名
                keyStatus = f"Status{j}"  # 动态生成键名
                field_name = f'Device{j}'

                value = getattr(i, field_name)
                # print(value)
                mock_dic[keyDev] = value
                # print(keyStatus)
                # print(Status_dict)
                mock_dic[keyStatus] = Status_dict[keyStatus]
                mock_dic[keyperiod] = Useyears_dict[keyUse]
            mock_data.append(mock_dic)


        data = {
            "errMsg": errMsg,
            "categoryOptions": categoryOptions,
            "classOptions": classOptions,
            "DeviceOptions": DeviceOptions,
            "content": mock_data,
            "permission": permission,

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'TestDeviceLNV/TestDeviceListLNV.html', locals())

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Q

def device_score_page(request):
    """设备评分页面"""
    return render(request, 'TestDeviceLNV/device_score.html')

def device_demand_week_page(request):
    """设备需求按周统计页面"""
    return render(request, 'TestDeviceLNV/device_demand_week.html')


# ===================== API 认证与请求 =====================
def get_api_token():
    """获取API认证token"""
    url = 'http://127.0.0.1:8002/PersonalInfo/api_Per/login/'
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    body = {"username": "API_CQM", "password": "Qs!3m6Tc7"}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(body), timeout=5)
        if r.status_code == 200 and r.json().get("token"):
            return "Bearer " + r.json()["token"]
    except Exception as e:
        print(f"获取token失败: {e}")
    return None

def api_request(url, params=None):
    token = get_api_token()
    if not token:
        return None
    headers = {"Authorization": token}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"API请求失败: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"请求异常: {e}")
    return None

from django.core.cache import cache
#这样第一次请求较慢，后续请求直接命中缓存，响应时间降至毫秒级。
import concurrent.futures

#并行请求 + 缓存
def fetch_testprojects():
    """获取四个测试项目API的数据，合并返回列表（缓存10分钟，并行请求）"""
    cache_key = 'testprojects_data'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    urls = [
        'http://127.0.0.1:8002/TestPlanSW/api/testprojects/',
        'http://127.0.0.1:8002/TestPlanSW/api/testprojects_aio/',
        'http://127.0.0.1:8002/TestPlanSWOS/api/testprojects/',
        'http://127.0.0.1:8002/TestPlanSWOS/api/testprojects_aio/',
    ]

    def fetch_single(url):
        data = api_request(url)
        if data and isinstance(data, list):
            return data
        elif data and isinstance(data, dict) and 'results' in data:
            return data['results']
        return []

    all_projects = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(fetch_single, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            if result:
                all_projects.extend(result)

    cache.set(cache_key, all_projects, timeout=600)  # 10分钟
    return all_projects

# ===================== 设备评分核心函数（完整移植） =====================
def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y%m%d'):
        try:
            return datetime.strptime(str(date_str), fmt).date()
        except:
            continue
    return None

def tech_score(dev):
    """技术评分（完整版）"""
    ctgry = (dev.DevCtgry or '').lower()
    prop = (dev.Devproperties or '').lower()
    intf = (dev.IntfCtgry or '').lower()

    if 'mouse' in ctgry or 'keyboard' in ctgry:
        if 'usb1' in intf or 'ps2' in prop:
            return 100
        elif 'usb2' in intf or '2.4g' in prop:
            return 50
        elif 'usb3' in intf or 'bt5' in prop or 'bluetooth 5' in prop:
            return 0
        else:
            return 70
    elif 'usb memory' in ctgry:
        size = (dev.Devsize or '').lower()
        if 'usb2' in intf or ('gb' in size and int(size.split('gb')[0]) < 8):
            return 100
        elif 'usb3' in intf:
            return 50
        else:
            return 70
    elif 'hdd' in ctgry or 'ssd' in ctgry:
        if 'hdd' in prop.lower():
            return 100
        elif 'ssd' in prop.lower() and 'usb3.0' in intf:
            return 50
        elif 'nvme' in prop.lower() or 'usb3.1' in intf or 'thunderbolt' in intf:
            return 0
        else:
            return 70
    elif 'headphone' in ctgry or 'speaker' in ctgry:
        if 'usb2.0' in intf or ('bt' in intf and 'bt3' in intf):
            return 100
        elif 'usb3.0' in intf or 'bt4' in intf or 'audio jack' in intf:
            return 50
        elif 'bt5' in intf or 'type-c' in intf:
            return 0
        else:
            return 70
    elif 'ap' in ctgry or 'router' in ctgry:
        if '802.11b' in prop or '802.11g' in prop or '802.11a' in prop:
            return 100
        elif '802.11n' in prop:
            return 50
        elif 'ac' in prop or 'ax' in prop or 'wifi6' in prop:
            return 0
        else:
            return 80
    elif 'card reader' in ctgry:
        if 'usb2.0' in intf:
            return 100
        elif 'usb3.0' in intf:
            return 50
        else:
            return 70
    elif 'hub' in ctgry or 'dongle' in ctgry:
        if 'usb2.0' in intf:
            return 100
        elif 'usb3.0' in intf and 'vga' not in intf:
            return 50
        elif 'usb-c' in intf or '4k' in intf:
            return 0
        else:
            return 70
    elif 'monitor' in ctgry:
        if 'vga' in intf or '1366' in prop:
            return 100
        elif 'hdmi 1.4' in intf or '1080p' in prop:
            return 50
        elif '4k' in prop or 'type-c' in intf:
            return 0
        else:
            return 70
    elif 'odd' in ctgry:
        if 'dvd-rom' in prop:
            return 100
        elif 'dvd-rw' in prop:
            return 50
        elif 'blu-ray' in prop:
            return 0
        else:
            return 80
    elif 'camera' in ctgry:
        if 'usb2.0' in intf or '720p' in prop or 'vga' in prop:
            return 100
        elif 'usb3.0' in intf and ('1080p' in prop or 'full hd' in prop):
            return 50
        elif '4k' in prop or 'usb-c' in intf or 'type-c' in intf:
            return 0
        else:
            return 70
    elif 'cable' in ctgry or 'audio jack' in ctgry:
        if 'vga' in intf or 'dvi' in intf or 'composite' in intf:
            return 100
        elif 'hdmi 1.4' in prop or 'dp 1.2' in prop or 'usb2.0' in intf:
            return 50
        elif 'hdmi 2.' in prop or 'dp 1.4' in prop or 'thunderbolt' in intf or 'usb-c' in intf:
            return 0
        else:
            return 70
    elif 'power adapter' in ctgry or ('adapter' in ctgry and 'power' in prop):
        if ('round' in intf or 'slim' in intf) and '65w' not in prop:
            return 100
        elif 'usb-c' in intf and '65w' not in prop:
            return 50
        elif 'gan' in prop or '65w' in prop or '100w' in prop or 'quick charge' in prop:
            return 0
        else:
            return 70
    elif 'phone' in ctgry or 'ipad' in ctgry or 'iphone' in ctgry or 'tablet' in ctgry:
        if 'micro usb' in intf or '30-pin' in intf:
            return 100
        elif 'lightning' in intf or ('usb-c' in intf and 'fast' not in prop):
            return 50
        elif 'wireless' in prop or 'fast charge' in prop or 'type-c' in intf:
            return 0
        else:
            return 70
    elif 'game' in ctgry or 'joystick' in ctgry or 'gamepad' in ctgry:
        if 'usb2.0' in intf or 'gameport' in intf:
            return 100
        elif 'usb3.0' in intf or '2.4g' in prop:
            return 50
        elif 'bt5' in intf or 'usb-c' in intf:
            return 0
        else:
            return 70
    elif 'microphone' in ctgry:
        if 'usb2.0' in intf or '3.5mm' in intf:
            return 100
        elif 'usb3.0' in intf or 'bt4' in intf:
            return 50
        elif 'type-c' in intf or 'bt5' in intf:
            return 0
        else:
            return 70
    elif 'projector' in ctgry:
        if 'vga' in intf or 'svga' in prop:
            return 100
        elif 'hdmi' in intf and '1080p' in prop:
            return 50
        elif '4k' in prop or 'laser' in prop:
            return 0
        else:
            return 70
    else:
        return 70

def compute_score(dev, today):
    """计算综合评分及各项子分"""
    pdate = parse_date(dev.Pchsdate)
    if pdate:
        years = (today - pdate).days / 365.25
        age_score = 100 if years > 10 else (80 if years > 8 else (60 if years > 5 else (30 if years > 1 else 0)))
    else:
        age_score = 50

    usr = dev.UsrTimes or 0
    try:
        usr = int(usr)
    except:
        usr = 0
    borrow_score = 100 if usr > 500 else (70 if usr > 300 else (40 if usr > 200 else (20 if usr > 100 else 0)))

    use_count = dev.uscyc or 0
    try:
        use_count = int(use_count)
    except:
        use_count = 0
    if use_count == 0:
        usage_score = 50
    else:
        usage_score = 100 if use_count > 2000 else (90 if use_count > 1500 else (80 if use_count > 1000 else (70 if use_count > 500 else (40 if use_count > 200 else (20 if use_count > 100 else 0)))))

    tech = tech_score(dev)

    eol_date = parse_date(dev.EOL)
    eol_score = 80 if (eol_date and eol_date < today) else 50

    status = (dev.DevStatus or '').lower()
    status_score = 100 if 'damaged' in status else (90 if 'lost' in status else (50 if 'long' in status else 0))

    weights = [0.3, 0.2, 0.1, 0.2, 0.1, 0.1]
    scores = [age_score, usage_score, borrow_score, tech, eol_score, status_score]
    total = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
    return total, {'age': age_score, 'usage': usage_score, 'borrow': borrow_score,
                   'tech': tech, 'eol': eol_score, 'status': status_score}

def upgrade_suggestion(dev, score):
    """生成升级建议"""
    ctgry = (dev.DevCtgry or '').lower()
    urgency = "紧急更换" if score >= 90 else ("酌情更换" if score >= 70 else ("可观察" if score >= 40 else "继续使用"))
    suggestion = "暂无特殊建议"
    if 'mouse' in ctgry:
        suggestion = "推荐升级至蓝牙5.0/5.2无线鼠标，支持多设备切换，更高DPI。"
    elif 'keyboard' in ctgry:
        suggestion = "推荐升级至USB-C或蓝牙机械键盘，支持多模连接。"
    elif 'usb memory' in ctgry:
        suggestion = "推荐升级至USB 3.1/3.2接口、容量≥128GB的高速U盘。"
    elif 'hdd' in ctgry or 'ssd' in ctgry:
        if 'hdd' in (dev.Devproperties or '').lower():
            suggestion = "强烈建议更换为NVMe SSD或USB3.2外置固态硬盘。"
        else:
            suggestion = "考虑升级为Thunderbolt 3/4或USB4接口的外置SSD。"
    elif 'headphone' in ctgry or 'speaker' in ctgry:
        suggestion = "推荐升级至蓝牙5.2+ANC主动降噪耳机，或Type-C有线高解析度耳机。"
    elif 'ap' in ctgry or 'router' in ctgry:
        suggestion = "推荐升级至Wi-Fi 6/6E路由器，支持OFDMA和更高速率。"
    elif 'card reader' in ctgry:
        suggestion = "升级至USB3.1读卡器，支持UHS-II SD卡。"
    elif 'hub' in ctgry or 'dongle' in ctgry:
        suggestion = "考虑升级为USB-C多功能扩展坞，支持4K输出、千兆网口、PD充电。"
    elif 'monitor' in ctgry:
        suggestion = "升级至4K分辨率、高刷新率、支持DisplayPort 1.4或Type-C一线连的显示器。"
    elif 'odd' in ctgry:
        suggestion = "当前光驱技术已过时，如必要可更换为外置蓝光刻录机。"
    elif 'camera' in ctgry:
        suggestion = "推荐升级至USB3.0或Type-C接口的4K网络摄像头。"
    elif 'cable' in ctgry or 'audio jack' in ctgry:
        suggestion = "建议更换为HDMI 2.1、DP 1.4或雷电4线缆。"
    elif 'power adapter' in ctgry or ('adapter' in ctgry and 'power' in (dev.Devproperties or '').lower()):
        suggestion = "推荐升级至氮化镓(GaN)充电器，支持USB-C PD快充。"
    elif 'phone' in ctgry or 'ipad' in ctgry or 'iphone' in ctgry or 'tablet' in ctgry:
        suggestion = "建议升级至支持5G、无线充电和快充的当前主流手机/平板。"
    elif 'game' in ctgry or 'joystick' in ctgry or 'gamepad' in ctgry:
        suggestion = "推荐升级至支持蓝牙5.0+、低延迟无线或有线USB-C的游戏手柄。"
    elif 'microphone' in ctgry:
        suggestion = "建议升级至USB-C接口或支持高采样率的专业麦克风。"
    elif 'projector' in ctgry:
        suggestion = "推荐升级至4K激光投影仪，支持HDR和无线投屏。"
    else:
        suggestion = "建议对照最新技术规范进行资产评估。"
    return urgency, suggestion


# ===================== JSON 接口视图 =====================
from django.core.cache import cache
from django.db.models import Q

@csrf_exempt
def device_score_view(request):
    """返回设备评分数据（JSON），过滤损坏/丢失设备，按分数降序，使用缓存优化性能"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # 缓存键（可添加版本号，便于清理）
    cache_key = 'device_score_data'
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        # 如果缓存存在，直接返回
        return JsonResponse(cached_data)

    today = datetime.now().date()
    result = []

    # 1. 查询优化：只获取评分所需的字段，排除损坏/丢失设备
    # 如果状态值大小写不一致，可改用 Q 对象的 __iexact
    devices = DeviceLNV.objects.exclude(
        Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')
    ).only(
        'id', 'NID', 'DevVendor', 'DevModel', 'DevName', 'DevCtgry',
        'DevStatus', 'Pchsdate', 'UsrTimes', 'uscyc', 'Devproperties',
        'IntfCtgry', 'Devsize', 'EOL'
    )

    # 2. 计算评分
    for dev in devices:
        total, detail = compute_score(dev, today)
        urgency, sug = upgrade_suggestion(dev, total)
        result.append({
            'id': dev.id,
            'NID': dev.NID,
            'DevVendor': dev.DevVendor,
            'DevModel': dev.DevModel,
            'DevName': dev.DevName,
            'DevCtgry': dev.DevCtgry,
            'DevStatus': dev.DevStatus,
            'Score': round(total, 2),
            'Priority': urgency,
            'Suggestion': sug,
            'AgeScore': detail['age'],
            'UsageScore': detail['usage'],
            'BorrowScore': detail['borrow'],
            'TechScore': detail['tech'],
            'EOLScore': detail['eol'],
            'StatusScore': detail['status'],
        })

    # 按综合评分降序排列
    result.sort(key=lambda x: x['Score'], reverse=True)

    # 构造最终响应数据
    response_data = {'data': result, 'count': len(result)}

    # 缓存 5 分钟（300秒），可根据实际情况调整
    cache.set(cache_key, response_data, timeout=300)

    return JsonResponse(response_data)

def get_device_type(dev):
    """返回设备的类型三元组"""
    return ((dev.IntfCtgry or ''), (dev.DevCtgry or ''), (dev.Devproperties or ''))


# import logging
# logger = logging.getLogger('django')  # 使用 settings.py 中的 'log' logger

import logging
from difflib import get_close_matches
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.cache import cache

logger = logging.getLogger('django')

import time

@csrf_exempt
def device_demand_week_view(request):
    """按周统计设备需求（所有项目共享相同设备需求），缓存优化"""
    import time
    start_total = time.time()

    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # ---------- 固定测试日期，正式时改为 datetime.now().date() ----------
    today = datetime(2019, 1, 29).date()
    # 正式启用：
    # today = datetime.now().date()

    cache_key = f'demand_week_result_{today.isoformat()}'
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return JsonResponse(cached_result)

    # ---------- 1. 获取需求项（缓存，使用新函数） ----------
    t1 = time.time()
    requirement_items = get_requirement_items()
    t2 = time.time()
    logger.info(f"获取需求项耗时: {t2-t1:.2f}s, 共 {len(requirement_items)} 项")
    if not requirement_items:
        return JsonResponse({'error': '无法为任何需求项匹配到可用设备'}, status=404)

    # ---------- 2. 获取项目计划（缓存） ----------
    t1 = time.time()
    projects = fetch_testprojects()
    t2 = time.time()
    logger.info(f"获取项目计划耗时: {t2-t1:.2f}s, 共 {len(projects) if projects else 0} 个项目")
    if not projects:
        return JsonResponse({'error': '无法获取项目计划数据'}, status=500)

    # 过滤有效项目
    t1 = time.time()
    valid_projects = []
    for proj in projects:
        start_str = proj.get('ScheduleBegin') or proj.get('start_date') or proj.get('StartDate')
        end_str = proj.get('ScheduleEnd') or proj.get('end_date') or proj.get('EndDate')
        if not start_str or not end_str:
            continue
        try:
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
        except Exception as e:
            logger.warning(f"日期解析失败: {start_str} / {end_str}，错误: {e}")
            continue
        valid_projects.append({
            'name': proj.get('Project') or proj.get('project_name') or proj.get('name') or 'Unknown',
            'Phase': proj.get('Phase') or '',
            'start': start,
            'end': end
        })
    t2 = time.time()
    logger.info(f"过滤项目耗时: {t2-t1:.2f}s, 有效项目: {len(valid_projects)}")
    if not valid_projects:
        logger.error("没有有效的项目计划数据")
        return JsonResponse({'error': '没有有效的项目计划数据'}, status=404)

    # ---------- 3. 统计库存 ----------
    t1 = time.time()
    inventory = defaultdict(int)
    for dev in DeviceLNV.objects.exclude(Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')):
        type_key = (dev.IntfCtgry, dev.DevCtgry, dev.Devproperties)
        inventory[type_key] += 1
    t2 = time.time()
    logger.info(f"统计库存耗时: {t2-t1:.2f}s, 共 {len(inventory)} 种设备类型")

    # ---------- 4. 按周汇总需求（包含项目名称和Phase） ----------
    t1 = time.time()
    week_demand = defaultdict(lambda: defaultdict(lambda: {'demand': 0, 'projects': set()}))

    for proj in valid_projects:
        start = proj['start']
        end = proj['end']
        days_since_monday = start.weekday()
        week_start = start - timedelta(days=days_since_monday)
        proj_info = f"{proj['name']} ({proj['Phase']})" if proj.get('Phase') else proj['name']
        while week_start <= end:
            effective_start = max(start, week_start)
            effective_end = min(end, week_start + timedelta(days=6))
            if effective_start <= effective_end:
                for type_key, nid in requirement_items:
                    week_demand[week_start][type_key]['demand'] += 1
                    week_demand[week_start][type_key]['projects'].add(proj_info)
            week_start += timedelta(days=7)
    t2 = time.time()
    logger.info(f"按周汇总耗时: {t2-t1:.2f}s, 共 {len(week_demand)} 周")

    # ---------- 5. 生成输出（仅未来周） ----------
    t1 = time.time()
    days_since_monday = today.weekday()
    this_week_start = today - timedelta(days=days_since_monday)

    output = []
    for week_start in sorted(week_demand.keys()):
        if week_start < this_week_start:
            continue
        week_end = week_start + timedelta(days=6)
        for type_key, info in week_demand[week_start].items():
            total_available = inventory.get(type_key, 0)
            demand = info['demand']
            sufficient = total_available >= demand
            output.append({
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'IntfCtgry': type_key[0] or 'N/A',
                'DevCtgry': type_key[1] or 'N/A',
                'Devproperties': type_key[2] or 'N/A',
                '需求量': demand,
                '库存量': total_available,
                '是否满足': '是' if sufficient else '否',
                '机种列表': list(info['projects'])
            })
    t2 = time.time()
    logger.info(f"生成输出耗时: {t2-t1:.2f}s, 输出 {len(output)} 条")

    result_data = {'data': output, 'count': len(output)}
    cache.set(cache_key, result_data, timeout=300)  # 5分钟

    logger.info(f"总耗时: {time.time() - start_total:.2f}s")
    return JsonResponse(result_data)

def get_requirement_items():
    """获取并缓存需求项列表 (type_key, nid)，优化匹配速度"""
    cache_key = 'requirement_items_v2'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    test_records = TestDeviceLNV.objects.all()
    if not test_records.exists():
        return []

    # 获取可用设备（排除 Damaged/Lost）
    all_devices = list(DeviceLNV.objects.exclude(
        Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')
    ))

    # 预计算设备信息
    device_infos = []
    for dev in all_devices:
        full_lower = f"{dev.DevName} {dev.DevModel} {dev.DevVendor}".lower()
        name_model_lower = f"{dev.DevName} {dev.DevModel}".lower()
        device_infos.append({
            'dev': dev,
            'full_lower': full_lower,
            'name_model_lower': name_model_lower,
            'nid': dev.NID,
        })

    req_items = []
    for rec in test_records:
        # 优先使用 Device1
        nid = rec.Device1 if rec.Device1 else None
        if nid:
            dev = next((d for d in all_devices if d.NID == nid), None)
            if dev:
                type_key = (dev.IntfCtgry, dev.DevCtgry, dev.Devproperties)
                req_items.append((type_key, nid))
                continue

        # 获取 Type 名称
        type_name = rec.Type or ''
        if not type_name and rec.Category and rec.Class:
            type_name = f"{rec.Category}|{rec.Class}"
        if not type_name:
            continue

        type_lower = type_name.lower()
        matched_nid = None

        # 1. 精确包含匹配（快速）
        for info in device_infos:
            if type_lower in info['full_lower']:
                matched_nid = info['nid']
                break

        # 2. 单词匹配（拆分 type_name 为单词，要求所有单词都在 full_lower 中出现）
        if not matched_nid:
            import re
            words = re.split(r'[\s|]+', type_lower)
            words = [w for w in words if len(w) > 2]
            if words:
                # 先尝试匹配所有单词
                for info in device_infos:
                    if all(w in info['full_lower'] for w in words):
                        matched_nid = info['nid']
                        break
                # 如果失败，降级为匹配任意一个单词
                if not matched_nid:
                    for info in device_infos:
                        if any(w in info['full_lower'] for w in words):
                            matched_nid = info['nid']
                            break

        # 3. 模糊匹配（作为最后手段，极少触发）
        if not matched_nid:
            from difflib import get_close_matches
            name_model_list = [info['name_model_lower'] for info in device_infos]
            closest = get_close_matches(type_lower, name_model_list, n=1, cutoff=0.6)
            if closest:
                for info in device_infos:
                    if info['name_model_lower'] == closest[0]:
                        matched_nid = info['nid']
                        break

        if matched_nid:
            dev = next(d for d in all_devices if d.NID == matched_nid)
            type_key = (dev.IntfCtgry, dev.DevCtgry, dev.Devproperties)
            req_items.append((type_key, matched_nid))
            # logger.info(f"为需求 '{type_name}' 匹配到设备 NID: {matched_nid}")
        else:
            # logger.warning(f"无法为需求 '{type_name}' 匹配任何设备")
            pass
    # 缓存1天（86400秒），因为设备库和需求表变化不频繁
    cache.set(cache_key, req_items, timeout=86400)
    return req_items