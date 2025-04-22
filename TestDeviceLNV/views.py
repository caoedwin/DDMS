from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime,os, json
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




@csrf_exempt
def TestDeviceListLNV(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "TestDeviceLNV/TestDeviceListLNV"
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
            if datetime.datetime.now().date() > i.Pchsdate:
                Purchase_period = round(
                    float(
                        str((datetime.datetime.now().date() - i.Pchsdate)).split(' ')[
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
                        if datetime.datetime.now().date() > Device_obj.Pchsdate:
                            Useyears_dict[keyUse] = round(
                                float(
                                    str((datetime.datetime.now().date() - Device_obj.Pchsdate)).split(' ')[
                                        0]) / 365,
                                1)
            mock_dic = {"id": i.id, "Category": i.Category, "Class": i.Class,
                        "Type": i.Type, "Covered_range_for_case": i.Covered_range_for_case,
                        "Require_State": i.Require_State,
                        "Comments": i.Comments, "Remark": i.Remark, "ODM_status": i.ODM_status,
                        "Purchase_Plan": i.Purchase_Plan, "Device_Price": i.Device_Price,
                        "Act_Status": i.Act_Status,
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


