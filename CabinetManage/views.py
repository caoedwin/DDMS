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
headermodel_Device = {
    '客戶別': 'Customer', '廠區': 'Plant', '設備序號': 'NID',
    # '設備編號': 'DevID',
    '設備用途': 'DevID',
    '介面種類': 'IntfCtgry', '設備種類': 'DevCtgry', '設備屬性': 'Devproperties', '設備廠家': 'DevVendor',
    '設備容量': 'Devsize', '設備型號': 'DevModel', '設備名稱': 'DevName',
    '借還狀態': 'BrwStatus', '用戶名稱': 'Usrname', '預計歸還日期': 'Plandate',
    # '使用天數': 'useday',
    '借用時間': 'Btime', '歸還日期': 'Rtime', '備註': 'Comment', #"超期天數": "Overday"实时计算出来的

    'HW Ver.': 'HWVer', 'FW Ver.': 'FWVer',
    '設備描述': 'DevDescription', '附帶品': 'PckgIncludes', '保固期': 'expirdate', '價值 RMB(單價)': 'DevPrice',
    '設備來源': 'Source', '購買時間': 'Pchsdate', '料號': 'PN', 'LNV/ABO 設備審核清单': 'LSTA',
    '申購單號': 'ApplicationNo', '報關單號': 'DeclarationNo', '資產編號': 'AssetNum', #"購買年限": "UsYear"实时计算出来的
    '使用次數': 'uscyc', '借還次數': 'UsrTimes', '設備添加人員': 'addnewname',
    '設備添加日期': 'addnewdate', '設備狀態': 'DevStatus',
    'EOL日期': 'EOL',

    '借還人員工號': 'BR_per_code',
    '機種': 'ProjectCode', 'Phase': 'Phase',
    '上一次借用人員': 'LastUsrname', '上一次借用人員工号': 'Last_BR_per_code', '上一次預計歸還日期': 'Last_Predict_return',
    '上一次借用日期': 'Last_Borrow_date', '上一次歸還日期': 'Last_Return_date',
}

@csrf_exempt
def CabinetManage_edit(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceA39/BorrowedDevice"
    mock_data = [
        # {"id": "1", "Customer": "C38", "Plant": "KS",
        #  "NID": "1513", "DevID": "UKB0022B", "IntfCtgry": "USB_A",
        #  "DevCtgry": "keyboard", "Devproperties": "USB1.0", "Devsize": "--",
        #  "DevVendor": "Lenovo", "DevModel": "SK-8815(L)", "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #  "HWVer": "--", "FWVer": "--", "DevDescription": "N/A", "PckgIncludes": "1. 說明書清單",
        #  "expirdate": "一年", "DevPrice": "", "Source": "Lenovo贈送", "Pchsdate": "2018-07-25", "PN": "73P2620",
        #  "LNV_ST": "",
        #  "Purchase_NO": "", "Declaration_NO": "11", "AssetNum": "", "UsYear": "2.7", "addnewname": "代月景",
        #  "addnewdate": "2018-08-01",
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "可借用", "Usrname": "單桂萍",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "2020-01-26", "Overday": ""},
    ]
    IntfCtgryOptions5 = {
        # "USB_A": [{"DevCtgry": "keyboard", "Devproperties": ["www", "qwee", "ewrfe"]},
        #           {"DevCtgry": "Heaphone", "Devproperties": ["2www", "qwee", "ewrfe"]},
        #           {"DevCtgry": "Heaphone", "Devproperties": ["3www", "qwee", "ewrfe"]}],
        # "USB_C&BT": [{"DevCtgry": "Heaphone", "Devproperties": ["ewdfeew", "edeqwe"]}],
        # "USB_Ac": [{"DevCtgry": "Heaphone", "Devproperties": ["2ewdf"]},
        #            {"DevCtgry": "keyboard", "Devproperties": ["www", "qwee", "ewrfe"]},
        #            {"DevCtgry": "Heaphone", "Devproperties": ["www", "qwee", "ewrfe"]}],
        # "USB_Accc": [{"DevCtgry": "Heaphone", "Devproperties": ["23ewfd"]},
        #              {"DevCtgry": "keyboard", "Devproperties": ["www", "qwee", "ewrfe"]}]
    }
    DevVendorOptions5 = {
        # "werfg": ["aa", "bb", "cc"], "werf": ["dd", "ee", "ff"]
    }

    allIntfCtgry = [
        # "USB_A", "USB_B"
    ]
    allDevCtgry = [
        # "USB_A", "USB_B"
    ]
    allDevproperties = [
        # "USB_A", "USB_B"
    ]
    allDevVendor = [
        # "USB_A", "USB_B"
    ]
    allDevsize = [
        # "USB_A", "USB_B"
    ]
    allDevStatus = [
        # "可借用", "已借出"
    ]

    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            # message1 = ('邮件标题1', '邮件标题1测试内容', '416434871@qq.com', ['brotherxd@126.com', 'edwin_cao@compal.com'])
            # message2 = ('邮件标题2', '邮件标题2测试内容', '416434871@qq.com', ['brotherxd@126.com'])
            # messages = (message1, message2)
            # sendmass_email(messages)
            # mock_data
            # res = tasks.ProjectSync.delay()
            # 任务逻辑
            # ProjectSyncview()
            checkAdaPow = {}
            # mock_data
            if checkAdaPow:
                # print(checkAdaPow)
                # mock_datalist = DeviceA39.objects.filter(**checkAdaPow)
                if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                    mock_datalist = DeviceA39.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor'])
                        & Q(Devsize=checkAdaPow['Devsize'])).filter(DevStatus__in=["Good", "Fixed", 'Long'])
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                    mock_datalist = DeviceA39.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor'])).filter(DevStatus__in=["Good", "Fixed", 'Long'])
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                    mock_datalist = DeviceA39.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties'])).filter(DevStatus__in=["Good", "Fixed", 'Long'])
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceA39.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])).filter(DevStatus__in=["Good", "Fixed", 'Long'])
                elif "IntfCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceA39.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry'])).filter(DevStatus__in=["Good", "Fixed", 'Long'])
                else:
                    mock_datalist = DeviceA39.objects.filter(**checkAdaPow).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            else:
                mock_datalist = DeviceA39.objects.all().filter(DevStatus__in=["Good", "Fixed", 'Long'])
            # print(mock_datalist)
            for i in mock_datalist:
                # Photolist = []
                # for h in i.Photo.all():
                #     Photolist.append(
                #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                if i.Plandate and i.Btime and not i.Rtime:
                    if datetime.datetime.now().date() > i.Plandate:
                        Exceed_days = round(
                            float(
                                str((datetime.datetime.now().date() - i.Plandate)).split(' ')[
                                    0]),
                            0)
                    else:
                        Exceed_days = ''
                    if datetime.datetime.now().date() > i.Btime:
                        usedays = round(
                            float(
                                str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                    0]),
                            0)
                    else:
                        usedays = ''
                else:
                    usedays = ''
                    Exceed_days = ''
                Useyears = ''
                if i.Pchsdate:
                    if datetime.datetime.now().date() > i.Pchsdate:
                        Useyears = round(
                            float(
                                str((datetime.datetime.now().date() - i.Pchsdate)).split(' ')[
                                    0])/365,
                            1)
                addnewdate_str = ''
                if i.addnewdate:
                    addnewdate_str = str(i.addnewdate)
                else:
                    addnewdate_str = ''
                Pchsdate_str = ''
                if i.Pchsdate:
                    Pchsdate_str = str(i.Pchsdate)
                else:
                    Pchsdate_str = ''
                Plandate_str = ''
                if i.Plandate:
                    Plandate_str = str(i.Plandate)
                else:
                    Plandate_str = ''
                Btime_str = ''
                if i.Btime:
                    Btime_str = str(i.Btime)
                else:
                    Btime_str = ''
                Rtime_str = ''
                if i.Rtime:
                    Rtime_str = str(i.Rtime)
                else:
                    Rtime_str = ''

                mock_data.append(
                    {"id": i.id, "Customer": i.Customer, "Plant": i.Plant,
                     "NID": i.NID, "DevID": i.DevID, "IntfCtgry": i.IntfCtgry,
                     "DevCtgry": i.DevCtgry, "Devproperties": i.Devproperties, "DevVendor": i.DevVendor,
                     "Devsize": i.Devsize, "DevModel": i.DevModel,
                     "DevName": i.DevName,
                     "HWVer": i.HWVer, "FWVer": i.FWVer, "DevDescription": i.DevDescription,
                     "PckgIncludes": i.PckgIncludes,
                     "expirdate": i.expirdate, "DevPrice": i.DevPrice, "Source": i.Source,
                     "Pchsdate": Pchsdate_str,
                     "PN": i.PN,
                     "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo, "Declaration_NO": i.DeclarationNo,
                     "AssetNum": i.AssetNum, "UsYear": Useyears,
                     "addnewname": i.addnewname, "addnewdate": addnewdate_str,
                     "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                     "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                     "Usrname": i.Usrname, 'Usrnumber': i.BR_per_code,
                     "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str, "Rtime": Rtime_str,
                     "Overday": Exceed_days},
                )
        if 'change5' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties, DevCtgry_P=DevCtgry_P).first()
            for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                DeviceDevsizeListvalue = []
                for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                    DeviceDevsizeListvalue.append(j.Devsize)
                DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
            # print(DevVendorOptions5)
        if 'SEARCH5' in str(request.body):
            checkAdaPow = {}
            IntfCtgry = request.POST.get('IntfCtgry')
            # if IntfCtgry and IntfCtgry != "All":
            #     checkAdaPow['IntfCtgry'] = IntfCtgry
            DevCtgry = request.POST.get('DevCtgry')
            if DevCtgry and DevCtgry != "All":
                checkAdaPow['DevCtgry'] = DevCtgry
            Devproperties = request.POST.get('Devproperties')
            # if Devproperties and Devproperties != "All":
            #     checkAdaPow['Devproperties'] = Devproperties
            DevVendor = request.POST.get('DevVendor')
            if DevVendor and DevVendor != "All":
                checkAdaPow['DevVendor'] = DevVendor
            Devsize = request.POST.get('Devsize')
            if Devsize and Devsize != "All":
                checkAdaPow['Devsize'] = Devsize
            DevStatus = request.POST.get('DevStatus')
            if DevStatus and DevStatus != "All":
                checkAdaPow['BrwStatus'] = DevStatus


            # mock_data
            if IntfCtgry and IntfCtgry != "All" and Devproperties and Devproperties != "All":
                mock_datalist = DeviceA39.objects.filter(
                    Q(IntfCtgry__icontains=IntfCtgry) & Q(Devproperties__icontains=Devproperties)).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            elif IntfCtgry and IntfCtgry != "All" and (not Devproperties or Devproperties == "All"):
                mock_datalist = DeviceA39.objects.filter(
                    Q(IntfCtgry__icontains=IntfCtgry)).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            elif (not IntfCtgry or IntfCtgry == "All") and (Devproperties and Devproperties != "All"):
                mock_datalist = DeviceA39.objects.filter(
                    Q(Devproperties__icontains=Devproperties)).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            else:
                mock_datalist = DeviceA39.objects.all().filter(DevStatus__in=["Good", "Fixed", 'Long'])
            if checkAdaPow:
                # print(checkAdaPow)
                # mock_datalist = DeviceA39.objects.filter(**checkAdaPow)
                mock_datalist = mock_datalist.filter(**checkAdaPow)
            # print(mock_datalist)
            for i in mock_datalist:
                # Photolist = []
                # for h in i.Photo.all():
                #     Photolist.append(
                #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                if i.Plandate and i.Btime and not i.Rtime:
                    if datetime.datetime.now().date() > i.Plandate:
                        Exceed_days = round(
                            float(
                                str((datetime.datetime.now().date() - i.Plandate)).split(' ')[
                                    0]),
                            0)
                    else:
                        Exceed_days = ''
                    if datetime.datetime.now().date() > i.Btime:
                        usedays = round(
                            float(
                                str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                    0]),
                            0)
                    else:
                        usedays = ''
                else:
                    usedays = ''
                    Exceed_days = ''
                Useyears = ''
                if i.Pchsdate:
                    if datetime.datetime.now().date() > i.Pchsdate:
                        Useyears = round(
                            float(
                                str((datetime.datetime.now().date() - i.Pchsdate)).split(' ')[
                                    0]) / 365,
                            1)
                addnewdate_str = ''
                if i.addnewdate:
                    addnewdate_str = str(i.addnewdate)
                else:
                    addnewdate_str = ''
                Pchsdate_str = ''
                if i.Pchsdate:
                    Pchsdate_str = str(i.Pchsdate)
                else:
                    Pchsdate_str = ''
                Plandate_str = ''
                if i.Plandate:
                    Plandate_str = str(i.Plandate)
                else:
                    Plandate_str = ''
                Btime_str = ''
                if i.Btime:
                    Btime_str = str(i.Btime)
                else:
                    Btime_str = ''
                Rtime_str = ''
                if i.Rtime:
                    Rtime_str = str(i.Rtime)
                else:
                    Rtime_str = ''

                mock_data.append(
                    {"id": i.id, "Customer": i.Customer, "Plant": i.Plant,
                     "NID": i.NID, "DevID": i.DevID, "IntfCtgry": i.IntfCtgry,
                     "DevCtgry": i.DevCtgry, "Devproperties": i.Devproperties, "DevVendor": i.DevVendor,
                     "Devsize": i.Devsize, "DevModel": i.DevModel,
                     "DevName": i.DevName,
                     "HWVer": i.HWVer, "FWVer": i.FWVer, "DevDescription": i.DevDescription,
                     "PckgIncludes": i.PckgIncludes,
                     "expirdate": i.expirdate, "DevPrice": i.DevPrice, "Source": i.Source,
                     "Pchsdate": Pchsdate_str,
                     "PN": i.PN,
                     "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo, "Declaration_NO": i.DeclarationNo,
                     "AssetNum": i.AssetNum, "UsYear": Useyears,
                     "addnewname": i.addnewname, "addnewdate": addnewdate_str,
                     "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                     "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                     "Usrname": i.Usrname, 'Usrnumber': i.BR_per_code,
                     "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str, "Rtime": Rtime_str,
                     "Overday": Exceed_days},
                )
        if 'BORROW' in str(request.body):
            # print(1)
            checkAdaPow = {}
            IntfCtgry = request.POST.get('IntfCtgry')
            # if IntfCtgry and IntfCtgry != "All":
            #     checkAdaPow['IntfCtgry'] = IntfCtgry
            DevCtgry = request.POST.get('DevCtgry')
            if DevCtgry and DevCtgry != "All":
                checkAdaPow['DevCtgry'] = DevCtgry
            Devproperties = request.POST.get('Devproperties')
            # if Devproperties and Devproperties != "All":
            #     checkAdaPow['Devproperties'] = Devproperties
            DevVendor = request.POST.get('DevVendor')
            if DevVendor and DevVendor != "All":
                checkAdaPow['DevVendor'] = DevVendor
            Devsize = request.POST.get('Devsize')
            if Devsize and Devsize != "All":
                checkAdaPow['Devsize'] = Devsize
            DevStatus = request.POST.get('DevStatus')
            if DevStatus and DevStatus != "All":
                checkAdaPow['BrwStatus'] = DevStatus

            BorrowedID = request.POST.get('BorrowId')
            # print(BorrowedID, type(BorrowedID))
            # print(json.loads(BorrowedID))
            # print(BorrowedID.split(','))
            updatedic = {'ProjectCode': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                         'BrwStatus': '預定確認中', 'Usrname': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'),
                         'Plandate': request.POST.get('Predict_return'), 'Btime': None, 'Rtime': None, }
            # print(updatedic)
            for i in BorrowedID.split(','):
                # print(i)
                try:
                    with transaction.atomic():
                        # print(updatedic)
                        DeviceA39.objects.filter(id=i).update(**updatedic)
                        alert = 0
                except:
                    # print('2')
                    alert = '此数据%s正被其他使用者编辑中...' % i

            # mock_data
            if IntfCtgry and IntfCtgry != "All" and Devproperties and Devproperties != "All":
                mock_datalist = DeviceA39.objects.filter(
                    Q(IntfCtgry__icontains=IntfCtgry) & Q(Devproperties__icontains=Devproperties)).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            elif IntfCtgry and IntfCtgry != "All" and (not Devproperties or Devproperties == "All"):
                mock_datalist = DeviceA39.objects.filter(
                    Q(IntfCtgry__icontains=IntfCtgry)).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            elif (not IntfCtgry or IntfCtgry == "All") and (Devproperties and Devproperties != "All"):
                mock_datalist = DeviceA39.objects.filter(
                    Q(Devproperties__icontains=Devproperties)).filter(DevStatus__in=["Good", "Fixed", 'Long'])
            else:
                mock_datalist = DeviceA39.objects.all().filter(DevStatus__in=["Good", "Fixed", 'Long'])
            if checkAdaPow:
                # print(checkAdaPow)
                # mock_datalist = DeviceA39.objects.filter(**checkAdaPow)
                mock_datalist = mock_datalist.filter(**checkAdaPow)
            # print(mock_datalist)
            for i in mock_datalist:
                # Photolist = []
                # for h in i.Photo.all():
                #     Photolist.append(
                #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                if i.Plandate and i.Btime and not i.Rtime:
                    if datetime.datetime.now().date() > i.Plandate:
                        Exceed_days = round(
                            float(
                                str((datetime.datetime.now().date() - i.Plandate)).split(' ')[
                                    0]),
                            0)
                    else:
                        Exceed_days = ''
                    if datetime.datetime.now().date() > i.Btime:
                        usedays = round(
                            float(
                                str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                    0]),
                            0)
                    else:
                        usedays = ''
                else:
                    usedays = ''
                    Exceed_days = ''
                Useyears = ''
                if i.Pchsdate:
                    if datetime.datetime.now().date() > i.Pchsdate:
                        Useyears = round(
                            float(
                                str((datetime.datetime.now().date() - i.Pchsdate)).split(' ')[
                                    0]) / 365,
                            1)
                addnewdate_str = ''
                if i.addnewdate:
                    addnewdate_str = str(i.addnewdate)
                else:
                    addnewdate_str = ''
                Pchsdate_str = ''
                if i.Pchsdate:
                    Pchsdate_str = str(i.Pchsdate)
                else:
                    Pchsdate_str = ''
                Plandate_str = ''
                if i.Plandate:
                    Plandate_str = str(i.Plandate)
                else:
                    Plandate_str = ''
                Btime_str = ''
                if i.Btime:
                    Btime_str = str(i.Btime)
                else:
                    Btime_str = ''
                Rtime_str = ''
                if i.Rtime:
                    Rtime_str = str(i.Rtime)
                else:
                    Rtime_str = ''

                mock_data.append(
                    {"id": i.id, "Customer": i.Customer, "Plant": i.Plant,
                     "NID": i.NID, "DevID": i.DevID, "IntfCtgry": i.IntfCtgry,
                     "DevCtgry": i.DevCtgry, "Devproperties": i.Devproperties, "DevVendor": i.DevVendor,
                     "Devsize": i.Devsize, "DevModel": i.DevModel,
                     "DevName": i.DevName,
                     "HWVer": i.HWVer, "FWVer": i.FWVer, "DevDescription": i.DevDescription,
                     "PckgIncludes": i.PckgIncludes,
                     "expirdate": i.expirdate, "DevPrice": i.DevPrice, "Source": i.Source,
                     "Pchsdate": Pchsdate_str,
                     "PN": i.PN,
                     "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo, "Declaration_NO": i.DeclarationNo,
                     "AssetNum": i.AssetNum, "UsYear": Useyears,
                     "addnewname": i.addnewname, "addnewdate": addnewdate_str,
                     "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                     "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                     "Usrname": i.Usrname, 'Usrnumber': i.BR_per_code,
                     "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str, "Rtime": Rtime_str,
                     "Overday": Exceed_days},
                )
        data = {
            "IntfCtgryOptions5": IntfCtgryOptions5,
            "DevVendorOptions5": DevVendorOptions5,
            "content": mock_data,

            "allIntfCtgry": allIntfCtgry,
            "allDevCtgry": allDevCtgry,
            "allDevproperties": allDevproperties,
            "allDevVendor": allDevVendor,
            "allDevsize": allDevsize,
            "allDevStatus": allDevStatus,
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'CabinetManage/CabinetManage.html', locals())




