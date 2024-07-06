from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime, os, json
from django.db.models import Max, Min, Sum, Count, Q
from django.http import JsonResponse
from .models import DeviceIntfCtgryList, DeviceDevCtgryList, DeviceDevpropertiesList, DeviceDevVendorList, \
    DeviceDevsizeList
from service.init_permission import init_permission
from DMS import settings
from django.core.mail import send_mail, send_mass_mail
from django.core.mail import EmailMultiAlternatives
from app01 import tasks
from app01.models import UserInfo
from .models import DeviceABO, DeviceABOHis, PICS, DeviceIntfCtgryList, DeviceDevCtgryList, DeviceDevpropertiesList, \
    DeviceDevVendorList, DeviceDevsizeList

headermodel_Device = {
    '客戶別': 'Customer', '廠區': 'Plant', '設備序號': 'NID',
    # '設備編號': 'DevID',
    '設備用途': 'DevID',
    '介面種類': 'IntfCtgry', '設備種類': 'DevCtgry', '設備屬性': 'Devproperties', '設備廠家': 'DevVendor',
    '設備容量': 'Devsize', '設備型號': 'DevModel', '設備名稱': 'DevName',
    '借還狀態': 'BrwStatus', '用戶名稱': 'Usrname', '預計歸還日期': 'Plandate',
    # '使用天數': 'useday',
    '借用時間': 'Btime', '歸還日期': 'Rtime', '備註': 'Comment',  # "超期天數": "Overday"实时计算出来的

    'HW Ver.': 'HWVer', 'FW Ver.': 'FWVer',
    '設備描述': 'DevDescription', '附帶品': 'PckgIncludes', '保固期': 'expirdate', '價值 RMB(單價)': 'DevPrice',
    '設備來源': 'Source', '購買時間': 'Pchsdate', '料號': 'PN', 'LNV/ABO 設備審核清单': 'LSTA',
    '申購單號': 'ApplicationNo', '報關單號': 'DeclarationNo', '資產編號': 'AssetNum',  # "購買年限": "UsYear"实时计算出来的
    '使用次數': 'uscyc', '借還次數': 'UsrTimes', '設備添加人員': 'addnewname',
    '設備添加日期': 'addnewdate', '設備狀態': 'DevStatus',

    '借還人員工號': 'BR_per_code',
    '機種': 'ProjectCode', 'Phase': 'Phase',
    '上一次借用人員': 'LastUsrname', '上一次借用人員工号': 'Last_BR_per_code', '上一次預計歸還日期': 'Last_Predict_return',
    '上一次借用日期': 'Last_Borrow_date', '上一次歸還日期': 'Last_Return_date',
}


@csrf_exempt
def BorrowedDeviceABO(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/BorrowedDevice"
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
    if DeviceIntfCtgryList.objects.all():
        for i in DeviceIntfCtgryList.objects.all():
            # IntfCtgryOptions.append(i.IntfCtgry)

            DeviceDevCtgryListvalue = []
            DeviceDevCtgryDevpropertiesListvalue = []
            for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                DeviceDevpropertiesListvalue = []
                for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                    DeviceDevpropertiesListvalue.append(k.Devproperties)
                DeviceDevCtgryDevpropertiesListvalue.append(
                    {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

            # IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
            # IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            # IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
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
                # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor'])
                        & Q(Devsize=checkAdaPow['Devsize']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                elif "IntfCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
            else:
                mock_datalist = DeviceABO.objects.all()
            # print(mock_datalist)
            # print("first")
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
                # print(mock_data)
        if 'change5' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                DeviceDevsizeListvalue = []
                for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                    DeviceDevsizeListvalue.append(j.Devsize)
                DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
            # print(DevVendorOptions5)
        if 'SEARCH5' in str(request.body):
            checkAdaPow = {}
            DevCtgry = request.POST.get('DevCtgry')
            if DevCtgry and DevCtgry != "All":
                checkAdaPow['DevCtgry'] = DevCtgry
            DevVendor = request.POST.get('DevVendor')
            if DevVendor and DevVendor != "All":
                checkAdaPow['DevVendor'] = DevVendor
            Devproperties = request.POST.get('Devproperties')
            if Devproperties and Devproperties != "All":
                checkAdaPow['Devproperties'] = Devproperties
            IntfCtgry = request.POST.get('IntfCtgry')
            if IntfCtgry and IntfCtgry != "All":
                checkAdaPow['IntfCtgry'] = IntfCtgry
            Devsize = request.POST.get('Devsize')
            if Devsize and Devsize != "All":
                checkAdaPow['Devsize'] = Devsize

            # mock_data
            if checkAdaPow:
                # print(checkAdaPow)
                # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor'])
                        & Q(Devsize=checkAdaPow['Devsize']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                elif "IntfCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
            else:
                mock_datalist = DeviceABO.objects.all()
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
            DevCtgry = request.POST.get('DevCtgry')
            if DevCtgry and DevCtgry != "All":
                checkAdaPow['DevCtgry'] = DevCtgry
            DevVendor = request.POST.get('DevVendor')
            if DevVendor and DevVendor != "All":
                checkAdaPow['DevVendor'] = DevVendor
            Devproperties = request.POST.get('Devproperties')
            if Devproperties and Devproperties != "All":
                checkAdaPow['Devproperties'] = Devproperties
            IntfCtgry = request.POST.get('IntfCtgry')
            if IntfCtgry and IntfCtgry != "All":
                checkAdaPow['IntfCtgry'] = IntfCtgry
            Devsize = request.POST.get('Devsize')
            if Devsize and Devsize != "All":
                checkAdaPow['Devsize'] = Devsize
            BorrowedID = request.POST.get('BorrowId')
            # print(BorrowedID, type(BorrowedID))
            # print(json.loads(BorrowedID))
            # print(BorrowedID.split(','))
            updatedic = {'ProjectCode': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                         'BrwStatus': '預定確認中', 'Usrname': request.session.get('CNname'),
                         'BR_per_code': request.session.get('account'),
                         'Plandate': request.POST.get('Predict_return'), 'Btime': None, 'Rtime': None, }
            # print(updatedic)
            for i in BorrowedID.split(','):
                # print(i)
                try:
                    with transaction.atomic():
                        # print(updatedic)
                        DeviceABO.objects.filter(id=i).update(**updatedic)
                        alert = 0
                except:
                    # print('2')
                    alert = '此数据%s正被其他使用者编辑中...' % i

            # mock_data
            if checkAdaPow:
                # print(checkAdaPow)
                # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor'])
                        & Q(Devsize=checkAdaPow['Devsize']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                            DevVendor=checkAdaPow['DevVendor']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                        & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                elif "IntfCtgry" in checkAdaPow.keys():
                    mock_datalist = DeviceABO.objects.filter(
                        Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
            else:
                mock_datalist = DeviceABO.objects.all()
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
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/BorrowedDeviceABO.html', locals())


# @csrf_exempt
# def BorrowedPowerCode(request):
#     if not request.session.get('is_login', None):
#         # print(request.session.get('is_login', None))
#         return redirect('/login/')
#     weizhi = "AdapterPowerCode/BorrowedPowerCode"
#     return render(request, 'AdapterPowerCode/BorrowedPowerCode.html', locals())

@csrf_exempt
def R_Borrowed(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/R_Borrowed"
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
    if DeviceIntfCtgryList.objects.all():
        for i in DeviceIntfCtgryList.objects.all():
            # IntfCtgryOptions.append(i.IntfCtgry)

            DeviceDevCtgryListvalue = []
            DeviceDevCtgryDevpropertiesListvalue = []
            for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                DeviceDevpropertiesListvalue = []
                for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                    DeviceDevpropertiesListvalue.append(k.Devproperties)
                DeviceDevCtgryDevpropertiesListvalue.append(
                    {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

            # IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
            # IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            # IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = DeviceABO.objects.filter(Usrname=request.session.get('CNname'),
                                                         BR_per_code=request.session.get('account'), BrwStatus='已借出')
                # if checkAdaPow:
                #     # print(checkAdaPow)
                #     # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                #     if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor'])
                #             & Q(Devsize=checkAdaPow['Devsize']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                #     elif "IntfCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                # else:
                #     mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('isGetData') == 'change5':
                IntfCtgry = request.POST.get('IntfCtgry')
                DevCtgry = request.POST.get('DevCtgry')
                Devproperties = request.POST.get('Devproperties')
                IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
                Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                         DevCtgry_P=DevCtgry_P).first()
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                    DeviceDevsizeListvalue = []
                    for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                        DeviceDevsizeListvalue.append(j.Devsize)
                    DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
                # print(DevVendorOptions5)
            if request.POST.get('isGetData') == 'SEARCH5':
                checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                    'BR_per_code': request.session.get('account'), 'BrwStatus': '已借出'}
                checkAdaPow = {}
                IntfCtgry = request.POST.get('IntfCtgry')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                DevCtgry = request.POST.get('DevCtgry')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                Devproperties = request.POST.get('Devproperties')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                DevVendor = request.POST.get('DevVendor')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devsize = request.POST.get('Devsize')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
            if request.POST.get('isGetData') == 'RENEW':
                RenewId = request.POST.get('RenewId')
                # print(BorrowedID, type(BorrowedID))
                # print(json.loads(BorrowedID))
                # print(BorrowedID.split(','))
                updatedic = {'ProjectCode': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                             'BrwStatus': '續借確認中', 'Usrname': request.session.get('CNname'),
                             'BR_per_code': request.session.get('account'),
                             'Plandate': request.POST.get('Predict_return'), 'Btime': None,
                             'Rtime': None, }
                # print(updatedic)
                for i in RenewId.split(','):
                    # updatedic['Last_BR_per'] = DeviceABO.objects.filter(id=i).first().BR_per
                    # updatedic['Last_Predict_return'] = DeviceABO.objects.filter(id=i).first().Predict_return
                    # updatedic['Last_Borrow_date'] = DeviceABO.objects.filter(id=i).first().Borrow_date
                    # updatedic['Last_Return_date'] = datetime.datetime.now().date()
                    try:
                        with transaction.atomic():
                            DeviceABO.objects.filter(id=i).update(**updatedic)
                            alert = 0
                    except:
                        alert = '此数据%s正被其他使用者编辑中...' % i

                # mock_data
                checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                    'BR_per_code': request.session.get('account'), 'BrwStatus': '已借出'}
                checkAdaPow = {}
                IntfCtgry = request.POST.get('IntfCtgry')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                DevCtgry = request.POST.get('DevCtgry')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                Devproperties = request.POST.get('Devproperties')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                DevVendor = request.POST.get('DevVendor')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devsize = request.POST.get('Devsize')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'Returning' in str(request.body):

                    responseData = json.loads(request.body)

                    updatedic = {'BrwStatus': '歸還確認中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 "Last_uscyc": responseData['USE_NUM']
                                 }
                    for i in responseData['ReturnId']:
                        try:
                            with transaction.atomic():
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    checkAdaPow = {'Usrname': request.session.get('CNname'),
                                   'BR_per_code': request.session.get('account'), 'BrwStatus': '已借出'}
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devproperties = responseData['Devproperties']
                    if Devproperties and Devproperties != "All":
                        checkAdaPow['Devproperties'] = Devproperties
                    IntfCtgry = responseData['IntfCtgry']
                    if IntfCtgry and IntfCtgry != "All":
                        checkAdaPow['IntfCtgry'] = IntfCtgry
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize

                    # mock_data
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                        else:
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = DeviceABO.objects.all()
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
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/R_Borrowed.html', locals())


@csrf_exempt
def R_Return(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/R_Return"
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
    if DeviceIntfCtgryList.objects.all():
        for i in DeviceIntfCtgryList.objects.all():
            # IntfCtgryOptions.append(i.IntfCtgry)

            DeviceDevCtgryListvalue = []
            DeviceDevCtgryDevpropertiesListvalue = []
            for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                DeviceDevpropertiesListvalue = []
                for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                    DeviceDevpropertiesListvalue.append(k.Devproperties)
                DeviceDevCtgryDevpropertiesListvalue.append(
                    {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

            # IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
            # IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            # IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = DeviceABO.objects.filter(Usrname=request.session.get('CNname'),
                                                         BR_per_code=request.session.get('account'), BrwStatus='歸還確認中')
                # mock_data
                # if checkAdaPow:
                #     # print(checkAdaPow)
                #     # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                #     if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor'])
                #             & Q(Devsize=checkAdaPow['Devsize']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                #     elif "IntfCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                # else:
                #     mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('isGetData') == 'change5':
                IntfCtgry = request.POST.get('IntfCtgry')
                DevCtgry = request.POST.get('DevCtgry')
                Devproperties = request.POST.get('Devproperties')
                IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
                Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                         DevCtgry_P=DevCtgry_P).first()
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                    DeviceDevsizeListvalue = []
                    for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                        DeviceDevsizeListvalue.append(j.Devsize)
                    DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
                # print(DevVendorOptions5)
            if request.POST.get('isGetData') == 'SEARCH5':
                checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                    'BR_per_code': request.session.get('account'), 'BrwStatus': '歸還確認中'}
                checkAdaPow = {}
                IntfCtgry = request.POST.get('IntfCtgry')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                DevCtgry = request.POST.get('DevCtgry')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                Devproperties = request.POST.get('Devproperties')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                DevVendor = request.POST.get('DevVendor')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devsize = request.POST.get('Devsize')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'CancelReturn' in str(request.body):

                    responseData = json.loads(request.body)
                    updatedic = {'BrwStatus': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['ReturnId']:
                        try:
                            with transaction.atomic():
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                        'BR_per_code': request.session.get('account'), 'BrwStatus': '歸還確認中'}
                    checkAdaPow = {}
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devproperties = responseData['Devproperties']
                    if Devproperties and Devproperties != "All":
                        checkAdaPow['Devproperties'] = Devproperties
                    IntfCtgry = responseData['IntfCtgry']
                    if IntfCtgry and IntfCtgry != "All":
                        checkAdaPow['IntfCtgry'] = IntfCtgry
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize

                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/R_Return.html', locals())


@csrf_exempt
def R_Keep(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/R_Keep"
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
    if DeviceIntfCtgryList.objects.all():
        for i in DeviceIntfCtgryList.objects.all():
            # IntfCtgryOptions.append(i.IntfCtgry)

            DeviceDevCtgryListvalue = []
            DeviceDevCtgryDevpropertiesListvalue = []
            for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                DeviceDevpropertiesListvalue = []
                for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                    DeviceDevpropertiesListvalue.append(k.Devproperties)
                DeviceDevCtgryDevpropertiesListvalue.append(
                    {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

            # IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
            # IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            # IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = DeviceABO.objects.filter(Usrname=request.session.get('CNname'),
                                                         BR_per_code=request.session.get('account'), BrwStatus='續借確認中')
                # mock_data
                # if checkAdaPow:
                #     # print(checkAdaPow)
                #     # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                #     if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor'])
                #             & Q(Devsize=checkAdaPow['Devsize']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                #     elif "IntfCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                # else:
                #     mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('isGetData') == 'change5':
                IntfCtgry = request.POST.get('IntfCtgry')
                DevCtgry = request.POST.get('DevCtgry')
                Devproperties = request.POST.get('Devproperties')
                IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
                Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                         DevCtgry_P=DevCtgry_P).first()
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                    DeviceDevsizeListvalue = []
                    for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                        DeviceDevsizeListvalue.append(j.Devsize)
                    DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
                # print(DevVendorOptions5)
            if request.POST.get('isGetData') == 'SEARCH5':
                checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                    'BR_per_code': request.session.get('account'), 'BrwStatus': '續借確認中'}
                checkAdaPow = {}
                IntfCtgry = request.POST.get('IntfCtgry')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                DevCtgry = request.POST.get('DevCtgry')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                Devproperties = request.POST.get('Devproperties')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                DevVendor = request.POST.get('DevVendor')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devsize = request.POST.get('Devsize')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'CancelRenew' in str(request.body):

                    responseData = json.loads(request.body)

                    updatedic = {'BrwStatus': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['Renew']:
                        updatedic['Usrname'] = DeviceABO.objects.filter(id=i).first().Last_BR_per
                        updatedic['BR_per_code'] = DeviceABO.objects.filter(id=i).first().Last_BR_per_code
                        updatedic['ProjectCode'] = DeviceABO.objects.filter(id=i).first().Last_ProjectCode
                        updatedic['Phase'] = DeviceABO.objects.filter(id=i).first().Last_Phase
                        updatedic['Plandate'] = DeviceABO.objects.filter(id=i).first().Last_Predict_return
                        updatedic['Btime'] = DeviceABO.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Rtime'] = DeviceABO.objects.filter(id=i).first().Last_Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                        'BR_per_code': request.session.get('account'), 'BrwStatus': '續借確認中'}
                    checkAdaPow = {}
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devproperties = responseData['Devproperties']
                    if Devproperties and Devproperties != "All":
                        checkAdaPow['Devproperties'] = Devproperties
                    IntfCtgry = responseData['IntfCtgry']
                    if IntfCtgry and IntfCtgry != "All":
                        checkAdaPow['IntfCtgry'] = IntfCtgry
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize

                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/R_Keep.html', locals())


@csrf_exempt
def R_Destine(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/R_Destine"
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
    if DeviceIntfCtgryList.objects.all():
        for i in DeviceIntfCtgryList.objects.all():
            # IntfCtgryOptions.append(i.IntfCtgry)

            DeviceDevCtgryListvalue = []
            DeviceDevCtgryDevpropertiesListvalue = []
            for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                DeviceDevpropertiesListvalue = []
                for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                    DeviceDevpropertiesListvalue.append(k.Devproperties)
                DeviceDevCtgryDevpropertiesListvalue.append(
                    {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

            # IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
            # IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            # IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
            IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

    if request.method == "POST":
        if request.POST:
            # print(request.body)
            if 'first' in str(request.body):
                # mock_data
                mock_datalist = DeviceABO.objects.filter(Usrname=request.session.get('CNname'),
                                                         BR_per_code=request.session.get('account'), BrwStatus='預定確認中')
                # if checkAdaPow:
                #     # print(checkAdaPow)
                #     # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                #     if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor'])
                #             & Q(Devsize=checkAdaPow['Devsize']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                #     elif "IntfCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceABO.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                # else:
                #     mock_datalist = DeviceABO.objects.all()
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
            if 'change5' in str(request.body):
                IntfCtgry = request.POST.get('IntfCtgry')
                DevCtgry = request.POST.get('DevCtgry')
                Devproperties = request.POST.get('Devproperties')
                IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
                Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                         DevCtgry_P=DevCtgry_P).first()
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                    DeviceDevsizeListvalue = []
                    for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                        DeviceDevsizeListvalue.append(j.Devsize)
                    DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
                # print(DevVendorOptions5)
            if 'SEARCH' in str(request.body):
                checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                    'BR_per_code': request.session.get('account'), 'BrwStatus': '預定確認中'}
                checkAdaPow = {}
                DevCtgry = request.POST.get('DevCtgry')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                DevVendor = request.POST.get('DevVendor')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devproperties = request.POST.get('Devproperties')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                IntfCtgry = request.POST.get('IntfCtgry')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                Devsize = request.POST.get('Devsize')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'CancelBook' in str(request.body):
                    # print(request.body)
                    responseData = json.loads(request.body)
                    # print(responseData)

                    updatedic = {'BrwStatus': '可借用',
                                 # 'BR_per': request.session.get('CNname'),
                                 'Plandate': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['BookId']:
                        # print(i)
                        updatedic['Usrname'] = DeviceABO.objects.filter(id=i).first().Last_BR_per
                        updatedic['BR_per_code'] = DeviceABO.objects.filter(id=i).first().Last_BR_per_code
                        updatedic['ProjectCode'] = DeviceABO.objects.filter(id=i).first().Last_ProjectCode
                        updatedic['Phase'] = DeviceABO.objects.filter(id=i).first().Last_Phase
                        # updatedic['Predict_return'] = DeviceABO.objects.filter(id=i).first().Last_Predict_return
                        updatedic['Btime'] = DeviceABO.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Rtime'] = DeviceABO.objects.filter(id=i).first().Last_Return_date
                        # print(updatedic)
                        try:
                            with transaction.atomic():
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    checkAdaPowfirst = {'Usrname': request.session.get('CNname'),
                                        'BR_per_code': request.session.get('account'), 'BrwStatus': '預定確認中'}
                    checkAdaPow = {}
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devproperties = responseData['Devproperties']
                    if Devproperties and Devproperties != "All":
                        checkAdaPow['Devproperties'] = Devproperties
                    IntfCtgry = responseData['IntfCtgry']
                    if IntfCtgry and IntfCtgry != "All":
                        checkAdaPow['IntfCtgry'] = IntfCtgry
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize

                    # mock_data
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst).filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPowfirst)
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
            # print(request.POST)

        data = {
            "IntfCtgryOptions5": IntfCtgryOptions5,
            "DevVendorOptions5": DevVendorOptions5,
            "content": mock_data,
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/R_Destine.html', locals())


@csrf_exempt
def M_Borrow(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/M_Borrow"
    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "11111111"}, {"value": " 錢剛", "number": "33445566"},
    ]
    for i in DeviceABO.objects.filter(BrwStatus='預定確認中').values('Usrname', 'BR_per_code').distinct().order_by(
            'BR_per_code'):
        selectItem.append({"value": i['Usrname'], "number": i["BR_per_code"]})
        # print(i)
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
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = DeviceABO.objects.filter(BrwStatus='預定確認中')
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
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BrwStatus': '預定確認中'}
                if request.POST.get('Borrower'):
                    checkAdaPow['Usrname'] = request.POST.get('Borrower')
                    if request.POST.get('BorrowerNum', None):
                        checkAdaPow['BR_per_code'] = request.POST.get('BorrowerNum')
                # Changjiasearch = request.POST.get('Changjia')
                # if Changjiasearch and Changjiasearch != "All":
                #     checkAdaPow['Changjia'] = Changjiasearch
                # Customerserach = request.POST.get('Customer')
                # if Customerserach and Customerserach != "All":
                #     checkAdaPow['Customer'] = Customerserach
                # PNsearch = request.POST.get('PN')
                # if PNsearch and PNsearch != "All":
                #     checkAdaPow['MaterialPN'] = PNsearch
                # Powersearch = request.POST.get('Power')
                # if Powersearch and Powersearch != "All":
                #     checkAdaPow['Power'] = Powersearch

                # mock_data
                # print(checkAdaPow)
                if checkAdaPow:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceABO.objects.all()
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'ChangeDelivery' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BrwStatus': '預定確認中'}
                    if responseData['Borrower']:
                        checkAdaPow['Usrname'] = responseData['Borrower']
                    if "BorrowerNum" in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['BorrowerNum']

                    updatedic = {'BrwStatus': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }
                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)
                        updatedic['Last_BR_per'] = DeviceABO.objects.filter(id=i).first().Usrname
                        updatedic['Last_BR_per_code'] = DeviceABO.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_ProjectCode'] = DeviceABO.objects.filter(id=i).first().ProjectCode
                        updatedic['Last_Phase'] = DeviceABO.objects.filter(id=i).first().Phase
                        updatedic['Last_Predict_return'] = DeviceABO.objects.filter(id=i).first().Plandate
                        updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = DeviceABO.objects.filter(id=i).first().Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = DeviceABO.objects.all()
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
            # "selectItem": selectItem,
            "content": mock_data,
            "select": selectItem,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/M_Borrow.html', locals())


@csrf_exempt
def M_Return(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/R_Destine"
    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "11111111"},
        # {"value": " 錢剛", "number": "33445566"},
    ]
    for i in DeviceABO.objects.filter(BrwStatus='歸還確認中').values('Usrname', 'BR_per_code').distinct().order_by(
            'BR_per_code'):
        selectItem.append({"value": i['Usrname'], 'number': i['BR_per_code']})
    mock_data = [
        # {"id": "2", "Customer": "C38", "Plant": "KS",
        #  "NID": "1514", "DevID": "UKB0022B", "IntfCtgry": "USB_A",
        #  "DevCtgry": "keyboard", "Devproperties": "USB1.0", "Devsize": "--",
        #  "DevVendor": "Lenovo", "DevModel": "SK-8815(L)", "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #  "HWVer": "", "FWVer": "", "DevDescription": "N/A", "PckgIncludes": "1. 說明書",
        #  "expirdate": "一年", "DevPrice": "", "Source": "Lenovo贈送", "Pchsdate": "", "PN": "73P2620",
        #  "LNV_ST": "", "Purchase_NO": "", "Declaration_NO": "12", "AssetNum": "", "UsYear": "2.7",
        #  "addnewname": "代月景", "addnewdate": "2018-08-01",
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "預定確認中", "Usrname": "單桂萍",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "", "Overday": ""},
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                # mock_data
                checkAdaPow = {'BrwStatus': '歸還確認中'}
                if checkAdaPow:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BrwStatus': '歸還確認中'}
                if request.POST.get('Borrower'):
                    checkAdaPow['Usrname'] = request.POST.get('Borrower')
                if request.POST.get('BorrowerNum', None):
                    checkAdaPow['BR_per_code'] = request.POST.get('BorrowerNum')

                # mock_data
                if checkAdaPow:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceABO.objects.all()
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'ChangeStorages' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BrwStatus': '歸還確認中'}
                    if responseData['Borrower']:
                        checkAdaPow['Usrname'] = responseData['Borrower']
                    if 'BorrowerNum' in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['BorrowerNum']

                    updatedic = {'BrwStatus': '可借用',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': datetime.datetime.now().date(),
                                 'Rtime': datetime.datetime.now().date(),
                                 "Last_uscyc": '',
                                 }

                    for i in responseData['params']:
                        # updatedic['Last_BR_per'] = DeviceABO.objects.filter(id=i).first().BR_per
                        # updatedic['Last_Predict_return'] = DeviceABO.objects.filter(id=i).first().Predict_return
                        # updatedic['Last_Borrow_date'] = datetime.datetime.now().date(),
                        updatedic['Last_Return_date'] = datetime.datetime.now().date()
                        updatedic['uscyc'] = str(int(DeviceABO.objects.filter(id=i).first().uscyc) + int(
                            DeviceABO.objects.filter(id=i).first().Last_uscyc))
                        updatedic['UsrTimes'] = str(int(DeviceABO.objects.filter(id=i).first().UsrTimes) + 1)

                        Devicebyid = DeviceABO.objects.filter(id=i).first()
                        updatedic_His = {
                            "NID": Devicebyid.NID, "DevID": Devicebyid.DevID,
                            "DevModel": Devicebyid.DevModel, "DevName": Devicebyid.DevName,
                            "uscyc": DeviceABO.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date, "Plandate": Devicebyid.Last_Predict_return,
                            "Rtime": datetime.datetime.now().date(),
                            "Usrname": Devicebyid.Last_BR_per, "BR_per_code": Devicebyid.Last_BR_per_code,
                            "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }
                        updatedic_His_check = {
                            "NID": Devicebyid.NID, "DevID": Devicebyid.DevID,
                            "DevModel": Devicebyid.DevModel, "DevName": Devicebyid.DevName,
                            # "uscyc": DeviceABO.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date, "Plandate": Devicebyid.Last_Predict_return,
                            # "Rtime": datetime.datetime.now().date(),#重新操作時，時間不一樣，不能以操作當下的時間作爲檢查條件
                            "Usrname": Devicebyid.Last_BR_per, "BR_per_code": Devicebyid.Last_BR_per_code,
                            "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }
                        try:
                            with transaction.atomic():
                                if DeviceABOHis.objects.filter(**updatedic_His_check):
                                    pass  # 防止历史记录存成功了，Device更新失败，需要重复操作。
                                else:
                                    DeviceABOHis.objects.create(**updatedic_His)
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = DeviceABO.objects.all()
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
                             "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo,
                             "Declaration_NO": i.DeclarationNo,
                             "AssetNum": i.AssetNum, "UsYear": Useyears,
                             "addnewname": i.addnewname, "addnewdate": addnewdate_str,
                             "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                             "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                             "Usrname": i.Usrname, 'Usrnumber': i.BR_per_code,
                             "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str,
                             "Rtime": Rtime_str,
                             "Overday": Exceed_days},
                        )
        data = {
            "select": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/M_Return.html', locals())


@csrf_exempt
def M_Keep(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/M_Keep"

    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "11111111"},
        # {"value": " 錢剛", "number": "33445566"},
    ]
    for i in DeviceABO.objects.filter(BrwStatus='續借確認中').values('Usrname', 'BR_per_code').distinct().order_by(
            'BR_per_code'):
        selectItem.append({"value": i['Usrname'], 'number': i['BR_per_code']})
    mock_data = [
        # {"id": "2", "Customer": "C38", "Plant": "KS",
        #  "NID": "1514", "DevID": "UKB0022B", "IntfCtgry": "USB_A",
        #  "DevCtgry": "keyboard", "Devproperties": "USB1.0", "Devsize": "--",
        #  "DevVendor": "Lenovo", "DevModel": "SK-8815(L)", "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #  "HWVer": "", "FWVer": "", "DevDescription": "N/A", "PckgIncludes": "1. 說明書",
        #  "expirdate": "一年", "DevPrice": "", "Source": "Lenovo贈送", "Pchsdate": "", "PN": "73P2620",
        #  "LNV_ST": "", "Purchase_NO": "", "Declaration_NO": "12", "AssetNum": "", "UsYear": "2.7",
        #  "addnewname": "代月景", "addnewdate": "2018-08-01",
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "預定確認中", "Usrname": "單桂萍",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "", "Overday": ""},
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '續借確認中'}
                if checkAdaPow:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BrwStatus': '續借確認中'}
                if request.POST.get('Borrower'):
                    checkAdaPow['Usrname'] = request.POST.get('Borrower')
                if request.POST.get('BorrowerNum', None):
                    checkAdaPow['BR_per_code'] = request.POST.get('BorrowerNum')

                # mock_data
                if checkAdaPow:
                    mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceABO.objects.all()
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
        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'EnsureRenew' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BrwStatus': '續借確認中'}
                    if responseData['Borrower']:
                        checkAdaPow['Usrname'] = responseData['Borrower']
                    if 'BorrowerNum' in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['BorrowerNum']

                    updatedic = {'BrwStatus': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }

                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)

                        updatedic['Last_BR_per'] = DeviceABO.objects.filter(id=i).first().Usrname
                        updatedic['Last_BR_per_code'] = DeviceABO.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_Predict_return'] = DeviceABO.objects.filter(id=i).first().Plandate
                        updatedic['Last_ProjectCode'] = DeviceABO.objects.filter(id=i).first().ProjectCode
                        updatedic['Last_Phase'] = DeviceABO.objects.filter(id=i).first().Phase
                        # updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = DeviceABO.objects.filter(id=i).first().Return_date

                        Devicebyid = DeviceABO.objects.filter(id=i).first()
                        updatedic_His = {
                            "NID": Devicebyid.NID, "DevID": Devicebyid.DevID,
                            "DevModel": Devicebyid.DevModel, "DevName": Devicebyid.DevName,
                            # "uscyc": DeviceABO.objects.filter(id=i).first().uscyc,
                            "Btime": Devicebyid.Last_Borrow_date, "Plandate": Devicebyid.Last_Predict_return,
                            # "Rtime": Devicebyid.Last_Return_date #续借没有还，所以没有归还时间
                            "Rtime": datetime.datetime.now().date(),
                            "Usrname": Devicebyid.Last_BR_per, "BR_per_code": Devicebyid.Last_BR_per_code,
                            "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            "Devstatus": "續借中",
                            # "Result": '',
                            # "Comments": '',
                        }
                        updatedic_His_check = {
                            "NID": Devicebyid.NID, "DevID": Devicebyid.DevID,
                            "DevModel": Devicebyid.DevModel, "DevName": Devicebyid.DevName,
                            # "uscyc": DeviceLNV.objects.filter(id=i).first().uscyc,
                            "Btime": Devicebyid.Last_Borrow_date, "Plandate": Devicebyid.Last_Predict_return,
                            # "Rtime": datetime.datetime.now().date(),#重新操作時，時間不一樣，不能以操作當下的時間作爲檢查條件
                            "Usrname": Devicebyid.Last_BR_per, "BR_per_code": Devicebyid.Last_BR_per_code,
                            "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            "Devstatus": "續借中",
                            # "Result": '',
                            # "Comments": '',
                        }
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                # print(updatedic_His)
                                if DeviceABOHis.objects.filter(**updatedic_His_check):
                                    pass  # 防止历史记录存成功了，Device更新失败，需要重复操作。
                                else:
                                    DeviceABOHis.objects.create(**updatedic_His)
                                DeviceABO.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = DeviceABO.objects.all()
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
            "select": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/M_Keep.html', locals())


@csrf_exempt
def M_Category(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/M_upload"
    errormessae = """"""
    IntfCtgryOptions = [
        # "USB_A", "USB_C&BT", "USB_Ac", "USB_Accc"
    ]
    IntfCtgryTable = [
        # {"id": 1, "IntfCtgry": "AdapterAndPowercode-LNV"},
        # {"id": 2, "IntfCtgry": "Device-LNV"},
        # {"id": 3, "IntfCtgry": "Device-ABO"},
    ]

    IntfCtgryOptions2 = {
        # "USB_A": [{"DevCtgry": "keyboard"}, {"DevCtgry": "Heaphone"}, {"DevCtgry": "Heaphone"}],
        # "USB_C&BT": [{"DevCtgry": "Heaphone"}],
        # "USB_Ac": [{"DevCtgry": "Heaphone"}, {"DevCtgry": "keyboard"}, {"DevCtgry": "Heaphone"}],
        # "USB_Accc": [{"DevCtgry": "Heaphone"}, {"DevCtgry": "keyboard"}]
    }
    DevCtgryTable = [
        # {"id": 4, "IntfCtgry": "AdapterAndPowercode-LNV", "DevCtgry": "https://www.baidu.com/"},
        # {"id": 5, "IntfCtgry": "Device-LNV", "DevCtgry": "https://www.tmall.com/"},
        # {"id": 6, "IntfCtgry": "Device-ABO", "DevCtgry": "https://www.taobao.com/"}
    ]

    IntfCtgryOptions3 = {
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
    DevpropertiesTable = [
        # {"id": 7, "IntfCtgry": "AdapterAndPowercode-LNV", "DevCtgry": "https://www.baidu.com/",
        #                    "Devproperties": "KS-Plant5"},
        #                   {"id": 8, "IntfCtgry": "Device-LNV", "DevCtgry": "https://www.tmall.com/",
        #                    "Devproperties": "KS-Plant5"},
        #                   {"id": 9, "IntfCtgry": "Device-ABO", "DevCtgry": "https://www.taobao.com/",
        #                    "Devproperties": "CQ"}
    ]
    IntfCtgryOptions4 = {
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
    DevVendorOptions4 = [
        # "wertfe", "tgfrt", "vhuikjh"
    ]
    DevVendorTable = [
        # {"id": 10, "IntfCtgry": "AdapterAndPowercode-LNV", "DevCtgry": "https://www.baidu.com/",
        #                "Devproperties": "KS-Plant5", "DevVendor": "王君"},
        #               {"id": 11, "IntfCtgry": "Device-LNV", "DevCtgry": "https://www.tmall.com/",
        #                "Devproperties": "KS-Plant5", "DevVendor": "曹泽"},
        #               {"id": 12, "IntfCtgry": "Device-ABO", "DevCtgry": "https://www.taobao.com/",
        #                "Devproperties": "CQ", "DevVendor": "孙俊清"}
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
    DevsizeTable = [
        # {"id": 13, "IntfCtgry": "AdapterAndPowercode-LNV", "DevCtgry": "https://www.baidu.com/",
        #              "Devproperties": "KS-Plant5", "DevVendor": "王君",
        #              "Devsize": ""},
        #             {"id": 14, "IntfCtgry": "Device-LNV", "DevCtgry": "https://www.tmall.com/",
        #              "Devproperties": "KS-Plant5", "DevVendor": "曹泽", "Devsize": ""},
        #             {"id": 15, "IntfCtgry": "Device-ABO", "DevCtgry": "https://www.taobao.com/", "Devproperties": "CQ",
        #              "DevVendor": "孙俊清", "Devsize": ""}
    ]

    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if 'first' in str(request.body):
            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

        if 'change4' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            # print(IntfCtgry_P, type(IntfCtgry_P))
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                DevVendorOptions4.append(i.DevVendor)
        if 'change5' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devproperties_P):
                DeviceDevsizeListvalue = []
                for j in DeviceDevsizeList.objects.filter(DevVendor_P=i):
                    DeviceDevsizeListvalue.append(j.Devsize)
                DevVendorOptions5[i.DevVendor] = DeviceDevsizeListvalue
            # print(DevVendorOptions5)
        if 'SEARCH1' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DeviceIntfCtgrycheck = {}
            if IntfCtgry:
                DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
            if DeviceIntfCtgrycheck:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
            else:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
            for i in DeviceIntfCtgrycheckresult:
                IntfCtgryTable.append({"id": i.id, "IntfCtgry": i.IntfCtgry})
        if 'editSubmit1' in str(request.body):
            responseData = json.loads(request.body)
            editID = responseData['editID']
            NewIntfCtgry = responseData['IntfCtgry']
            IntfCtgryUpdatedic = {'IntfCtgry': NewIntfCtgry}
            if DeviceIntfCtgryList.objects.filter(IntfCtgry=NewIntfCtgry):
                errormessae = """IntfCtgry:%s 已经存在 """ % NewIntfCtgry
                print(errormessae)
            else:
                DeviceIntfCtgryList.objects.filter(id=editID).update(**IntfCtgryUpdatedic)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                DeviceIntfCtgrycheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    IntfCtgryTable.append({"id": i.id, "IntfCtgry": i.IntfCtgry})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'addSubmit1' in str(request.body):
            responseData = json.loads(request.body)
            IntfCtgry = responseData['IntfCtgry']
            if DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry):
                errormessae = """IntfCtgry:%s 已经存在 """ % IntfCtgry
                print(errormessae)
            else:
                DeviceIntfCtgryList.objects.create(IntfCtgry=IntfCtgry)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                DeviceIntfCtgrycheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    IntfCtgryTable.append({"id": i.id, "IntfCtgry": i.IntfCtgry})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'Delete1' in str(request.body):
            responseData = json.loads(request.body)
            DeleteId = responseData['DeleteId']
            # print(DeleteId)
            errormessae = """"""
            for i in DeleteId:
                try:
                    DeviceIntfCtgryList.objects.filter(id=i).delete()
                except:
                    errormessae += """IntfCtgry:%s 有下层关联数据<br/>""" % DeviceIntfCtgryList.objects.filter(
                        id=i).first().IntfCtgry
                    print(errormessae)
                    print(i)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                DeviceIntfCtgrycheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    IntfCtgryTable.append({"id": i.id, "IntfCtgry": i.IntfCtgry})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

        if 'SEARCH2' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            DeviceIntfCtgrycheck = {}
            DeviceDevCtgrycheck = {}
            if IntfCtgry:
                DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
            if DeviceIntfCtgrycheck:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
            else:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
            for i in DeviceIntfCtgrycheckresult:
                if DevCtgry:
                    DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                DeviceDevCtgrycheck['IntfCtgry_P'] = i
                if DeviceDevCtgrycheck:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                else:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                for j in DeviceDevCtgrycheckresult:
                    DevCtgryTable.append({"id": j.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry})
        if 'editSubmit2' in str(request.body):
            responseData = json.loads(request.body)
            editID = responseData['editID']
            NewIntfCtgry = responseData['IntfCtgry']
            NewDevCtgry = responseData['DevCtgry']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=NewIntfCtgry).first()
            NewDevCtgryUpdatedic = {'DevCtgry': NewDevCtgry, "IntfCtgry_P": IntfCtgry_P}
            if DeviceDevCtgryList.objects.filter(**NewDevCtgryUpdatedic):
                errormessae = """IntfCtgry:%s>DevCtgry:%s 已经存在 """ % (NewIntfCtgry, NewDevCtgry)
                print(errormessae)
            else:
                DeviceDevCtgryList.objects.filter(id=editID).update(**NewDevCtgryUpdatedic)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']

                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        DevCtgryTable.append({"id": j.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'addSubmit2' in str(request.body):
            responseData = json.loads(request.body)
            IntfCtgry = responseData['IntfCtgry']
            DevCtgry = responseData['DevCtgry']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            if DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P):
                errormessae = """IntfCtgry:%s>DevCtgry:%s 已经存在 """ % (IntfCtgry, DevCtgry)
                print(errormessae)
            else:
                # print(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first(),type(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()))
                DeviceDevCtgryList.objects.create(DevCtgry=DevCtgry, IntfCtgry_P=DeviceIntfCtgryList.objects.filter(
                    IntfCtgry=IntfCtgry).first())

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']

                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        DevCtgryTable.append({"id": j.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'Delete2' in str(request.body):
            responseData = json.loads(request.body)
            DeleteId = responseData['DeleteId']
            # print(DeleteId)
            IntfCtgry = responseData['IntfCtgry_search']
            errormessae = """"""
            for i in DeleteId:
                try:
                    DeviceDevCtgryList.objects.filter(id=i).delete()
                except:
                    errormessae += """IntfCtgry:%s>DevCtgry:%s 有下层关联数据<br/>""" % (
                    IntfCtgry, DeviceDevCtgryList.objects.filter(id=i).first().DevCtgry)
                    print(errormessae)
                    print(i)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']

                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        DevCtgryTable.append({"id": j.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

        if 'SEARCH3' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            DeviceIntfCtgrycheck = {}
            DeviceDevCtgrycheck = {}
            DeviceDevpropertiescheck = {}
            if IntfCtgry:
                DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
            if DeviceIntfCtgrycheck:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
            else:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
            for i in DeviceIntfCtgrycheckresult:
                if DevCtgry:
                    DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                DeviceDevCtgrycheck['IntfCtgry_P'] = i
                if DeviceDevCtgrycheck:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                else:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                for j in DeviceDevCtgrycheckresult:
                    if Devproperties:
                        DeviceDevpropertiescheck['Devproperties'] = Devproperties
                    DeviceDevpropertiescheck['DevCtgry_P'] = j
                    # print(DeviceDevpropertiescheck)
                    if DeviceDevpropertiescheck:
                        DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                            **DeviceDevpropertiescheck)
                    else:
                        DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                    for k in DeviceDevpropertiescheckresult:
                        DevpropertiesTable.append({"id": k.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                   "Devproperties": k.Devproperties})
        if 'editSubmit3' in str(request.body):
            responseData = json.loads(request.body)
            editID = responseData['editID']
            NewIntfCtgry = responseData['IntfCtgry']
            NewDevCtgry = responseData['DevCtgry']
            NewDevproperties = responseData['Devproperties']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=NewIntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=NewDevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            NewDevpropertiesUpdatedic = {'Devproperties': NewDevproperties, "DevCtgry_P": DevCtgry_P}
            if DeviceDevpropertiesList.objects.filter(**NewDevpropertiesUpdatedic):
                errormessae = """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s 已经存在 """ % (
                NewIntfCtgry, NewDevCtgry, NewDevproperties)
                print(errormessae)
            else:
                DeviceDevpropertiesList.objects.filter(id=editID).update(**NewDevpropertiesUpdatedic)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            DevpropertiesTable.append({"id": k.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                       "Devproperties": k.Devproperties})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'addSubmit3' in str(request.body):
            responseData = json.loads(request.body)
            IntfCtgry = responseData['IntfCtgry']
            DevCtgry = responseData['DevCtgry']
            Devproperties = responseData['Devproperties']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first().id
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first().id
            if DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties, DevCtgry_P=DevCtgry_P):
                errormessae = """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s 已经存在 """ % (
                IntfCtgry, DevCtgry, Devproperties)
                print(errormessae)
            else:
                # print(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first(),type(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()))
                DeviceDevpropertiesList.objects.create(Devproperties=Devproperties,
                                                       DevCtgry_P=DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry,
                                                                                                    IntfCtgry_P=IntfCtgry_P).first())

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        # print(IntfCtgry,DevCtgry,Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            DevpropertiesTable.append({"id": k.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                       "Devproperties": k.Devproperties})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'Delete3' in str(request.body):
            responseData = json.loads(request.body)
            DeleteId = responseData['DeleteId']
            # print(DeleteId)
            IntfCtgry = responseData['IntfCtgry_search']
            DevCtgry = responseData['DevCtgry_search']
            errormessae = """"""
            # print(DeleteId)
            for i in DeleteId:
                try:
                    DeviceDevpropertiesList.objects.filter(id=i).delete()
                except:
                    errormessae += """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s 有下层关联数据<br/>""" % (
                    IntfCtgry, DeviceDevpropertiesList.objects.filter(id=i).first().DevCtgry_P.DevCtgry,
                    DeviceDevpropertiesList.objects.filter(id=i).first().Devproperties)
                    print(errormessae)
                    print(i)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            DevpropertiesTable.append({"id": k.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                       "Devproperties": k.Devproperties})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

        if 'SEARCH4' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            DevVendor = request.POST.get('DevVendor')
            DeviceIntfCtgrycheck = {}
            DeviceDevCtgrycheck = {}
            DeviceDevpropertiescheck = {}
            DeviceDevVendorcheck = {}
            if IntfCtgry:
                DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
            if DeviceIntfCtgrycheck:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
            else:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
            for i in DeviceIntfCtgrycheckresult:
                if DevCtgry:
                    DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                DeviceDevCtgrycheck['IntfCtgry_P'] = i
                if DeviceDevCtgrycheck:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                else:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                for j in DeviceDevCtgrycheckresult:
                    if Devproperties:
                        DeviceDevpropertiescheck['Devproperties'] = Devproperties
                    DeviceDevpropertiescheck['DevCtgry_P'] = j
                    # print(DeviceDevpropertiescheck)
                    if DeviceDevpropertiescheck:
                        DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                            **DeviceDevpropertiescheck)
                    else:
                        DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                    for k in DeviceDevpropertiescheckresult:
                        if DevVendor:
                            DeviceDevVendorcheck['DevVendor'] = DevVendor
                        DeviceDevVendorcheck['Devproperties_P'] = k
                        # print(DeviceDevVendorcheck)
                        if DeviceDevVendorcheck:
                            DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                **DeviceDevVendorcheck)
                        else:
                            DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                        for l in DeviceDevVendorcheckresult:
                            # print(l)
                            DevVendorTable.append({"id": l.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                   "Devproperties": k.Devproperties, "DevVendor": l.DevVendor})
        if 'editSubmit4' in str(request.body):
            responseData = json.loads(request.body)
            editID = responseData['editID']
            NewIntfCtgry = responseData['IntfCtgry']
            NewDevCtgry = responseData['DevCtgry']
            NewDevproperties = responseData['Devproperties']
            NewDevVendor = responseData['DevVendor']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=NewIntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=NewDevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=NewDevproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            NewDevVendorUpdatedic = {'DevVendor': NewDevVendor, "Devproperties_P": Devproperties_P}
            if DeviceDevVendorList.objects.filter(**NewDevVendorUpdatedic):
                errormessae = """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s>DevVendor:%s 已经存在 """ % (
                NewIntfCtgry, NewDevCtgry, NewDevproperties, NewDevVendor)
                print(errormessae)
            else:
                DeviceDevVendorList.objects.filter(id=editID).update(**NewDevVendorUpdatedic)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        if 'DevVendor_search' in str(request.body):
                            DevVendor = responseData['DevVendor_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                DeviceDevVendorcheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        # print(DeviceDevpropertiescheck)
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            if DevVendor:
                                DeviceDevVendorcheck['DevVendor'] = DevVendor
                            DeviceDevVendorcheck['Devproperties_P'] = k
                            # print(DeviceDevVendorcheck)
                            if DeviceDevVendorcheck:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                    **DeviceDevVendorcheck)
                            else:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                            for l in DeviceDevVendorcheckresult:
                                # print(l)
                                DevVendorTable.append({"id": l.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                       "Devproperties": k.Devproperties, "DevVendor": l.DevVendor})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'addSubmit4' in str(request.body):
            responseData = json.loads(request.body)
            IntfCtgry = responseData['IntfCtgry']
            DevCtgry = responseData['DevCtgry']
            Devproperties = responseData['Devproperties']
            DevVendor = responseData['DevVendor']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            if DeviceDevVendorList.objects.filter(DevVendor=DevVendor, Devproperties_P=Devproperties_P):
                errormessae = """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s>DevVendor:%s 已经存在 """ % (
                IntfCtgry, DevCtgry, Devproperties, DevVendor)
                print(errormessae)
            else:
                # print(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first(),type(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()))
                DeviceDevVendorList.objects.create(DevVendor=DevVendor, Devproperties_P=Devproperties_P)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        if 'DevVendor_search' in str(request.body):
                            DevVendor = responseData['DevVendor_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                DeviceDevVendorcheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        # print(DeviceDevpropertiescheck)
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            if DevVendor:
                                DeviceDevVendorcheck['DevVendor'] = DevVendor
                            DeviceDevVendorcheck['Devproperties_P'] = k
                            # print(DeviceDevVendorcheck)
                            if DeviceDevVendorcheck:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                    **DeviceDevVendorcheck)
                            else:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                            for l in DeviceDevVendorcheckresult:
                                # print(l)
                                DevVendorTable.append({"id": l.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                       "Devproperties": k.Devproperties, "DevVendor": l.DevVendor})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'Delete4' in str(request.body):
            responseData = json.loads(request.body)
            DeleteId = responseData['DeleteId']
            # print(DeleteId)
            IntfCtgry = responseData['IntfCtgry_search']
            DevCtgry = responseData['DevCtgry_search']
            DevVendor = responseData['DevVendor_search']
            errormessae = """"""
            # print(DeleteId)
            for i in DeleteId:
                try:
                    DeviceDevVendorList.objects.filter(id=i).delete()
                except:
                    msgvalue = DeviceDevVendorList.objects.filter(id=i).first()
                    errormessae += """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s >DevVendor:%s 有下层关联数据<br/>""" % (
                    IntfCtgry, msgvalue.Devproperties_P.DevCtgry_P.DevCtgry, msgvalue.Devproperties_P.Devproperties,
                    msgvalue.DevVendor)
                    print(errormessae)
                    print(i)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        if 'DevVendor_search' in str(request.body):
                            DevVendor = responseData['DevVendor_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                DeviceDevVendorcheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        # print(DeviceDevpropertiescheck)
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            if DevVendor:
                                DeviceDevVendorcheck['DevVendor'] = DevVendor
                            DeviceDevVendorcheck['Devproperties_P'] = k
                            # print(DeviceDevVendorcheck)
                            if DeviceDevVendorcheck:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                    **DeviceDevVendorcheck)
                            else:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                            for l in DeviceDevVendorcheckresult:
                                # print(l)
                                DevVendorTable.append({"id": l.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                       "Devproperties": k.Devproperties, "DevVendor": l.DevVendor})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

        if 'SEARCH5' in str(request.body):
            IntfCtgry = request.POST.get('IntfCtgry')
            DevCtgry = request.POST.get('DevCtgry')
            Devproperties = request.POST.get('Devproperties')
            DevVendor = request.POST.get('DevVendor')
            Devsize = request.POST.get('Devsize')
            DeviceIntfCtgrycheck = {}
            DeviceDevCtgrycheck = {}
            DeviceDevpropertiescheck = {}
            DeviceDevVendorcheck = {}
            DeviceDevsizecheck = {}
            if IntfCtgry:
                DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
            if DeviceIntfCtgrycheck:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
            else:
                DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
            for i in DeviceIntfCtgrycheckresult:
                if DevCtgry:
                    DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                DeviceDevCtgrycheck['IntfCtgry_P'] = i
                if DeviceDevCtgrycheck:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                else:
                    DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                for j in DeviceDevCtgrycheckresult:
                    if Devproperties:
                        DeviceDevpropertiescheck['Devproperties'] = Devproperties
                    DeviceDevpropertiescheck['DevCtgry_P'] = j
                    # print(DeviceDevpropertiescheck)
                    if DeviceDevpropertiescheck:
                        DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                            **DeviceDevpropertiescheck)
                    else:
                        DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                    for k in DeviceDevpropertiescheckresult:
                        if DevVendor:
                            DeviceDevVendorcheck['DevVendor'] = DevVendor
                        DeviceDevVendorcheck['Devproperties_P'] = k
                        # print(DeviceDevVendorcheck)
                        if DeviceDevVendorcheck:
                            DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                **DeviceDevVendorcheck)
                        else:
                            DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                        for l in DeviceDevVendorcheckresult:
                            # print(l)
                            if Devsize:
                                DeviceDevsizecheck['Devsize'] = Devsize
                            DeviceDevsizecheck['DevVendor_P'] = l
                            print(DeviceDevsizecheck)
                            if DeviceDevsizecheck:
                                DeviceDevsizecheckresult = DeviceDevsizeList.objects.filter(
                                    **DeviceDevsizecheck)
                            else:
                                DeviceDevsizecheckresult = DeviceDevsizeList.objects.all()
                            for m in DeviceDevsizecheckresult:
                                # print(m)
                                DevsizeTable.append({"id": m.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                     "Devproperties": k.Devproperties, "DevVendor": l.DevVendor,
                                                     "Devsize": m.Devsize})
        if 'editSubmit5' in str(request.body):
            responseData = json.loads(request.body)
            editID = responseData['editID']
            NewIntfCtgry = responseData['IntfCtgry']
            NewDevCtgry = responseData['DevCtgry']
            NewDevproperties = responseData['Devproperties']
            NewDevVendor = responseData['DevVendor']
            NewDevsize = responseData['Devsize']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=NewIntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=NewDevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=NewDevproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            DevVendor_P = DeviceDevVendorList.objects.filter(DevVendor=NewDevVendor,
                                                             Devproperties_P=Devproperties_P).first()
            NewDevsizeUpdatedic = {'Devsize': NewDevsize, "DevVendor_P": DevVendor_P}
            if DeviceDevsizeList.objects.filter(**NewDevsizeUpdatedic):
                errormessae = """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s>DevVendor:%s>DevVendor:%s 已经存在 """ % (
                NewIntfCtgry, NewDevCtgry, NewDevproperties, NewDevVendor, NewDevsize)
                print(errormessae)
            else:
                DeviceDevsizeList.objects.filter(id=editID).update(**NewDevsizeUpdatedic)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        if 'DevVendor_search' in str(request.body):
                            DevVendor = responseData['DevVendor_search']
                            if 'Devsize_search' in str(request.body):
                                Devsize = responseData['Devsize_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                DeviceDevVendorcheck = {}
                DeviceDevsizecheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        # print(DeviceDevpropertiescheck)
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            if DevVendor:
                                DeviceDevVendorcheck['DevVendor'] = DevVendor
                            DeviceDevVendorcheck['Devproperties_P'] = k
                            # print(DeviceDevVendorcheck)
                            if DeviceDevVendorcheck:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                    **DeviceDevVendorcheck)
                            else:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                            for l in DeviceDevVendorcheckresult:
                                # print(l)
                                if Devsize:
                                    DeviceDevsizecheck['Devsize'] = Devsize
                                DeviceDevsizecheck['DevVendor_P'] = l
                                # print(DeviceDevsizecheck)
                                if DeviceDevsizecheck:
                                    DeviceDevsizecheckresult = DeviceDevsizeList.objects.filter(
                                        **DeviceDevsizecheck)
                                else:
                                    DeviceDevsizecheckresult = DeviceDevsizeList.objects.all()
                                for m in DeviceDevsizecheckresult:
                                    # print(m,m.Devsize)
                                    DevsizeTable.append({"id": m.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                         "Devproperties": k.Devproperties, "DevVendor": l.DevVendor,
                                                         "Devsize": m.Devsize})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'addSubmit5' in str(request.body):
            # print(1)
            responseData = json.loads(request.body)
            IntfCtgry = responseData['IntfCtgry']
            DevCtgry = responseData['DevCtgry']
            Devproperties = responseData['Devproperties']
            DevVendor = responseData['DevVendor']
            Devsize = responseData['Devsize']
            IntfCtgry_P = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
            DevCtgry_P = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgry_P).first()
            Devproperties_P = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                     DevCtgry_P=DevCtgry_P).first()
            DevVendor_P = DeviceDevVendorList.objects.filter(DevVendor=DevVendor,
                                                             Devproperties_P=Devproperties_P).first()
            if DeviceDevsizeList.objects.filter(Devsize=Devsize, DevVendor_P=DevVendor_P):
                errormessae = """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s>DevVendor:%s>Devsize:%s 已经存在 """ % (
                IntfCtgry, DevCtgry, Devproperties, DevVendor, Devsize)
                print(errormessae)
            else:
                # print(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first(),type(DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()))
                DeviceDevsizeList.objects.create(Devsize=Devsize, DevVendor_P=DevVendor_P)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        if 'DevVendor_search' in str(request.body):
                            DevVendor = responseData['DevVendor_search']
                            if 'Devsize_search' in str(request.body):
                                Devsize = responseData['Devsize_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                DeviceDevVendorcheck = {}
                DeviceDevsizecheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        # print(DeviceDevpropertiescheck)
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            if DevVendor:
                                DeviceDevVendorcheck['DevVendor'] = DevVendor
                            DeviceDevVendorcheck['Devproperties_P'] = k
                            # print(DeviceDevVendorcheck)
                            if DeviceDevVendorcheck:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                    **DeviceDevVendorcheck)
                            else:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                            for l in DeviceDevVendorcheckresult:
                                # print(l)
                                if Devsize:
                                    DeviceDevsizecheck['Devsize'] = Devsize
                                DeviceDevsizecheck['DevVendor_P'] = l
                                # print(DeviceDevsizecheck)
                                if DeviceDevsizecheck:
                                    DeviceDevsizecheckresult = DeviceDevsizeList.objects.filter(
                                        **DeviceDevsizecheck)
                                else:
                                    DeviceDevsizecheckresult = DeviceDevsizeList.objects.all()
                                for m in DeviceDevsizecheckresult:
                                    # print(m,m.Devsize)
                                    DevsizeTable.append({"id": m.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                         "Devproperties": k.Devproperties, "DevVendor": l.DevVendor,
                                                         "Devsize": m.Devsize})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        if 'Delete5' in str(request.body):
            responseData = json.loads(request.body)
            DeleteId = responseData['DeleteId']
            # print(DeleteId)
            IntfCtgry = responseData['IntfCtgry_search']
            DevCtgry = responseData['DevCtgry_search']
            DevVendor = responseData['DevVendor_search']
            Devsize = responseData['Devsize_search']
            errormessae = """"""
            # print(DeleteId)
            for i in DeleteId:
                try:
                    DeviceDevsizeList.objects.filter(id=i).delete()
                except:
                    msgvalue = DeviceDevsizeList.objects.filter(id=i).first()
                    errormessae += """IntfCtgry:%s>DevCtgry:%s>Devproperties:%s>DevVendor:%s>Devsize:%s 有下层关联数据<br/>""" % (
                    IntfCtgry, msgvalue.DevVendor_P.Devproperties_P.DevCtgry_P.DevCtgry,
                    msgvalue.DevVendor_P.Devproperties_P.Devproperties, msgvalue.DevVendor_P.DevVendor,
                    msgvalue.Devsize)
                    print(errormessae)
                    print(i)

            if 'IntfCtgry_search' in str(request.body):
                IntfCtgry = responseData['IntfCtgry_search']
                if 'DevCtgry_search' in str(request.body):
                    DevCtgry = responseData['DevCtgry_search']
                    if 'Devproperties_search' in str(request.body):
                        Devproperties = responseData['Devproperties_search']
                        if 'DevVendor_search' in str(request.body):
                            DevVendor = responseData['DevVendor_search']
                            if 'Devsize_search' in str(request.body):
                                Devsize = responseData['Devsize_search']
                        # print(IntfCtgry, DevCtgry, Devproperties)
                DeviceIntfCtgrycheck = {}
                DeviceDevCtgrycheck = {}
                DeviceDevpropertiescheck = {}
                DeviceDevVendorcheck = {}
                DeviceDevsizecheck = {}
                if IntfCtgry:
                    DeviceIntfCtgrycheck['IntfCtgry'] = IntfCtgry
                if DeviceIntfCtgrycheck:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.filter(**DeviceIntfCtgrycheck)
                else:
                    DeviceIntfCtgrycheckresult = DeviceIntfCtgryList.objects.all()
                for i in DeviceIntfCtgrycheckresult:
                    if DevCtgry:
                        DeviceDevCtgrycheck['DevCtgry'] = DevCtgry
                    DeviceDevCtgrycheck['IntfCtgry_P'] = i
                    if DeviceDevCtgrycheck:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.filter(**DeviceDevCtgrycheck)
                    else:
                        DeviceDevCtgrycheckresult = DeviceDevCtgryList.objects.all()
                    for j in DeviceDevCtgrycheckresult:
                        if Devproperties:
                            DeviceDevpropertiescheck['Devproperties'] = Devproperties
                        DeviceDevpropertiescheck['DevCtgry_P'] = j
                        # print(DeviceDevpropertiescheck)
                        if DeviceDevpropertiescheck:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.filter(
                                **DeviceDevpropertiescheck)
                        else:
                            DeviceDevpropertiescheckresult = DeviceDevpropertiesList.objects.all()
                        for k in DeviceDevpropertiescheckresult:
                            if DevVendor:
                                DeviceDevVendorcheck['DevVendor'] = DevVendor
                            DeviceDevVendorcheck['Devproperties_P'] = k
                            # print(DeviceDevVendorcheck)
                            if DeviceDevVendorcheck:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.filter(
                                    **DeviceDevVendorcheck)
                            else:
                                DeviceDevVendorcheckresult = DeviceDevVendorList.objects.all()
                            for l in DeviceDevVendorcheckresult:
                                # print(l)
                                if Devsize:
                                    DeviceDevsizecheck['Devsize'] = Devsize
                                DeviceDevsizecheck['DevVendor_P'] = l
                                # print(DeviceDevsizecheck)
                                if DeviceDevsizecheck:
                                    DeviceDevsizecheckresult = DeviceDevsizeList.objects.filter(
                                        **DeviceDevsizecheck)
                                else:
                                    DeviceDevsizecheckresult = DeviceDevsizeList.objects.all()
                                for m in DeviceDevsizecheckresult:
                                    # print(m,m.Devsize)
                                    DevsizeTable.append({"id": m.id, "IntfCtgry": i.IntfCtgry, "DevCtgry": j.DevCtgry,
                                                         "Devproperties": k.Devproperties, "DevVendor": l.DevVendor,
                                                         "Devsize": m.Devsize})

            if DeviceIntfCtgryList.objects.all():
                for i in DeviceIntfCtgryList.objects.all():
                    IntfCtgryOptions.append(i.IntfCtgry)

                    DeviceDevCtgryListvalue = []
                    DeviceDevCtgryDevpropertiesListvalue = []
                    for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                        DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                        DeviceDevpropertiesListvalue = []
                        for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                            DeviceDevpropertiesListvalue.append(k.Devproperties)
                        DeviceDevCtgryDevpropertiesListvalue.append(
                            {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

                    IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
                    IntfCtgryOptions3[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions4[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
                    IntfCtgryOptions5[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue
        data = {
            "IntfCtgryOptions": IntfCtgryOptions,
            "IntfCtgryTable": IntfCtgryTable,
            "IntfCtgryOptions2": IntfCtgryOptions2,
            "DevCtgryTable": DevCtgryTable,
            "IntfCtgryOptions3": IntfCtgryOptions3,
            "DevpropertiesTable": DevpropertiesTable,
            "IntfCtgryOptions4": IntfCtgryOptions4,
            "DevVendorOptions4": DevVendorOptions4,
            "DevVendorTable": DevVendorTable,
            "IntfCtgryOptions5": IntfCtgryOptions5,
            "DevVendorOptions5": DevVendorOptions5,
            "DevsizeTable": DevsizeTable,
            'err_MSG': errormessae,
            'canExport': 1,
        }
        # print(data)
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/M_Category.html', locals())


@csrf_exempt
def M_edit(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceABO/M_upload"
    mock_data = [
        # {"id": "2", "Customer": "C38", "Plant": "KS",
        #  "NID": "1514", "DevID": "UKB0022B", "IntfCtgry": "USB_A",
        #  "DevCtgry": "Keyboard", "Devproperties": "USB1.0", "Devsize": "--",
        #  "DevVendor": "Lenovo", "DevModel": "SK-8815(L)", "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #  "HWVer": "", "FWVer": "", "DevDescription": "N/A", "PckgIncludes": "1. 說明書",
        #  "expirdate": "一年", "DevPrice": "", "Source": "Lenovo贈送", "Pchsdate": "", "PN": "73P2620",
        #  "LNV_ST": "", "Purchase_NO": "", "Declaration_NO": "12", "AssetNum": "", "UsYear": "2.7",
        #  "addnewname": "代月景", "addnewdate": "2018-08-01",
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "預定確認中", "Usrname": "單桂萍","Usrnumber": "123333333",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "", "Overday": ""},
    ]

    selectItem = [
        # {"value": "姚麗麗", "number": "20652552"}, {"value": "姚麗麗", "number": "20564439"},
        # {"value": "單桂萍", "number": "123333333"},
    ]

    # 歷史記錄
    tableData = [
        # {
        #     "id": "1", "NID": "1514", "DevID": "UKB0022B", "DevModel": "SK-8815(L)",
        #     "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #     "uscyc": "100", "Btime": "2020-01-25", "Rtime": "2020-01-26", "Usrname": "單桂萍", "BR_per_code": "12345678",
        # },
    ]

    selectIntfCtgry = {
        # "USB_A": [{"DevCtgry": "Keyboard", "Devproperties": ["USB1.0", "USB1.1"]},
        #           {"DevCtgry": "Wireless card", "Devproperties": ["USB2.0"]},
        #           {"DevCtgry": "USB Memory", "Devproperties": ["USB2.0, USB3.0, USB3.1"]}],
        # "USB_B": [{"DevCtgry": "Keyboard", "Devproperties": ["USB1.0,USB1.1"]},
        #           {"DevCtgry": "Wireless card", "Devproperties": ["USB2.0"]},
        #           {"DevCtgry": "USB Memory", "Devproperties": ["USB2.0, USB3.0, USB3.1"]}],
    }

    selectOption = {
        # "IBM": [
        #     {"Devsize": "4G",},搜索
        #         {"Devsize": "16G"}
        #         ],
    }

    formselectOption = {
        # "IBM": [{"Devsize": "4G, 16G, 32G, 64G"}],
        # "Lenovo": [{"Devsize": "256G, 500G, 1TB"}],
        # "Acer": [{"Devsize": "16G, 32G"}],
    }

    form1selectOption = {
        # "IBM": [{"Devsize": "4G, 16G, 32G, 64G"}],
        # "Lenovo": [{"Devsize": "256G, 500G, 1TB"}],
        # "Acer": [{"Devsize": "16G, 32G"}],
    }
    sectionCustomer = [
        "C38", "A39", "ABO"
    ]

    sectionPlant = [
        "KS", "CQ"
    ]

    sectionexpirdate = [
        "一年", "兩年", "三年", "四年", "五年"
    ]

    sectionDevStatus = [
        "Good", "Fixed", "Damaged", "Lost"
    ]

    sectionBrwStatus = [
        "驗收中", "可借用", "固定設備", "長期借用", "已借出", "歸還確認中", "預定確認中", "續借確認中"
    ]

    sectionPhase = [
        "NPI",
    ]
    sectionLNVST = ["Must", "Optional", "Similar"]

    for i in UserInfo.objects.filter(role__name="Device_LNV_Users").values('account', 'CNname').distinct().order_by(
            'CNname'):
        selectItem.append({"value": i["CNname"], "number": i["account"]})
    #     print(i,'1')
    # for i in UserInfo.objects.all().values('account', 'CNname').distinct().order_by(
    #         'CNname'):
    #     print(i,'2')

    # if DeviceIntfCtgryList.objects.all():
    #     for i in DeviceIntfCtgryList.objects.values("IntfCtgry").distinct().order_by("IntfCtgry"):
    #         print(i)
    #         DevCtgryList = []
    #         if DeviceDevCtgryList.objects.filter(IntfCtgry_P__IntfCtgry=i['IntfCtgry']):
    #             for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P__IntfCtgry=i['IntfCtgry']).values("DevCtgry").distinct().order_by("DevCtgry"):
    #                 # print(j['DevCtgry'])
    #                 print(j)
    #                 Devpropertieslist = []
    #                 if DeviceDevCtgryList.objects.filter(IntfCtgry_P__IntfCtgry=i['IntfCtgry']):
    #                     for m in DeviceDevpropertiesList.objects.filter(DevCtgry_P__DevCtgry=j['DevCtgry']).values('Devproperties').distinct().order_by('Devproperties'):
    #                         print(m)
    #                         Devpropertieslist.append(m['Devproperties'])
    #                 DevCtgryList.append({"DevCtgry": j['DevCtgry'], 'Devproperties': Devpropertieslist})
    #         selectIntfCtgry[i["IntfCtgry"]] = DevCtgryList

    if DeviceIntfCtgryList.objects.all():
        for i in DeviceIntfCtgryList.objects.all():
            # IntfCtgryOptions.append(i.IntfCtgry)

            DeviceDevCtgryListvalue = []
            DeviceDevCtgryDevpropertiesListvalue = []
            for j in DeviceDevCtgryList.objects.filter(IntfCtgry_P=i.id):
                DeviceDevCtgryListvalue.append({"DevCtgry": j.DevCtgry})

                DeviceDevpropertiesListvalue = []
                for k in DeviceDevpropertiesList.objects.filter(DevCtgry_P=j.id):
                    DeviceDevpropertiesListvalue.append(k.Devproperties)
                DeviceDevCtgryDevpropertiesListvalue.append(
                    {"DevCtgry": j.DevCtgry, "Devproperties": DeviceDevpropertiesListvalue})

            # IntfCtgryOptions2[i.IntfCtgry] = DeviceDevCtgryListvalue
            selectIntfCtgry[i.IntfCtgry] = DeviceDevCtgryDevpropertiesListvalue

    Lent = ''  # 已借出
    kejieyong = ''  # 可借用
    jieyongyuding = ''  # 預定確認中
    guihuanqueren = ''  # 歸還確認中
    errMsg = ''
    errMsgNumber = ''  # 新增弹框
    # print(DeviceABO._meta.fields)
    # # print([f.name for f DeviceABO._meta.fields])
    # iii=0
    # for i in DeviceABO._meta.fields:
    #     print(i.name, type(i), i.get_internal_type())
    # iii+=1
    # print(iii)
    # print(DeviceABO._meta.get_fields())
    # print(request.method)
    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if request.POST:
            # if request.POST.get('isGetData') == 'first':
            #     # mock_data
            #     mock_datalist = DeviceABO.objects.all()
            #     for i in mock_datalist:
            #         Photolist = []
            #         for h in i.Photo.all():
            #             Photolist.append(
            #                 {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
            #         if i.Predict_return and not i.Return_date:
            #             if datetime.datetime.now().date() > i.Predict_return:
            #                 Exceed_days = round(
            #                     float(
            #                         str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
            #                             0]),
            #                     0)
            #             else:
            #                 Exceed_days = ''
            #         else:
            #             Exceed_days = ''
            #         Predict_return_str = ''
            #         if i.Predict_return:
            #             Predict_return_str = str(i.Predict_return)
            #         else:
            #             Predict_return_str = ''
            #         Borrow_date_str = ''
            #         if i.Borrow_date:
            #             Borrow_date_str = str(i.Borrow_date)
            #         else:
            #             Borrow_date_str = ''
            #         Return_date_str = ''
            #         if i.Return_date:
            #             Return_date_str = str(i.Return_date)
            #         else:
            #             Return_date_str = ''
            #         Last_Borrow_date_str = ''
            #         if i.Last_Borrow_date:
            #             Last_Borrow_date_str = str(i.Last_Borrow_date)
            #         else:
            #             Last_Borrow_date_str = ''
            #         Last_Return_date_str = ''
            #         if i.Last_Return_date:
            #             Last_Return_date_str = str(i.Last_Return_date)
            #         else:
            #             Last_Return_date_str = ''
            #         mock_data.append(
            #             {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
            #              "Description": i.Description,
            #              "Power": i.Power,
            #              "Number": i.Number, "Location": i.Location,
            #              "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
            #              "Customer": i.Customer,
            #              "Project_Code": i.Project_Code,
            #              "Phase": i.Phase,
            #              "OAP": i.OAP,
            #              "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
            #              "Predict_return": Predict_return_str,
            #              "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
            #              "Last_BR_per": i.Last_BR_per,
            #              "Last_Borrow_date": Last_Borrow_date_str,
            #              "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
            #              "fileListO": Photolist},
            #         )
            #
            #     # print(mock_data)
            if request.POST.get('isGetData') == 'SearchJiLian':
                IntfCtgry = request.POST.get('IntfCtgry')
                IntfCtgrysearch = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry = request.POST.get('DevCtgry')
                DevCtgrysearch = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry,
                                                                   IntfCtgry_P=IntfCtgrysearch).first()
                # print(DevCtgrysearch)
                Devproperties = request.POST.get('Devproperties')
                Devpropertiessearch = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                             DevCtgry_P=DevCtgrysearch).first()
                # print(Devpropertiessearch)
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devpropertiessearch).values(
                        'DevVendor').distinct().order_by('DevVendor'):  # 其实去不去重无所谓，都是唯一的
                    # print(i)
                    sizelist = []
                    if DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']):
                        for j in DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']).values(
                                'Devsize').distinct().order_by('Devsize'):  # 其实去不去重无所谓，都是唯一的
                            sizelist.append({"Devsize": j['Devsize']})
                    selectOption[i['DevVendor']] = sizelist
            if request.POST.get('isGetData') == 'InsertJiLian':
                IntfCtgry = request.POST.get('IntfCtgry')
                IntfCtgrysearch = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry = request.POST.get('DevCtgry')
                DevCtgrysearch = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry,
                                                                   IntfCtgry_P=IntfCtgrysearch).first()
                # print(DevCtgrysearch)
                Devproperties = request.POST.get('Devproperties')
                Devpropertiessearch = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                             DevCtgry_P=DevCtgrysearch).first()
                # print(Devpropertiessearch)
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devpropertiessearch).values(
                        'DevVendor').distinct().order_by('DevVendor'):  # 其实去不去重无所谓，都是唯一的
                    # print(i)
                    sizelist = []
                    if DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']):
                        for j in DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']).values(
                                'Devsize').distinct().order_by('Devsize'):  # 其实去不去重无所谓，都是唯一的
                            sizelist.append({"Devsize": j['Devsize']})
                    formselectOption[i['DevVendor']] = sizelist
                # print(formselectOption)
            if request.POST.get('isGetData') == 'UpdateJiLian':
                IntfCtgry = request.POST.get('IntfCtgry')
                IntfCtgrysearch = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry = request.POST.get('DevCtgry')
                DevCtgrysearch = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry,
                                                                   IntfCtgry_P=IntfCtgrysearch).first()
                # print(DevCtgrysearch)
                Devproperties = request.POST.get('Devproperties')
                Devpropertiessearch = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties,
                                                                             DevCtgry_P=DevCtgrysearch).first()
                # print(Devpropertiessearch)
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devpropertiessearch).values(
                        'DevVendor').distinct().order_by('DevVendor'):  # 其实去不去重无所谓，都是唯一的
                    # print(i)
                    sizelist = []
                    if DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']):
                        for j in DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']).values(
                                'Devsize').distinct().order_by('Devsize'):  # 其实去不去重无所谓，都是唯一的
                            sizelist.append({"Devsize": j['Devsize']})
                    form1selectOption[i['DevVendor']] = sizelist

            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {}
                IntfCtgry = request.POST.get('IntfCtgry')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                DevCtgry = request.POST.get('DevCtgry')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                Devproperties = request.POST.get('Devproperties')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                DevVendor = request.POST.get('DevVendor')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devsize = request.POST.get('Devsize')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize
                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('action') == "submit":
                checkAdaPow = {}
                DevCtgry = request.POST.get('DevCtgrySearch')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                DevVendor = request.POST.get('DevVendorSearch')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devproperties = request.POST.get('DevpropertiesSearch')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                IntfCtgry = request.POST.get('IntfCtgrySearch')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                Devsize = request.POST.get('DevsizeSearch')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize
                # print(checkAdaPow)

                Customer = request.POST.get('Customer')
                Plant = request.POST.get('Plant')
                NID = request.POST.get('NID')
                DevID = request.POST.get('DevID')
                IntfCtgry = request.POST.get('IntfCtgry')
                DevCtgry = request.POST.get('DevCtgry')
                Devproperties = request.POST.get('Devproperties')
                DevVendor = request.POST.get('DevVendor')
                Devsize = request.POST.get('Devsize')
                DevModel = request.POST.get('DevModel')
                DevName = request.POST.get('DevName')
                HWVer = request.POST.get('HWVer')
                FWVer = request.POST.get('FWVer')
                DevDescription = request.POST.get('DevDescription')
                PckgIncludes = request.POST.get('PckgIncludes')
                expirdate = request.POST.get('expirdate')
                DevPrice = request.POST.get('DevPrice')
                Source = request.POST.get('Source')
                Pchsdate = request.POST.get('Pchsdate')
                if not Pchsdate or Pchsdate == 'null':
                    Pchsdate = None  # 日期爲空
                PN = request.POST.get('PN')
                Declaration_NO = request.POST.get('Declaration_NO')
                AssetNum = request.POST.get('AssetNum')
                addnewname = request.POST.get('addnewname')
                addnewdate = request.POST.get('addnewdate')
                if not addnewdate or addnewdate == 'null':
                    addnewdate = None  # 日期爲空
                Comment = request.POST.get('Comment')
                uscyc = request.POST.get('uscyc')
                UsrTimes = request.POST.get('UsrTimes')
                DevStatus = request.POST.get('DevStatus')
                BrwStatus = request.POST.get('BrwStatus')
                Usrname = request.POST.get('Usrname')
                BR_per_code = request.POST.get('Usrnumber')
                Plandate = request.POST.get('Plandate')
                if not Plandate or Plandate == 'null':
                    Plandate = None  # 日期爲空
                useday = request.POST.get('useday')
                Btime = request.POST.get('Btime')
                if not Btime or Btime == 'null':
                    Btime = None  # 日期爲空
                Rtime = request.POST.get('Rtime')
                if not Rtime or Rtime == 'null':
                    Rtime = None  # 日期爲空
                LNV_ST = request.POST.get('LNV_ST')
                Purchase_NO = request.POST.get('Purchase_NO')

                createdic = {
                    "Customer": Customer, "Plant": Plant,
                    "NID": NID, "DevID": DevID, "IntfCtgry": IntfCtgry,
                    "DevCtgry": DevCtgry, "Devproperties": Devproperties, "DevVendor": DevVendor,
                    "Devsize": Devsize, "DevModel": DevModel,
                    "DevName": DevName,
                    "HWVer": HWVer, "FWVer": FWVer, "DevDescription": DevDescription,
                    "PckgIncludes": PckgIncludes,
                    "expirdate": expirdate, "DevPrice": DevPrice, "Source": Source,
                    "Pchsdate": Pchsdate,
                    "PN": PN,
                    "LSTA": LNV_ST, "ApplicationNo": Purchase_NO,
                    "DeclarationNo": Declaration_NO,
                    "AssetNum": AssetNum, "useday": useday,
                    "addnewname": addnewname, "addnewdate": addnewdate,
                    "Comment": Comment, "uscyc": uscyc, "UsrTimes": UsrTimes,
                    "DevStatus": DevStatus, "BrwStatus": BrwStatus,
                    "Usrname": Usrname, "BR_per_code": BR_per_code,
                    "Plandate": Plandate, "Btime": Btime,
                    "Rtime": Rtime,
                }
                # print(createdic)
                if DeviceABO.objects.filter(NID=NID):
                    errMsgNumber = """設備序號已存在"""
                else:
                    # print(createdic)
                    DeviceABO.objects.create(**createdic)
                    # print(Photo)
                    # if Photo:
                    #     for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                    #         # print(f)
                    #         empt = PICS()
                    #         # 增加其他字段应分别对应填写
                    #         empt.single = f
                    #         empt.pic = f
                    #         empt.save()
                    #         DeviceABO.objects.filter(Number=Number).first().Photo.add(empt)

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.all()
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
                         "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo,
                         "Declaration_NO": i.DeclarationNo,
                         "AssetNum": i.AssetNum, "UsYear": Useyears,
                         "addnewname": i.addnewname, "addnewdate": addnewdate_str,
                         "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                         "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                         "Usrname": i.Usrname, 'Usrnumber': i.BR_per_code,
                         "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str,
                         "Rtime": Rtime_str,
                         "Overday": Exceed_days},
                    )
            if request.POST.get('action') == "submit1":
                checkAdaPow = {}
                DevCtgry = request.POST.get('DevCtgrySearch')
                if DevCtgry and DevCtgry != "All":
                    checkAdaPow['DevCtgry'] = DevCtgry
                DevVendor = request.POST.get('DevVendorSearch')
                if DevVendor and DevVendor != "All":
                    checkAdaPow['DevVendor'] = DevVendor
                Devproperties = request.POST.get('DevpropertiesSearch')
                if Devproperties and Devproperties != "All":
                    checkAdaPow['Devproperties'] = Devproperties
                IntfCtgry = request.POST.get('IntfCtgrySearch')
                if IntfCtgry and IntfCtgry != "All":
                    checkAdaPow['IntfCtgry'] = IntfCtgry
                Devsize = request.POST.get('DevsizeSearch')
                if Devsize and Devsize != "All":
                    checkAdaPow['Devsize'] = Devsize

                id = request.POST.get('id')
                Customer = request.POST.get('Customer')
                Plant = request.POST.get('Plant')
                NID = request.POST.get('NID')
                DevID = request.POST.get('DevID')
                IntfCtgry = request.POST.get('IntfCtgry')
                DevCtgry = request.POST.get('DevCtgry')
                Devproperties = request.POST.get('Devproperties')
                DevVendor = request.POST.get('DevVendor')
                Devsize = request.POST.get('Devsize')
                DevModel = request.POST.get('DevModel')
                DevName = request.POST.get('DevName')
                HWVer = request.POST.get('HWVer')
                FWVer = request.POST.get('FWVer')
                DevDescription = request.POST.get('DevDescription')
                PckgIncludes = request.POST.get('PckgIncludes')
                expirdate = request.POST.get('expirdate')
                DevPrice = request.POST.get('DevPrice')
                Source = request.POST.get('Source')
                Pchsdate = request.POST.get('Pchsdate')
                if not Pchsdate or Pchsdate == 'null':
                    Pchsdate = None  # 日期爲空
                PN = request.POST.get('PN')
                Declaration_NO = request.POST.get('Declaration_NO')
                AssetNum = request.POST.get('AssetNum')
                addnewname = request.POST.get('addnewname')
                addnewdate = request.POST.get('addnewdate')
                if not addnewdate or addnewdate == 'null':
                    addnewdate = None  # 日期爲空
                Comment = request.POST.get('Comment')
                uscyc = request.POST.get('uscyc')
                UsrTimes = request.POST.get('UsrTimes')
                DevStatus = request.POST.get('DevStatus')
                BrwStatus = request.POST.get('BrwStatus')
                Usrname = request.POST.get('Usrname')
                BR_per_code = request.POST.get('Usrnumber')
                Plandate = request.POST.get('Plandate')
                if not Plandate or Plandate == 'null':
                    Plandate = None  # 日期爲空
                useday = request.POST.get('useday')
                Btime = request.POST.get('Btime')
                if not Btime or Btime == 'null':
                    Btime = None  # 日期爲空
                Rtime = request.POST.get('Rtime')
                if not Rtime or Rtime == 'null':
                    Rtime = None  # 日期爲空
                LNV_ST = request.POST.get('LNV_ST')
                Purchase_NO = request.POST.get('Purchase_NO')

                updatedic = {
                    "Customer": Customer, "Plant": Plant,
                    "NID": NID, "DevID": DevID, "IntfCtgry": IntfCtgry,
                    "DevCtgry": DevCtgry, "Devproperties": Devproperties, "DevVendor": DevVendor,
                    "Devsize": Devsize, "DevModel": DevModel,
                    "DevName": DevName,
                    "HWVer": HWVer, "FWVer": FWVer, "DevDescription": DevDescription,
                    "PckgIncludes": PckgIncludes,
                    "expirdate": expirdate, "DevPrice": DevPrice, "Source": Source,
                    "Pchsdate": Pchsdate,
                    "PN": PN,
                    "LSTA": LNV_ST, "ApplicationNo": Purchase_NO,
                    "DeclarationNo": Declaration_NO,
                    "AssetNum": AssetNum, "useday": useday,
                    "addnewname": addnewname, "addnewdate": addnewdate,
                    "Comment": Comment, "uscyc": uscyc, "UsrTimes": UsrTimes,
                    "DevStatus": DevStatus, "BrwStatus": BrwStatus,
                    "Usrname": Usrname, "BR_per_code": BR_per_code,
                    "Plandate": Plandate, "Btime": Btime,
                    "Rtime": Rtime,
                }
                # if DeviceABO.objects.filter(Number=Number):
                #     errMsgNumber = """编号已存在"""
                # else:
                # print(updatedic)
                try:
                    with transaction.atomic():
                        DeviceABO.objects.filter(id=id).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % id
                # print(Photo)
                # if Photo:
                #     for m in DeviceABO.objects.filter(id=id).first().Photo.all():  # 每次接受图片前清除原来的图片，而不是叠加
                #         # print(m.id)
                #         PICS.objects.filter(
                #             id=m.id).delete()
                #     for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                #         # print(f)
                #         empt = PICS()
                #         # 增加其他字段应分别对应填写
                #         empt.single = f
                #         empt.pic = f
                #         empt.save()
                #         DeviceABO.objects.filter(id=id).first().Photo.add(empt)

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceABO.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                else:
                    mock_datalist = DeviceABO.objects.all()
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
            if request.POST.get('isGetData') == "alertData":
                # id = request.POST.get('ID')
                NID = request.POST.get('NID')
                # print(NID)
                if DeviceABOHis.objects.filter(NID=NID):
                    for i in DeviceABOHis.objects.filter(NID=NID):
                        if i.Btime:
                            Btime_str = str(i.Btime)
                        else:
                            Btime_str = ''
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        tableData.append({
                            "id": i.id, "NID": i.NID, "DevID": i.DevID, "DevModel": i.DevModel,
                            "DevName": i.DevName,
                            "uscyc": i.uscyc, "Btime": Btime_str, "Rtime": Rtime_str, "Usrname": i.Usrname,
                            "BR_per_code": i.BR_per_code,
                        })


        else:
            try:
                request.body
                # print(request.body)
            except:
                # print('1')
                pass
            else:
                # print('2')
                if 'MUTICANCEL' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {}
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devproperties = responseData['Devproperties']
                    if Devproperties and Devproperties != "All":
                        checkAdaPow['Devproperties'] = Devproperties
                    IntfCtgry = responseData['IntfCtgry']
                    if IntfCtgry and IntfCtgry != "All":
                        checkAdaPow['IntfCtgry'] = IntfCtgry
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize
                    for i in responseData['params']:
                        # print(i)
                        DeviceABO.objects.get(id=i).delete()

                    # mock_data
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceABO.objects.all()
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
                if 'ExcelData' in str(request.body):
                    responseData = json.loads(request.body)
                    # print(responseData)
                    # print(responseData['historyYear'],type(responseData['historyYear']))
                    checkAdaPow = {}
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devproperties = responseData['Devproperties']
                    if Devproperties and Devproperties != "All":
                        checkAdaPow['Devproperties'] = Devproperties
                    IntfCtgry = responseData['IntfCtgry']
                    if IntfCtgry and IntfCtgry != "All":
                        checkAdaPow['IntfCtgry'] = IntfCtgry
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize
                    xlsxlist = json.loads(responseData['ExcelData'])
                    # Adapterlist = [
                    #     {
                    #         'Number': '編號', }
                    # ]
                    rownum = 0
                    startupload = 0
                    # print(xlsxlist)
                    uploadxlsxlist = []
                    for i in xlsxlist:
                        print(type(i), i)
                        rownum += 1
                        print(rownum)
                        modeldata = {}
                        for key, value in i.items():
                            if key in headermodel_Device.keys():
                                modeldata[headermodel_Device[key]] = value
                        if 'Customer' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，客戶別不能爲空
                                                                            """ % rownum
                            break
                        if 'Plant' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，廠區不能爲空
                                                                            """ % rownum
                            break
                        if 'NID' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，設備序號不能爲空
                                                                            """ % rownum
                            break
                        if 'IntfCtgry' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，介面種類不能爲空
                                                                            """ % rownum
                            break
                        if 'DevCtgry' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，設備種類不能爲空
                                                                            """ % rownum
                            break
                        if 'Devproperties' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，設備屬性不能爲空
                                                                            """ % rownum
                            break
                        if 'DevVendor' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，設備廠家不能爲空
                                                                            """ % rownum
                            break
                        # if 'DevModel' in modeldata.keys():
                        #     startupload = 1
                        # else:
                        #     # canEdit = 0
                        #     startupload = 0
                        #     err_ok = 2
                        #     errMsg = err_msg = """
                        #                                 第"%s"條數據，設備型號不能爲空
                        #                                                     """ % rownum
                        #     break
                        # if 'DevName' in modeldata.keys():
                        #     startupload = 1
                        # else:
                        #     # canEdit = 0
                        #     startupload = 0
                        #     err_ok = 2
                        #     errMsg = err_msg = """
                        #                                 第"%s"條數據，設備名稱不能爲空
                        #                                                     """ % rownum
                        #     break
                        if 'Pchsdate' in modeldata.keys():
                            # modeldata['Pchsdate'] = modeldata['Pchsdate'].replace('/', '-')
                            # print(len(modeldata['Pchsdate'].split('-')))
                            if len(modeldata['Pchsdate']) >= 8 and len(modeldata['Pchsdate']) <= 10:
                                # modeldata['Pchsdate'].replace('/', '-')
                                # print(modeldata['Pchsdate'].replace('/', '-'))
                                modeldata['Pchsdate'] = modeldata['Pchsdate'].replace('/', '-')
                                modeldata['Pchsdate'] = modeldata['Pchsdate'].replace('.', '-')
                                # print(modeldata['Pchsdate'])
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，購買時間格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['Pchsdate'] = None  # 日期爲空
                        if 'addnewdate' in modeldata.keys():
                            # modeldata['Pchsdate'] = modeldata['Pchsdate'].replace('/', '-')
                            # print(len(modeldata['Pchsdate'].split('-')))
                            # print(len(modeldata['addnewdate']))
                            if len(modeldata['addnewdate']) >= 8 and len(modeldata['addnewdate']) <= 10:
                                modeldata['addnewdate'] = modeldata['addnewdate'].replace('/', '-')
                                modeldata['addnewdate'] = modeldata['addnewdate'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，設備添加日期格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['addnewdate'] = None  # 日期爲空
                        if 'Plandate' in modeldata.keys():
                            if len(modeldata['Plandate']) >= 8 and len(modeldata['Plandate']) <= 10:
                                modeldata['Plandate'] = modeldata['Plandate'].replace('/', '-')
                                modeldata['Plandate'] = modeldata['Plandate'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，預計歸還日期格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['Plandate'] = None  # 日期爲空
                        if 'Btime' in modeldata.keys():
                            if len(modeldata['Btime']) >= 8 and len(modeldata['Btime']) <= 10:
                                modeldata['Btime'] = modeldata['Btime'].replace('/', '-')
                                modeldata['Btime'] = modeldata['Btime'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，借用時間格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['Btime'] = None  # 日期爲空
                        if 'Rtime' in modeldata.keys():
                            if len(modeldata['Rtime']) >= 8 and len(modeldata['Rtime']) <= 10:
                                modeldata['Rtime'] = modeldata['Rtime'].replace('/', '-')
                                modeldata['Rtime'] = modeldata['Rtime'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，歸還日期格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['Rtime'] = None  # 日期爲空
                        uploadxlsxlist.append(modeldata)
                    # print(startupload)
                    # 让数据可以从有值更新为无值
                    DevieModelfiedlist = []
                    for i in DeviceABO._meta.fields:
                        if i.name != 'id':
                            DevieModelfiedlist.append([i.name, i.get_internal_type()])
                    for i in uploadxlsxlist:
                        for j in DevieModelfiedlist:
                            if j[0] not in i.keys():
                                # print(j)
                                if j[1] == "DateField":
                                    i[j[0]] = None
                                else:
                                    i[j[0]] = ''
                    num1 = 0
                    if startupload:
                        for i in uploadxlsxlist:
                            num1 += 1
                            # print(num1)
                            # print(i)
                            # modeldata = {}
                            # for key, value in i.items():
                            #     if key in headermodel_Device.keys():
                            #         if headermodel_Device[key] == "Predict_return" or headermodel_Device[
                            #             key] == "Borrow_date" or headermodel_Device[key] == "Return_date":
                            #             print(value)
                            #             modeldata[headermodel_Device[key]] = value.split("/")[2] + "-" + \
                            #                                                        value.split("/")[0] + "-" + \
                            #                                                        value.split("/")[1]
                            #         else:
                            #             modeldata[headermodel_Device[key]] = value
                            Check_dic = {
                                'NID': i['NID'],
                            }
                            # print(modeldata)
                            # print(i)
                            # Check_dic_Gantt['Test_Start'] = None  # 日期格式为空NULL不能用空字符
                            if DeviceABO.objects.filter(**Check_dic):  # 已经存在覆盖
                                DeviceABO.objects.filter(
                                    **Check_dic).update(**i)
                            else:  # 新增
                                DeviceABO.objects.create(**i)
                        errMsg = '上傳成功'

                    # mock_data
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceABO.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceABO.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceABO.objects.all()
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
                    # print(mock_data)

        data = {
            "content": mock_data,
            "tableData": tableData,
            "selectIntfCtgry": selectIntfCtgry,
            "selectItem": selectItem,
            "selectOption": selectOption,
            "formselectOption": formselectOption,
            "form1selectOption": form1selectOption,
            "sectionCustomer": sectionCustomer,
            "sectionPlant": sectionPlant,
            "sectionexpirdate": sectionexpirdate,
            "sectionBrwStatus": sectionBrwStatus,
            "sectionDevStatus": sectionDevStatus,
            "sectionPhase": sectionPhase,
            # "sectionStatus": sectionStatus,
            "sectionLNVST": sectionLNVST,
            # "sectionDeviceStatus": sectionDeviceStatus,
            "errMsg": errMsg,
            "errMsgNumber": errMsgNumber,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'DeviceABO/M_edit.html', locals())


