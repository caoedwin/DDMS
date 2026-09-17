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
# 尝试导入其他客户模型（若不存在则置为 None）
try:
    from DeviceLNV.models import DeviceLNV
except ImportError:
    DeviceLNV = None

try:
    from DeviceA31CD.models import DeviceA31CD
except ImportError:
    DeviceA31CD = None
try:
    from DeviceA31KS.models import DeviceA31KS
except ImportError:
    DeviceA31KS = None
try:
    from DeviceA31LKE.models import DeviceA31LKE
except ImportError:
    DeviceA31LKE = None
try:
    from DeviceA31PCP.models import DeviceA31PCP
except ImportError:
    DeviceA31PCP = None
try:
    from DeviceA31TPE.models import DeviceA31TPE
except ImportError:
    DeviceA31TPE = None
try:
    from DeviceA32KS.models import DeviceA32KS
except ImportError:
    DeviceA32KS = None
try:
    from DeviceA32TPE.models import DeviceA32TPE
except ImportError:
    DeviceA32TPE = None
try:
    from DeviceA39.models import DeviceA39
except ImportError:
    DeviceA39 = None
try:
    from DeviceABO.models import DeviceABO
except ImportError:
    DeviceABO = None
try:
    from DeviceAPDQATPE.models import DeviceAPDQATPE
except ImportError:
    DeviceAPDQATPE = None
try:
    from DeviceCQT88.models import DeviceCQT88
except ImportError:
    DeviceCQT88 = None

# 定义模型映射（只包含非 None 的模型）
DEVICE_MODELS = {
    'LNV': DeviceLNV,
}
if DeviceA31CD:
    DEVICE_MODELS['A31CD'] = DeviceA31CD
if DeviceA31KS:
    DEVICE_MODELS['A31KS'] = DeviceA31KS
if DeviceA31LKE:
    DEVICE_MODELS['A31LKE'] = DeviceA31LKE
if DeviceA31PCP:
    DEVICE_MODELS['A31PCP'] = DeviceA31PCP
if DeviceA31TPE:
    DEVICE_MODELS['A31TPE'] = DeviceA31TPE
if DeviceA32KS:
    DEVICE_MODELS['A32KS'] = DeviceA32KS
if DeviceA32TPE:
    DEVICE_MODELS['A32TPE'] = DeviceA32TPE
if DeviceA39:
    DEVICE_MODELS['A39'] = DeviceA39
if DeviceABO:
    DEVICE_MODELS['ABO'] = DeviceABO
if DeviceAPDQATPE:
    DEVICE_MODELS['APDQATPE'] = DeviceAPDQATPE
if DeviceCQT88:
    DEVICE_MODELS['CQT88'] = DeviceCQT88

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
    url = 'http://127.0.0.1:8002/TestPlanSW/api/token/'
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
    # print(all_projects)
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
    """计算综合评分及各项子分
    权重：使用年限10% + 使用次数40% + 技术先进性5% + 借用次数40% + EOL状态5%
    """
    # ---- 使用年限 10% ----
    pdate = parse_date(dev.Pchsdate)
    if pdate:
        years = (today - pdate).days / 365.25
        if years > 10:
            age_score = 100
        elif years > 8:
            age_score = 80
        elif years > 5:
            age_score = 60
        elif years > 1:
            age_score = 30
        else:
            age_score = 0
    else:
        age_score = 50

    # ---- 使用次数 40% ----
    use_count = dev.uscyc or 0
    try:
        use_count = int(use_count)
    except Exception:
        use_count = 0
    if use_count > 2000:
        usage_score = 100
    elif use_count > 1500:
        usage_score = 90
    elif use_count > 1000:
        usage_score = 80
    elif use_count > 500:
        usage_score = 70
    elif use_count > 200:
        usage_score = 40
    elif use_count > 100:
        usage_score = 20
    else:
        usage_score = 0

    # ---- 技术先进性 5% ----
    tech = tech_score(dev)

    # ---- 借用次数 40% ----
    usr = dev.UsrTimes or 0
    try:
        usr = int(usr)
    except Exception:
        usr = 0
    if usr > 500:
        borrow_score = 100
    elif usr > 300:
        borrow_score = 70
    elif usr > 200:
        borrow_score = 40
    elif usr > 100:
        borrow_score = 20
    else:
        borrow_score = 0

    # ---- EOL 状态 5% ----
    eol_date = parse_date(dev.EOL)
    if eol_date:
        if eol_date < today:
            eol_score = 100
        else:
            eol_score = 60
    else:
        eol_score = 0

    # 权重求和（合计 1.0）
    weights = [0.10, 0.40, 0.05, 0.40, 0.05]
    scores = [age_score, usage_score, tech, borrow_score, eol_score]
    total = sum(s * w for s, w in zip(scores, weights))
    return total, {
        'age': age_score,
        'usage': usage_score,
        'borrow': borrow_score,
        'tech': tech,
        'eol': eol_score,
        'status': 0,  # 状态分已从权重中移除，保留字段以兼容前端
    }

def upgrade_suggestion(dev, score):
    """
    生成升级建议（新版逻辑）：
    - 设备状态 Damaged / Lost：需要购买（优先级紧急更换）
    - 同类可用设备数量不足（Monitor 除外，至少 2 台）：需要购买（紧急更换）
    - 综合评分 >= 80：评估购买（酌情更换）
    - 40 ~ 79：可观察
    - < 40：继续使用
    技术建议完整保留，末尾追加数量评估信息。
    """
    # ---------- 1. 价格解析 ----------
    price_raw = getattr(dev, 'DevPrice', None) or '0'
    try:
        import re
        price_str = re.sub(r'[^0-9.]', '', str(price_raw))
        price = float(price_str) if price_str else 0.0
    except (ValueError, TypeError):
        price = 0.0

    # ---------- 2. 判断是否 monitor 类 + 统计同类可用数量 ----------
    ctgry = (dev.DevCtgry or '').lower()
    is_monitor = ('monitor' in ctgry)

    same_type_available = 0
    try:
        model_class = dev.__class__
        same_type_available = model_class.objects.filter(
            IntfCtgry=dev.IntfCtgry,
            DevCtgry=dev.DevCtgry,
            Devproperties=dev.Devproperties,
        ).exclude(
            Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')
        ).count()
    except Exception:
        same_type_available = 0

    target_count = 2  # 非 Monitor 类型同类至少 2 台

    # ---------- 3. 优先级判定 ----------
    status_lower = (dev.DevStatus or '').lower()
    is_damaged_lost = ('damaged' in status_lower or 'lost' in status_lower)
    qty_shortage = (not is_monitor) and (same_type_available < target_count)

    if is_damaged_lost:
        base_priority = "紧急更换"
    elif qty_shortage:
        base_priority = "紧急更换"
    elif score >= 80:
        base_priority = "酌情更换"
    elif score >= 40:
        base_priority = "可观察"
    else:
        base_priority = "继续使用"

    final_priority = base_priority

    # ---------- 4. 生成技术建议（保留原有逻辑） ----------
    ctgry = (dev.DevCtgry or '').lower()
    prop = (dev.Devproperties or '').lower()
    intf = (dev.IntfCtgry or '').lower()
    dev_desc = (dev.DevDescription or '').lower()
    combined_text = f"{prop} {dev_desc} {intf}".lower()

    base_suggestion = "暂无特殊建议"
    if 'mouse' in ctgry or 'keyboard' in ctgry:
        if 'mouse' in ctgry:
            base_suggestion = "推荐升级至蓝牙5.0/5.2无线鼠标，支持多设备切换，更高DPI。"
        else:
            base_suggestion = "推荐升级至USB-C或蓝牙机械键盘，支持多模连接。"
    elif 'usb memory' in ctgry:
        base_suggestion = "推荐升级至USB 3.1/3.2接口、容量≥128GB的高速U盘。"
    elif 'hdd' in ctgry or 'ssd' in ctgry:
        if 'hdd' in prop:
            base_suggestion = "强烈建议更换为NVMe SSD或USB3.2外置固态硬盘。"
        else:
            base_suggestion = "考虑升级为Thunderbolt 3/4或USB4接口的外置SSD。"
    elif 'headphone' in ctgry or 'speaker' in ctgry:
        base_suggestion = "推荐升级至蓝牙5.2+ANC主动降噪耳机，或Type-C有线高解析度耳机。"
    elif 'ap' in ctgry or 'router' in ctgry:
        base_suggestion = "推荐升级至Wi-Fi 6/6E路由器，支持OFDMA和更高速率。"
    elif 'card reader' in ctgry:
        base_suggestion = "升级至USB3.1读卡器，支持UHS-II SD卡。"
    elif 'hub' in ctgry or 'dongle' in ctgry:
        base_suggestion = "考虑升级为USB-C多功能扩展坞，支持4K输出、千兆网口、PD充电。"
    elif 'monitor' in ctgry:
        base_suggestion = "升级至4K分辨率、高刷新率、支持DisplayPort 1.4或Type-C一线连的显示器。"
    elif 'odd' in ctgry:
        base_suggestion = "当前光驱技术已过时，如必要可更换为外置蓝光刻录机。"
    elif 'camera' in ctgry:
        base_suggestion = "推荐升级至USB3.0或Type-C接口的4K网络摄像头。"
    elif 'cable' in ctgry or 'audio jack' in ctgry:
        base_suggestion = "建议更换为HDMI 2.1、DP 1.4或雷电4线缆。"
    elif 'power adapter' in ctgry or ('adapter' in ctgry and 'power' in prop):
        base_suggestion = "推荐升级至氮化镓(GaN)充电器，支持USB-C PD快充。"
    elif 'phone' in ctgry or 'ipad' in ctgry or 'iphone' in ctgry or 'tablet' in ctgry:
        base_suggestion = "建议升级至支持5G、无线充电和快充的当前主流手机/平板。"
    elif 'game' in ctgry or 'joystick' in ctgry or 'gamepad' in ctgry:
        base_suggestion = "推荐升级至支持蓝牙5.0+、低延迟无线或有线USB-C的游戏手柄。"
    elif 'microphone' in ctgry:
        base_suggestion = "建议升级至USB-C接口或支持高采样率的专业麦克风。"
    elif 'projector' in ctgry:
        base_suggestion = "推荐升级至4K激光投影仪，支持HDR和无线投屏。"
    else:
        base_suggestion = "建议对照最新技术规范进行资产评估。"

    # ---------- Monitor 碎屏险建议 ----------
    insurance_advice = ""
    if 'monitor' in ctgry:
        def get_panel_type():
            if 'oled' in combined_text:
                return 'OLED'
            elif 'mini-led' in combined_text:
                return 'Mini-LED'
            elif '曲面' in combined_text:
                return '曲面屏'
            elif 'ips' in combined_text:
                return 'IPS'
            elif 'va' in combined_text:
                return 'VA'
            elif 'tn' in combined_text:
                return 'TN'
            else:
                return '未知面板类型'

        panel = get_panel_type()
        need_insurance = False
        reasons = []
        if price >= 6000:
            if '曲面' in combined_text and 'oled' in combined_text:
                need_insurance = True
                reasons.append(f"价格≥6000元且{panel}（曲面OLED）")
            elif 'oled' in combined_text:
                need_insurance = True
                reasons.append(f"价格≥6000元且{panel}")
            elif any(key in combined_text for key in ['窄边框', '无边框', '窄/无边框']):
                need_insurance = True
                reasons.append(f"价格≥6000元且{panel}（窄/无边框）")
            else:
                reasons.append(f"价格≥6000元，但当前面板为【{panel}】，不属于推荐类型")
        else:
            reasons.append(f"价格{price}元（低于6000元），当前面板为【{panel}】")

        if need_insurance and reasons:
            insurance_advice = f"当前设备【强烈建议】购买碎屏险。原因：{', '.join(reasons)}。屏幕维修成本高，建议额外购买意外保障。"
        else:
            insurance_advice = f"当前设备【不建议】购买碎屏险。原因：{', '.join(reasons)}，购买保险性价比不高。"

        tech_suggestion = base_suggestion + " " + insurance_advice
    else:
        tech_suggestion = base_suggestion

    # ---------- 5. 末尾追加数量评估信息 ----------
    if is_monitor:
        quantity_info = "（Monitor 类设备无需数量检查）"
    elif same_type_available >= target_count:
        quantity_info = f"（同类可用设备 {same_type_available} 台，已满足至少 {target_count} 台，无需额外采购）"
    else:
        quantity_info = f"（同类可用设备仅 {same_type_available} 台，未达 {target_count} 台，建议采购）"

    if is_damaged_lost:
        quantity_info += "；设备已损坏/丢失，新设备入库后请将原设备状态改为 Replaced。"

    final_suggestion = tech_suggestion + " " + quantity_info
    return final_priority, final_suggestion

def match_audit_type_to_device_type(rec):
    """
    预留接口：根据 audit 记录的字段推断设备库中的类型三元组。
    返回 dict 形如 {'IntfCtgry':..., 'DevCtgry':..., 'Devproperties':...} 或 None。

    目前 audit list 的 Category/Class/Type 与设备库字段尚未对齐，
    后期会改造为一致格式后在此补充映射逻辑。
    """
    return None


def evaluate_audit_record(rec, today):
    """
    评估单条 audit 记录，决定是否需要采购。

    返回 dict:
        Need_Purchase      : bool
        Suggestion_Level   : '无需购买' / '考虑更换' / '建议更换'
        Score              : 0 / 60 / 80
        Bound_Devices      : Device1~Device10 中存在的设备详细信息
        Missing_NIDs       : Device1~Device10 中在设备库中查不到的 NID
        Available_Devices  : 最终可用设备列表（好设备或同类型设备）
        Reason             : 判定原因
        Matched_Type_Count : 同类型可用数量
    """
    # ---------- 1. 收集 Device1~Device10 中的 NID ----------
    device_nids = []
    for i in range(1, 11):
        nid = getattr(rec, f'Device{i}', None)
        if nid and str(nid).strip():
            device_nids.append(str(nid).strip())

    # ---------- 2. 逐个查设备库 ----------
    good_devices = []    # 非 Damaged/Lost 且评分 < 80
    bound_devices = []   # 所有在设备库中能查到的绑定设备（无论好坏）
    missing_nids = []    # 在设备库中查不到的
    ref_dev = None       # 用于推断同类型（取第一个查到的绑定设备）

    for nid in device_nids:
        try:
            dev = DeviceLNV.objects.filter(NID=nid).first()
        except Exception:
            dev = None
        if not dev:
            missing_nids.append(nid)
            continue

        total, _ = compute_score(dev, today)
        status_lower = (dev.DevStatus or '').lower()
        is_damaged_lost = ('damaged' in status_lower or 'lost' in status_lower)

        info = {
            'NID': nid,
            'DevStatus': dev.DevStatus or '',
            'BrwStatus': dev.BrwStatus or '',
            'DevModel': dev.DevModel or '',
            'DevName': dev.DevName or '',
            'Score': round(total, 2),
        }
        bound_devices.append(info)
        if ref_dev is None:
            ref_dev = dev
        if (not is_damaged_lost) and total < 80:
            good_devices.append(info)

    # ---------- 3. 场景 A：存在好设备 ----------
    if good_devices:
        return {
            'Need_Purchase': False,
            'Suggestion_Level': '无需购买',
            'Score': 0,
            'Bound_Devices': bound_devices,
            'Missing_NIDs': missing_nids,
            'Available_Devices': good_devices,
            'Reason': '已绑定可用设备：' + '、'.join(d['NID'] for d in good_devices),
            'Matched_Type_Count': 0,
        }

    # ---------- 4. 场景 B/C：无好设备，尝试找同类型可用设备 ----------
    same_type_available_devices = []
    used_type = None

    if ref_dev is not None:
        used_type = {
            'IntfCtgry': ref_dev.IntfCtgry,
            'DevCtgry': ref_dev.DevCtgry,
            'Devproperties': ref_dev.Devproperties,
        }
    else:
        used_type = match_audit_type_to_device_type(rec)

    is_monitor = False
    if used_type:
        is_monitor = 'monitor' in (used_type.get('DevCtgry') or '').lower()

    if used_type and not is_monitor:
        try:
            qs = DeviceLNV.objects.filter(
                IntfCtgry=used_type.get('IntfCtgry'),
                DevCtgry=used_type.get('DevCtgry'),
                Devproperties=used_type.get('Devproperties'),
            ).exclude(
                Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')
            )
            for d in qs:
                same_type_available_devices.append({
                    'NID': d.NID,
                    'DevStatus': d.DevStatus or '',
                    'BrwStatus': d.BrwStatus or '',
                    'DevModel': d.DevModel or '',
                    'DevName': d.DevName or '',
                })
        except Exception:
            same_type_available_devices = []

    # ---------- 5. 场景 B：同类型有可用设备 ----------
    if same_type_available_devices:
        return {
            'Need_Purchase': False,
            'Suggestion_Level': '考虑更换',
            'Score': 60,
            'Bound_Devices': bound_devices,
            'Missing_NIDs': missing_nids,
            'Available_Devices': same_type_available_devices,
            'Reason': f"无可用绑定设备，但同类型有 {len(same_type_available_devices)} 台可替换，建议考虑更换",
            'Matched_Type_Count': len(same_type_available_devices),
        }

    # ---------- 6. 场景 C：同类型也无可用 → 建议更换 ----------
    if is_monitor:
        reason = '绑定设备不可用，Monitor 类不做同类型匹配，建议采购'
    elif ref_dev is None and used_type is None:
        reason = '无绑定设备且暂未支持同类型匹配，建议采购'
    else:
        reason = '无可用绑定设备，且同类型无可用库存，建议采购'
    return {
        'Need_Purchase': True,
        'Suggestion_Level': '建议更换',
        'Score': 80,
        'Bound_Devices': bound_devices,
        'Missing_NIDs': missing_nids,
        'Available_Devices': [],
        'Reason': reason,
        'Matched_Type_Count': 0,
    }


def match_audit_by_device_library(rec):
    """
    预留接口：根据 audit 记录的 Category / Class / Type 去设备库匹配。
    （等 audit list 格式改成 device 库的格式后启用）
    目前返回空列表，即不做自动匹配。
    """
    return []


def get_audit_list_data():
    """获取所有 Require_State=Must 的 audit list 记录，并做设备采购评估

    注意：TestDeviceLNV 表中某些行多个字段存在"合并标识"，
    还原规则：按 id 升序扫描全表，每个字段都用"最近一次出现的非'合并标识'值"覆盖。
    还原完成后再过滤 Require_State='Must'。
    """
    cache_key = 'audit_list_data_v5'   # 版本升级，确保刷新
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    today = datetime.now().date()

    # ---------- 1. 按 id 排序取全部记录 ----------
    all_records = list(TestDeviceLNV.objects.all().order_by('id'))
    MERGE_TAG = '合并标识'

    restore_fields = [
        'Category',
        'Class',
        'Type',
        'Covered_range_for_case',
        'Require_State',
        'Comments',
        'Remark',
        'ODM_status',
        'Purchase_Plan',
        'Act_Status',
        'Device_Know_Issue',
    ]

    # ---------- 2. 逐行还原每个字段 ----------
    current_values = {f: '' for f in restore_fields}
    filled_records = []
    for rec in all_records:
        restored = {}
        for f in restore_fields:
            val = getattr(rec, f, None)
            val_str = str(val).strip() if val is not None else ''
            if val_str == MERGE_TAG:
                restored[f] = current_values[f]
            else:
                current_values[f] = val_str
                restored[f] = val_str
        filled_records.append({'rec': rec, 'restored': restored})

    # ---------- 3. 过滤出 Require_State=Must 的记录 ----------
    must_records = [
        item for item in filled_records
        if (item['restored'].get('Require_State', '') or '').strip().lower() == 'must'
    ]

    # ---------- 4. 组装输出 ----------
    result = []
    for item in must_records:
        rec = item['rec']
        r = item['restored']
        ev = evaluate_audit_record(rec, today)

        result.append({
            'id': rec.id,
            'Category': r.get('Category', ''),
            'Class': r.get('Class', ''),
            'Type': r.get('Type', ''),
            'Require_State': r.get('Require_State', ''),
            'Covered_range_for_case': r.get('Covered_range_for_case', ''),
            'Comments': r.get('Comments', ''),
            'Remark': r.get('Remark', ''),

            # 采购评估结果
            'Need_Purchase': ev['Need_Purchase'],
            'Suggestion_Level': ev['Suggestion_Level'],
            'Score': ev['Score'],
            'Reason': ev['Reason'],
            'Matched_Type_Count': ev['Matched_Type_Count'],

            # 设备信息
            'Device_NIDs': '、'.join(
                [str(getattr(rec, f'Device{i}', '') or '') for i in range(1, 11)
                 if getattr(rec, f'Device{i}', None)]
            ),
            'Bound_Devices': ev['Bound_Devices'],
            'Missing_NIDs': ev['Missing_NIDs'],
            'Available_Devices': ev['Available_Devices'],
        })

    cache.set(cache_key, result, timeout=300)
    return result
# ===================== JSON 接口视图 =====================
from django.core.cache import cache
from django.db.models import Q

@csrf_exempt
@csrf_exempt
def device_score_view(request):
    """统一入口：返回模型列表 / 设备评分数据 / Audit list 数据"""
    # 返回客户列表（用于前端下拉）
    if request.method == 'GET' and request.GET.get('action') == 'get_models':
        data = [{'key': k, 'name': k} for k in DEVICE_MODELS.keys()]
        return JsonResponse(data, safe=False)
    if request.method == 'POST' and request.POST.get('action') == 'get_models':
        data = [{'key': k, 'name': k} for k in DEVICE_MODELS.keys()]
        return JsonResponse(data, safe=False)

    # 返回 Audit list 数据
    if request.method == 'GET' and request.GET.get('action') == 'get_audit_list':
        audit_data = get_audit_list_data()
        return JsonResponse({'data': audit_data, 'count': len(audit_data)})
    if request.method == 'POST' and request.POST.get('action') == 'get_audit_list':
        audit_data = get_audit_list_data()
        return JsonResponse({'data': audit_data, 'count': len(audit_data)})

    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    model_key = request.GET.get('model', 'LNV')
    model = DEVICE_MODELS.get(model_key)
    if not model:
        return JsonResponse({'error': f'Unknown model: {model_key}'}, status=400)

    # 缓存键改为 _v2 避免旧缓存干扰
    cache_key = f'device_score_data_{model_key}_v2'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return JsonResponse(cached_data)

    today = datetime.now().date()
    result = []

    # 查询包含 Devsize 字段（用于统计）
    devices = model.objects.only(
        'id', 'NID', 'DevVendor', 'DevModel', 'DevName', 'DevCtgry',
        'DevStatus', 'Pchsdate', 'UsrTimes', 'uscyc', 'Devproperties',
        'IntfCtgry', 'Devsize', 'EOL', 'DevPrice',
        'DevDescription'
    )

    for dev in devices:
        total, detail = compute_score(dev, today)
        urgency, sug = upgrade_suggestion(dev, total)

        # 同类可用数量（仅展示用）
        is_monitor = 'monitor' in (dev.DevCtgry or '').lower()
        same_type = 0
        try:
            same_type = model.objects.filter(
                IntfCtgry=dev.IntfCtgry,
                DevCtgry=dev.DevCtgry,
                Devproperties=dev.Devproperties,
            ).exclude(
                Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')
            ).count()
        except Exception:
            same_type = 0

        result.append({
            'id': dev.id,
            'NID': dev.NID,
            'IntfCtgry': dev.IntfCtgry or '',
            'DevCtgry': dev.DevCtgry or '',
            'Devproperties': dev.Devproperties or '',
            'DevVendor': dev.DevVendor,
            'DevModel': dev.DevModel,
            'DevName': dev.DevName,
            'DevStatus': dev.DevStatus,
            'Devsize': dev.Devsize or '',
            'Score': round(total, 2),
            'Priority': urgency,
            'DevPrice': dev.DevPrice,
            'Suggestion': sug,
            'AgeScore': detail['age'],
            'UsageScore': detail['usage'],
            'BorrowScore': detail['borrow'],
            'TechScore': detail['tech'],
            'EOLScore': detail['eol'],
            'StatusScore': detail['status'],
            'IsMonitor': is_monitor,
            'SameTypeAvailable': same_type,
            'NeedPurchase': urgency in ('紧急更换',),
        })

    # ---------- 排序：先按优先级，再按得分降序 ----------
    priority_order = {"紧急更换": 1, "酌情更换": 2, "可观察": 3, "继续使用": 4}
    result.sort(key=lambda x: (priority_order.get(x['Priority'].strip(), 5), -x['Score']))

    response_data = {'data': result, 'count': len(result), 'model': model_key}
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
    import time
    start_total = time.time()

    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # 固定测试日期，正式时改为 datetime.now().date()
    today = datetime(2019, 1, 29).date()
    # today = datetime.now().date()

    cache_key = f'demand_week_result_{today.isoformat()}'
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return JsonResponse(cached_result)

    # 1. 获取需求单元
    t1 = time.time()
    req_units = get_requirement_items()
    t2 = time.time()
    logger.info(f"获取需求项耗时: {t2-t1:.2f}s, 共 {len(req_units)} 个需求单元")
    if not req_units:
        return JsonResponse({'error': '无法获取需求项'}, status=404)

    # 按 type_key 分组统计需求量和明细
    type_demand = defaultdict(int)
    type_units = defaultdict(list)
    for unit in req_units:
        tk = unit['type_key']
        if tk is not None:
            type_demand[tk] += 1
            type_units[tk].append(unit)
        else:
            # 未匹配
            tk = ('未匹配', '未匹配', '未匹配')
            type_demand[tk] += 1
            type_units[tk].append(unit)

    # 统计库存
    inventory = defaultdict(int)
    inventory_nids = defaultdict(list)
    for dev in DeviceLNV.objects.exclude(Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')):
        tk = (dev.IntfCtgry or '', dev.DevCtgry or '', dev.Devproperties or '')
        inventory[tk] += 1
        inventory_nids[tk].append(dev.NID)

    # 2. 获取项目计划
    t1 = time.time()
    projects = fetch_testprojects()
    t2 = time.time()
    logger.info(f"获取项目计划耗时: {t2-t1:.2f}s, 共 {len(projects) if projects else 0} 个项目")
    if not projects:
        return JsonResponse({'error': '无法获取项目计划数据'}, status=500)

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
    if not valid_projects:
        return JsonResponse({'error': '没有有效的项目计划数据'}, status=404)

    # 3. 按周汇总需求
    t1 = time.time()
    week_demand = defaultdict(lambda: defaultdict(lambda: {'demand': 0, 'projects': set(), 'units': [], '_seen_units': set()}))

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
                for tk, demand_count in type_demand.items():
                    week_demand[week_start][tk]['demand'] += demand_count
                    week_demand[week_start][tk]['projects'].add(proj_info)
                    # 添加明细单元（去重）
                    for unit in type_units.get(tk, []):
                        key = (unit['category'], unit['class'], unit['type'], unit['require_state'], unit['nid'], unit['is_must'])
                        if key not in week_demand[week_start][tk]['_seen_units']:
                            week_demand[week_start][tk]['_seen_units'].add(key)
                            week_demand[week_start][tk]['units'].append(unit)
            week_start += timedelta(days=7)
    t2 = time.time()
    logger.info(f"按周汇总耗时: {t2-t1:.2f}s, 共 {len(week_demand)} 周")

    # 4. 生成输出
    t1 = time.time()
    days_since_monday = today.weekday()
    this_week_start = today - timedelta(days=days_since_monday)

    output = []
    for week_start in sorted(week_demand.keys()):
        if week_start < this_week_start:
            continue
        week_end = week_start + timedelta(days=6)
        for tk, info in week_demand[week_start].items():
            units_for_display = [{
                'category': u['category'],
                'class': u['class'],
                'type': u['type'],
                'require_state': u['require_state'],
                'is_must': u['is_must'],
                'nid': u['nid'] or '未匹配',
                'dev_vendor': u.get('dev_vendor', ''),
                'dev_model': u.get('dev_model', ''),
                'dev_name': u.get('dev_name', ''),
            } for u in info['units']]
            output.append({
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'IntfCtgry': tk[0] or 'N/A',
                'DevCtgry': tk[1] or 'N/A',
                'Devproperties': tk[2] or 'N/A',
                '需求量': info['demand'],
                '库存量': inventory.get(tk, 0),
                '是否满足': '是' if inventory.get(tk, 0) >= info['demand'] else '否',
                '机种列表': list(info['projects']),
                '库存设备NID': ','.join(inventory_nids.get(tk, [])),
                '需求项明细': units_for_display,
            })
    t2 = time.time()
    logger.info(f"生成输出耗时: {t2-t1:.2f}s, 输出 {len(output)} 条")

    result_data = {'data': output, 'count': len(output)}
    cache.set(cache_key, result_data, timeout=300)
    logger.info(f"总耗时: {time.time() - start_total:.2f}s")
    return JsonResponse(result_data)

import re
from collections import defaultdict
from rapidfuzz import fuzz, process
from django.db.models import Q
import logging

logger = logging.getLogger('django')

# 在 views.py 中替换或添加以下函数

def get_requirement_items():
    """
    返回需求单元列表，每个单元包含：
        category, class, type, require_state,
        type_key, nid, is_must,
        dev_vendor, dev_model, dev_name
    """
    cache_key = 'requirement_items_v5'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 获取所有 Active 记录，按 id 排序
    records = list(TestDeviceLNV.objects.filter(Act_Status__iexact='Active').order_by('id'))
    if not records:
        return []

    # 填充合并标识
    filled_records = []
    current_category = None
    current_class = None
    for rec in records:
        cat = rec.Category or ''
        cls = rec.Class or ''
        if cat != '合并标识':
            current_category = cat
        if cls != '合并标识':
            current_class = cls
        real_category = current_category if cat == '合并标识' else cat
        real_class = current_class if cls == '合并标识' else cls
        filled_records.append({
            'id': rec.id,
            'Category': real_category,
            'Class': real_class,
            'Type': rec.Type or '',
            'Require_State': rec.Require_State or '',
            'Comments': rec.Comments or '',
            'original': rec,
        })

    # 按 Category 分组
    groups = defaultdict(list)
    for rec in filled_records:
        groups[rec['Category']].append(rec)

    # 获取可用设备
    all_devices = list(DeviceLNV.objects.exclude(
        Q(DevStatus__iexact='Damaged') | Q(DevStatus__iexact='Lost')
    ))
    device_infos = []
    for dev in all_devices:
        match_str = f"{dev.IntfCtgry or ''} {dev.DevCtgry or ''} {dev.Devproperties or ''} {dev.DevVendor or ''} {dev.Devsize or ''} {dev.DevModel or ''} {dev.DevName or ''}".lower()
        device_infos.append({
            'dev': dev,
            'match_str': match_str,
            'nid': dev.NID,
            'vendor': (dev.DevVendor or '').lower(),
            'intf': (dev.IntfCtgry or '').lower(),
            'type_key': (dev.IntfCtgry or '', dev.DevCtgry or '', dev.Devproperties or ''),
            'status': (dev.DevStatus or '').lower(),
            'dev_model': (dev.DevModel or '').lower(),
        })

    req_units = []

    for category, recs in groups.items():
        # 取 Comments
        comments = ''
        for r in recs:
            if r['Comments']:
                comments = r['Comments']
                break

        # 分离 Must 和 Optional
        must_recs = [r for r in recs if r['Require_State'].lower() in ('must', 'unique must')]
        opt_recs = [r for r in recs if r['Require_State'].lower() not in ('must', 'unique must')]

        # 处理 Must：每条独立
        for rec in must_recs:
            parts = [rec['Category'], rec['Class'], rec['Type']]
            match_str = ' '.join([p for p in parts if p]).strip().lower()
            if not match_str:
                match_str = rec['Type'].lower()
            matched_info = None
            if match_str:
                matched_info = match_single_device(match_str, device_infos)
            req_units.append({
                'category': rec['Category'],
                'class': rec['Class'],
                'type': rec['Type'],
                'require_state': rec['Require_State'],
                'type_key': matched_info['type_key'] if matched_info else None,
                'nid': matched_info['nid'] if matched_info else None,
                'is_must': True,
                'dev_vendor': matched_info['dev'].DevVendor if matched_info else '',
                'dev_model': matched_info['dev'].DevModel if matched_info else '',
                'dev_name': matched_info['dev'].DevName if matched_info else '',
            })

        # 处理 Optional：整组选取
        if opt_recs:
            quantity = 1
            required_vendors = 0
            require_a = False
            require_c = False
            if comments:
                num_match = re.search(r'(\d+)\s*(?:device|devices|unit)', comments, re.IGNORECASE)
                if num_match:
                    quantity = int(num_match.group(1))
                else:
                    quantity = len(opt_recs)
                vendor_match = re.search(r'(\d+)\s*vendor', comments, re.IGNORECASE)
                if vendor_match:
                    required_vendors = int(vendor_match.group(1))
                if 'a port' in comments.lower() or 'type-a' in comments.lower():
                    require_a = True
                if 'c port' in comments.lower() or 'type-c' in comments.lower():
                    require_c = True

            # 构建候选设备
            candidates = []
            seen_nids = set()
            for rec in opt_recs:
                parts = [rec['Category'], rec['Class'], rec['Type']]
                match_str = ' '.join([p for p in parts if p]).strip().lower()
                if not match_str:
                    match_str = rec['Type'].lower()
                if not match_str:
                    continue
                # 包含匹配
                for info in device_infos:
                    if match_str in info['match_str']:
                        if info['nid'] not in seen_nids:
                            seen_nids.add(info['nid'])
                            candidates.append(info)
                # 模糊匹配
                if len(candidates) < quantity:
                    fuzzy_list = [info['match_str'] for info in device_infos if info['nid'] not in seen_nids]
                    if fuzzy_list:
                        matches = process.extract(match_str, fuzzy_list, scorer=fuzz.token_sort_ratio, limit=20, score_cutoff=65)
                        for matched_str, score, idx in matches:
                            info = device_infos[idx]
                            if info['nid'] not in seen_nids:
                                seen_nids.add(info['nid'])
                                candidates.append(info)
            if not candidates:
                logger.warning(f"Optional 组 (Category={category}) 无匹配设备")
                for rec in opt_recs:
                    req_units.append({
                        'category': rec['Category'],
                        'class': rec['Class'],
                        'type': rec['Type'],
                        'require_state': rec['Require_State'],
                        'type_key': None,
                        'nid': None,
                        'is_must': False,
                        'dev_vendor': '',
                        'dev_model': '',
                        'dev_name': '',
                    })
                continue

            # 按状态排序
            status_priority = {'good': 0, 'fixed': 1, 'long': 2}
            candidates.sort(key=lambda x: status_priority.get(x['status'], 3))
            selected = select_devices(candidates, quantity, required_vendors, require_a, require_c)

            sample_rec = opt_recs[0]
            for info in selected:
                req_units.append({
                    'category': sample_rec['Category'],
                    'class': sample_rec['Class'],
                    'type': sample_rec['Type'],
                    'require_state': sample_rec['Require_State'],
                    'type_key': info['type_key'],
                    'nid': info['nid'],
                    'is_must': False,
                    'dev_vendor': info['dev'].DevVendor if info.get('dev') else '',
                    'dev_model': info['dev'].DevModel if info.get('dev') else '',
                    'dev_name': info['dev'].DevName if info.get('dev') else '',
                })

    logger.info(f"生成需求单元数: {len(req_units)}")
    cache.set(cache_key, req_units, timeout=86400)
    return req_units


def match_single_device(match_str, device_infos, threshold=50):
    if not match_str:
        return None
    # 1. 子串包含匹配（match_str 在设备的 match_str 中）
    for info in device_infos:
        if match_str in info['match_str']:
            return info
    # 2. 反向包含：设备的 DevModel 出现在 match_str 中
    for info in device_infos:
        if info.get('dev_model') and info['dev_model'] in match_str:
            return info
    # 3. 模糊匹配（降低阈值）
    fuzzy_list = [info['match_str'] for info in device_infos]
    matches = process.extract(match_str, fuzzy_list, scorer=fuzz.token_sort_ratio, limit=1, score_cutoff=threshold)
    if matches:
        idx = matches[0][2]
        return device_infos[idx]
    return None


def select_devices(candidates, required_count, required_vendors=0, require_a=False, require_c=False):
    """从候选中按厂商分散选取设备，满足厂商数和接口要求"""
    if not candidates:
        return []

    # 按厂商分组
    vendor_groups = defaultdict(list)
    for info in candidates:
        vendor_groups[info['vendor']].append(info)

    # 检查可用厂商数
    vendors_available = list(vendor_groups.keys())
    if required_vendors > 0 and len(vendors_available) < required_vendors:
        logger.warning(f"要求 {required_vendors} 个厂商，实际只有 {len(vendors_available)} 个")

    selected = []
    # 轮询各厂商，每次取一个
    vendor_cycle = vendors_available[:]

    while len(selected) < required_count and candidates:
        for vendor in vendor_cycle:
            if len(selected) >= required_count:
                break
            if vendor_groups.get(vendor):
                info = vendor_groups[vendor].pop(0)
                # 接口检查（如果有要求）
                if require_a and 'a' not in info['intf']:
                    logger.debug(f"设备 {info['nid']} 不满足 A 口要求，但仍选取")
                if require_c and 'c' not in info['intf']:
                    logger.debug(f"设备 {info['nid']} 不满足 C 口要求，但仍选取")
                selected.append(info)
                candidates = [c for c in candidates if c['nid'] != info['nid']]
        vendor_cycle = [v for v in vendor_cycle if vendor_groups.get(v)]
        if not vendor_cycle and len(selected) < required_count:
            # 补足
            for info in candidates:
                if len(selected) >= required_count:
                    break
                selected.append(info)
            break

    if len(selected) < required_count:
        for info in candidates:
            if len(selected) >= required_count:
                break
            if info not in selected:
                selected.append(info)

    return selected

