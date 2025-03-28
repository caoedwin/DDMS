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
def TestDeviceListLNV(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "DeviceLNV/M_upload"
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
        "Good", "Fixed", "Long", "Damaged", "Lost"
    ]

    sectionBrwStatus = [
        "驗收中", "可借用", "固定設備", "已借出", "歸還確認中", "預定確認中", "續借確認中"
    ]

    sectionPhase = [
        "NPI",
    ]
    sectionLNVST = ["Must", "Optional", "Similar"]

    for i in UserInfo.objects.filter(role__name="Device_LNV_Users").values('account', 'CNname').distinct().order_by('CNname'):
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
    allBrwStatus = [
        # "可借用", "已借出"
    ]
    allDevStatus = [
        # "Good", "Good"
    ]


    Lent = ''  # 已借出
    kejieyong = ''  # 可借用
    jieyongyuding = ''  # 預定確認中
    guihuanqueren = ''  # 歸還確認中
    errMsg = ''
    errMsgNumber = ''#新增弹框
    # print(DeviceLNV._meta.fields)
    # # print([f.name for f DeviceLNV._meta.fields])
    # iii=0
    # for i in DeviceLNV._meta.fields:
    #     print(i.name, type(i), i.get_internal_type())
        # iii+=1
    # print(iii)
    # print(DeviceLNV._meta.get_fields())
    # print(request.method)
    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if request.POST:
            # if request.POST.get('isGetData') == 'first':
            #     # mock_data
            #     mock_datalist = DeviceLNV.objects.all()
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
                DevCtgrysearch = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgrysearch).first()
                # print(DevCtgrysearch)
                Devproperties = request.POST.get('Devproperties')
                Devpropertiessearch = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties, DevCtgry_P=DevCtgrysearch).first()
                # print(Devpropertiessearch)
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devpropertiessearch).values('DevVendor').distinct().order_by('DevVendor'):#其实去不去重无所谓，都是唯一的
                    # print(i)
                    sizelist = []
                    if DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']):
                        for j in DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']).values('Devsize').distinct().order_by('Devsize'):#其实去不去重无所谓，都是唯一的
                            sizelist.append({"Devsize": j['Devsize']})
                    selectOption[i['DevVendor']] = sizelist
            if request.POST.get('isGetData') == 'InsertJiLian':
                IntfCtgry = request.POST.get('IntfCtgry')
                IntfCtgrysearch = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry = request.POST.get('DevCtgry')
                DevCtgrysearch = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgrysearch).first()
                # print(DevCtgrysearch)
                Devproperties = request.POST.get('Devproperties')
                Devpropertiessearch = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties, DevCtgry_P=DevCtgrysearch).first()
                # print(Devpropertiessearch)
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devpropertiessearch).values('DevVendor').distinct().order_by('DevVendor'):#其实去不去重无所谓，都是唯一的
                    # print(i)
                    sizelist = []
                    if DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']):
                        for j in DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']).values('Devsize').distinct().order_by('Devsize'):#其实去不去重无所谓，都是唯一的
                            sizelist.append({"Devsize": j['Devsize']})
                    formselectOption[i['DevVendor']] = sizelist
                # print(formselectOption)
            if request.POST.get('isGetData') == 'UpdateJiLian':
                IntfCtgry = request.POST.get('IntfCtgry')
                IntfCtgrysearch = DeviceIntfCtgryList.objects.filter(IntfCtgry=IntfCtgry).first()
                DevCtgry = request.POST.get('DevCtgry')
                DevCtgrysearch = DeviceDevCtgryList.objects.filter(DevCtgry=DevCtgry, IntfCtgry_P=IntfCtgrysearch).first()
                # print(DevCtgrysearch)
                Devproperties = request.POST.get('Devproperties')
                Devpropertiessearch = DeviceDevpropertiesList.objects.filter(Devproperties=Devproperties, DevCtgry_P=DevCtgrysearch).first()
                # print(Devpropertiessearch)
                for i in DeviceDevVendorList.objects.filter(Devproperties_P=Devpropertiessearch).values('DevVendor').distinct().order_by('DevVendor'):#其实去不去重无所谓，都是唯一的
                    # print(i)
                    sizelist = []
                    if DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']):
                        for j in DeviceDevsizeList.objects.filter(DevVendor_P__DevVendor=i['DevVendor']).values('Devsize').distinct().order_by('Devsize'):#其实去不去重无所谓，都是唯一的
                            sizelist.append({"Devsize": j['Devsize']})
                    form1selectOption[i['DevVendor']] = sizelist


            if request.POST.get('isGetData') == 'SEARCH':
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
                BrwStatus = request.POST.get('Brwstatus')
                if BrwStatus and BrwStatus != "All":
                    checkAdaPow['BrwStatus'] = BrwStatus
                DevStatus = request.POST.get('DevStatus')
                if DevStatus and DevStatus != "All":
                    checkAdaPow['DevStatus'] = DevStatus

                # mock_data
                if IntfCtgry and IntfCtgry != "All" and Devproperties and Devproperties != "All":
                    mock_datalist = DeviceLNV.objects.filter(
                        Q(IntfCtgry__icontains=IntfCtgry) & Q(Devproperties__icontains=Devproperties))
                elif IntfCtgry and IntfCtgry != "All" and (not Devproperties or Devproperties == "All"):
                    mock_datalist = DeviceLNV.objects.filter(
                        Q(IntfCtgry__icontains=IntfCtgry))
                elif (not IntfCtgry or IntfCtgry == "All") and (Devproperties and Devproperties != "All"):
                    mock_datalist = DeviceLNV.objects.filter(
                        Q(Devproperties__icontains=Devproperties))
                else:
                    mock_datalist = DeviceLNV.objects.all()
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                    mock_datalist = mock_datalist.filter(**checkAdaPow)
                # print(mock_datalist)
                for i in mock_datalist:
                    # Photolist = []
                    # for h in i.Photo.all():
                    #     Photolist.append(
                    #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    EOLflag = 0
                    if i.EOL:
                        # print(i.EOL,datetime.datetime.now().date())
                        if datetime.datetime.now().date() < i.EOL:
                            flag_days = round(
                                float(
                                    str((i.EOL - datetime.datetime.now().date())).split(' ')[
                                        0]),
                                0)
                            # print(flag_days)
                            if flag_days <= 7:
                                EOLflag = 1
                        else:
                            EOLflag = 1
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
                    EOL_str = ''
                    if i.addnewdate:
                        EOL_str = str(i.EOL)
                    else:
                        EOL_str = ''
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
                         "addnewname": i.addnewname, "addnewdate": addnewdate_str, "EOL": EOL_str, "EOLflag": EOLflag,
                         "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                         "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                         "Usrname": i.Usrname, 'Usrnumber': i.BR_per_code,
                         "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str, "Rtime": Rtime_str,
                         "Overday": Exceed_days},
                    )
                # checkAdaPow = {}
                # IntfCtgry = request.POST.get('IntfCtgry')
                # if IntfCtgry and IntfCtgry != "All":
                #     checkAdaPow['IntfCtgry'] = IntfCtgry
                # DevCtgry = request.POST.get('DevCtgry')
                # if DevCtgry and DevCtgry != "All":
                #     checkAdaPow['DevCtgry'] = DevCtgry
                # Devproperties = request.POST.get('Devproperties')
                # if Devproperties and Devproperties != "All":
                #     checkAdaPow['Devproperties'] = Devproperties
                # DevVendor = request.POST.get('DevVendor')
                # if DevVendor and DevVendor != "All":
                #     checkAdaPow['DevVendor'] = DevVendor
                # Devsize = request.POST.get('Devsize')
                # if Devsize and Devsize != "All":
                #     checkAdaPow['Devsize'] = Devsize
                # BrwStatus = request.POST.get('DevStatus')
                # if BrwStatus and BrwStatus != "All":
                #     checkAdaPow['BrwStatus'] = BrwStatus
                # # mock_data
                # if checkAdaPow:
                #     # print(checkAdaPow)
                #     # mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                #     if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                #         mock_datalist = DeviceLNV.objects.filter(Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry'])&Q(DevCtgry=checkAdaPow['DevCtgry'])
                #                                                    &Q(Devproperties__icontains=checkAdaPow['Devproperties'])&Q(DevVendor=checkAdaPow['DevVendor'])
                #                                                  & Q(Devsize=checkAdaPow['Devsize']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                #         mock_datalist = DeviceLNV.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                #                 DevVendor=checkAdaPow['DevVendor']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                #         mock_datalist = DeviceLNV.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                #             & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                #     elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceLNV.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                #     elif "IntfCtgry" in checkAdaPow.keys():
                #         mock_datalist = DeviceLNV.objects.filter(
                #             Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                # else:
                #     mock_datalist = DeviceLNV.objects.all()
                # # print(mock_datalist)
                # for i in mock_datalist:
                #     # Photolist = []
                #     # for h in i.Photo.all():
                #     #     Photolist.append(
                #     #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                #     if i.Plandate and i.Btime and not i.Rtime:
                #         if datetime.datetime.now().date() > i.Plandate:
                #             Exceed_days = round(
                #                 float(
                #                     str((datetime.datetime.now().date() - i.Plandate)).split(' ')[
                #                         0]),
                #                 0)
                #         else:
                #             Exceed_days = ''
                #         if datetime.datetime.now().date() > i.Btime:
                #             usedays = round(
                #                 float(
                #                     str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                #                         0]),
                #                 0)
                #         else:
                #             usedays = ''
                #     else:
                #         usedays = ''
                #         Exceed_days = ''
                #     Useyears = ''
                #     if i.Pchsdate:
                #         if datetime.datetime.now().date() > i.Pchsdate:
                #             Useyears = round(
                #                 float(
                #                     str((datetime.datetime.now().date() - i.Pchsdate)).split(' ')[
                #                         0]) / 365,
                #                 1)
                #     addnewdate_str = ''
                #     if i.addnewdate:
                #         addnewdate_str = str(i.addnewdate)
                #     else:
                #         addnewdate_str = ''
                #     Pchsdate_str = ''
                #     if i.Pchsdate:
                #         Pchsdate_str = str(i.Pchsdate)
                #     else:
                #         Pchsdate_str = ''
                #     Plandate_str = ''
                #     if i.Plandate:
                #         Plandate_str = str(i.Plandate)
                #     else:
                #         Plandate_str = ''
                #     Btime_str = ''
                #     if i.Btime:
                #         Btime_str = str(i.Btime)
                #     else:
                #         Btime_str = ''
                #     Rtime_str = ''
                #     if i.Rtime:
                #         Rtime_str = str(i.Rtime)
                #     else:
                #         Rtime_str = ''
                #
                #     mock_data.append(
                #         {"id": i.id, "Customer": i.Customer, "Plant": i.Plant,
                #          "NID": i.NID, "DevID": i.DevID, "IntfCtgry": i.IntfCtgry,
                #          "DevCtgry": i.DevCtgry, "Devproperties": i.Devproperties, "DevVendor": i.DevVendor,
                #          "Devsize": i.Devsize, "DevModel": i.DevModel,
                #          "DevName": i.DevName,
                #          "HWVer": i.HWVer, "FWVer": i.FWVer, "DevDescription": i.DevDescription,
                #          "PckgIncludes": i.PckgIncludes,
                #          "expirdate": i.expirdate, "DevPrice": i.DevPrice, "Source": i.Source,
                #          "Pchsdate": Pchsdate_str,
                #          "PN": i.PN,
                #          "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo, "Declaration_NO": i.DeclarationNo,
                #          "AssetNum": i.AssetNum, "UsYear": Useyears,
                #          "addnewname": i.addnewname, "addnewdate": addnewdate_str,
                #          "Comment": i.Comment, "uscyc": i.uscyc, "UsrTimes": i.UsrTimes,
                #          "DevStatus": i.DevStatus, "BrwStatus": i.BrwStatus,
                #          "Usrname": i.Usrname,  'Usrnumber': i.BR_per_code,
                #          "Plandate": Plandate_str, "useday": usedays, "Btime": Btime_str, "Rtime": Rtime_str,
                #          "Overday": Exceed_days},
                #     )
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
                EOL = request.POST.get('EOL')
                if not EOL or EOL == 'null' or EOL == 'None':
                    EOL = None  # 日期爲空
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
                    "addnewname": addnewname, "addnewdate": addnewdate, "EOL": EOL,
                    "Comment": Comment, "uscyc": uscyc, "UsrTimes": UsrTimes,
                    "DevStatus": DevStatus, "BrwStatus": BrwStatus,
                    "Usrname": Usrname, "BR_per_code": BR_per_code,
                    "Plandate": Plandate, "Btime": Btime,
                    "Rtime": Rtime,
                             }
                # print(createdic)
                if DeviceLNV.objects.filter(NID=NID):
                    errMsgNumber = """設備序號已存在"""
                else:
                    # print(createdic)
                    DeviceLNV.objects.create(**createdic)
                    # print(Photo)
                    # if Photo:
                    #     for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                    #         # print(f)
                    #         empt = PICS()
                    #         # 增加其他字段应分别对应填写
                    #         empt.single = f
                    #         empt.pic = f
                    #         empt.save()
                    #         DeviceLNV.objects.filter(Number=Number).first().Photo.add(empt)

                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceLNV.objects.all()
                # print(mock_datalist)
                for i in mock_datalist:
                    # Photolist = []
                    # for h in i.Photo.all():
                    #     Photolist.append(
                    #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    EOLflag = 0
                    if i.EOL:
                        # print(i.EOL,datetime.datetime.now().date())
                        if datetime.datetime.now().date() < i.EOL:
                            flag_days = round(
                                float(
                                    str((i.EOL - datetime.datetime.now().date())).split(' ')[
                                        0]),
                                0)
                            # print(flag_days)
                            if flag_days <= 7:
                                EOLflag = 1
                        else:
                            EOLflag = 1
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
                    EOL_str = ''
                    if i.addnewdate:
                        EOL_str = str(i.EOL)
                    else:
                        EOL_str = ''
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
                         "addnewname": i.addnewname, "addnewdate": addnewdate_str, "EOL": EOL_str, "EOLflag": EOLflag,
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
                EOL = request.POST.get('EOL')
                if not EOL or EOL == 'null' or EOL == 'None':
                    EOL = None  # 日期爲空
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
                    "addnewname": addnewname, "addnewdate": addnewdate, "EOL": EOL,
                    "Comment": Comment, "uscyc": uscyc, "UsrTimes": UsrTimes,
                    "DevStatus": DevStatus, "BrwStatus": BrwStatus,
                    "Usrname": Usrname, "BR_per_code": BR_per_code,
                    "Plandate": Plandate, "Btime": Btime,
                    "Rtime": Rtime,
                }
                # if DeviceLNV.objects.filter(Number=Number):
                #     errMsgNumber = """编号已存在"""
                # else:
                # print(updatedic)
                try:
                    with transaction.atomic():
                        DeviceLNV.objects.filter(id=id).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % id
                # print(Photo)
                # if Photo:
                #     for m in DeviceLNV.objects.filter(id=id).first().Photo.all():  # 每次接受图片前清除原来的图片，而不是叠加
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
                #         DeviceLNV.objects.filter(id=id).first().Photo.add(empt)


                # mock_data
                if checkAdaPow:
                    # print(checkAdaPow)
                    # mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                    if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor'])
                            & Q(Devsize=checkAdaPow['Devsize']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                DevVendor=checkAdaPow['DevVendor']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                            & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                    elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                    elif "IntfCtgry" in checkAdaPow.keys():
                        mock_datalist = DeviceLNV.objects.filter(
                            Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                    else:
                        mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = DeviceLNV.objects.all()
                # print(mock_datalist)
                for i in mock_datalist:
                    # Photolist = []
                    # for h in i.Photo.all():
                    #     Photolist.append(
                    #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    EOLflag = 0
                    if i.EOL:
                        # print(i.EOL,datetime.datetime.now().date())
                        if datetime.datetime.now().date() < i.EOL:
                            flag_days = round(
                                float(
                                    str((i.EOL - datetime.datetime.now().date())).split(' ')[
                                        0]),
                                0)
                            # print(flag_days)
                            if flag_days <= 7:
                                EOLflag = 1
                        else:
                            EOLflag = 1
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
                    EOL_str = ''
                    if i.addnewdate:
                        EOL_str = str(i.EOL)
                    else:
                        EOL_str = ''
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
                         "addnewname": i.addnewname, "addnewdate": addnewdate_str, "EOL": EOL_str, "EOLflag": EOLflag,
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
                if DeviceLNVHis.objects.filter(NID=NID):
                    for i in DeviceLNVHis.objects.filter(NID=NID):
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
                        DeviceLNV.objects.get(id=i).delete()

                    # mock_data
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                        else:
                            mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = DeviceLNV.objects.all()
                    for i in mock_datalist:
                        # Photolist = []
                        # for h in i.Photo.all():
                        #     Photolist.append(
                        #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        EOLflag = 0
                        if i.EOL:
                            # print(i.EOL,datetime.datetime.now().date())
                            if datetime.datetime.now().date() < i.EOL:
                                flag_days = round(
                                    float(
                                        str((i.EOL - datetime.datetime.now().date())).split(' ')[
                                            0]),
                                    0)
                                # print(flag_days)
                                if flag_days <= 7:
                                    EOLflag = 1
                            else:
                                EOLflag = 1
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
                        EOL_str = ''
                        if i.addnewdate:
                            EOL_str = str(i.EOL)
                        else:
                            EOL_str = ''
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
                             "addnewname": i.addnewname, "addnewdate": addnewdate_str, "EOL": EOL_str, "EOLflag": EOLflag,
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
                        # print(type(i),i)
                        rownum += 1
                        # print(rownum)
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
                            if type(modeldata['Pchsdate']) != 'int' and len(modeldata['Pchsdate']) >= 8 and len(modeldata['Pchsdate']) <= 10:
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
                            if type(modeldata['Pchsdate']) != 'int' and len(modeldata['addnewdate']) >= 8 and len(modeldata['addnewdate']) <= 10:
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
                        if 'EOL' in modeldata.keys():
                            # modeldata['Pchsdate'] = modeldata['Pchsdate'].replace('/', '-')
                            # print(len(modeldata['Pchsdate'].split('-')))
                            # print(len(modeldata['EOL']))
                            if type(modeldata['Pchsdate']) != 'int' and len(modeldata['EOL']) >= 8 and len(modeldata['EOL']) <= 10:
                                modeldata['EOL'] = modeldata['EOL'].replace('/', '-')
                                modeldata['EOL'] = modeldata['EOL'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，EOL日期格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['EOL'] = None  # 日期爲空
                        if 'Plandate' in modeldata.keys():
                            if type(modeldata['Pchsdate']) != 'int' and len(modeldata['Plandate']) >= 8 and len(modeldata['Plandate']) <= 10:
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
                            if type(modeldata['Pchsdate']) != 'int' and len(modeldata['Btime']) >= 8 and len(modeldata['Btime']) <= 10:
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
                            if type(modeldata['Pchsdate']) != 'int' and len(modeldata['Rtime']) >= 8 and len(modeldata['Rtime']) <= 10:
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
                    #让数据可以从有值更新为无值
                    DevieModelfiedlist = []
                    for i in DeviceLNV._meta.fields:
                        if i.name != 'id':
                            DevieModelfiedlist.append([i.name,i.get_internal_type()])
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
                            if DeviceLNV.objects.filter(**Check_dic):#已经存在覆盖
                                # pass
                                DeviceLNV.objects.filter(
                                    **Check_dic).update(**i)
                            else:#新增
                                DeviceLNV.objects.create(**i)
                        errMsg = '上傳成功'

                    # mock_data
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                        if "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys() and "Devsize" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor'])
                                & Q(Devsize=checkAdaPow['Devsize']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys() and "DevVendor" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']) & Q(
                                    DevVendor=checkAdaPow['DevVendor']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys() and "Devproperties" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry'])
                                & Q(Devproperties__icontains=checkAdaPow['Devproperties']))
                        elif "IntfCtgry" in checkAdaPow.keys() and "DevCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']) & Q(DevCtgry=checkAdaPow['DevCtgry']))
                        elif "IntfCtgry" in checkAdaPow.keys():
                            mock_datalist = DeviceLNV.objects.filter(
                                Q(IntfCtgry__icontains=checkAdaPow['IntfCtgry']))
                        else:
                            mock_datalist = DeviceLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = DeviceLNV.objects.all()
                    for i in mock_datalist:
                        # Photolist = []
                        # for h in i.Photo.all():
                        #     Photolist.append(
                        #         {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        EOLflag = 0
                        if i.EOL:
                            # print(i.EOL,datetime.datetime.now().date())
                            if datetime.datetime.now().date() < i.EOL:
                                flag_days = round(
                                    float(
                                        str((i.EOL - datetime.datetime.now().date())).split(' ')[
                                            0]),
                                    0)
                                # print(flag_days)
                                if flag_days <= 7:
                                    EOLflag = 1
                            else:
                                EOLflag = 1
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
                        EOL_str = ''
                        if i.addnewdate:
                            EOL_str = str(i.EOL)
                        else:
                            EOL_str = ''
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
                             "HWVer": i.HWVer, "FWVer": i.FWVer, "DevDescription": i.DevDescription, "PckgIncludes": i.PckgIncludes,
                             "expirdate": i.expirdate, "DevPrice": i.DevPrice, "Source": i.Source, "Pchsdate": Pchsdate_str,
                             "PN": i.PN,
                             "LNV_ST": i.LSTA, "Purchase_NO": i.ApplicationNo, "Declaration_NO": i.DeclarationNo,
                             "AssetNum": i.AssetNum, "UsYear": Useyears,
                             "addnewname": i.addnewname, "addnewdate": addnewdate_str, "EOL": EOL_str, "EOLflag": EOLflag,
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

            "allIntfCtgry": allIntfCtgry,
            "allDevCtgry": allDevCtgry,
            "allDevproperties": allDevproperties,
            "allDevVendor": allDevVendor,
            "allDevsize": allDevsize,
            "allDevStatus": allDevStatus,
            "allBrwStatus": allBrwStatus,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'TestDeviceLNV/TestDeviceListLNV.html', locals())


