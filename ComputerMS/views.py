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
from .models import ComputerLNV, ComputerLNVHis
from app01.models import UserInfo

headermodel_Computer = {
    '統一編號': 'NID',
    'MaterialPN': 'MaterialPN',
    'CPU': 'CPU', 'RAM': 'RAM', 'HDD': 'HDD', 'Wireless': 'Wireless',
    'LCD': 'LCD', 'OCR': 'OCR', 'Battery': 'Battery', 'Adaptor': 'Adaptor',
    '地區': 'Area', '攜出廠外': 'Carryif', '廠區': 'Plant', '電腦用途': 'Purpose', '產品類別': 'Category',
    '工作機狀態': 'BrwStatus', '閒置狀態': 'IdleStatus', 'E-Form單號': 'EFormNo', '姓名': 'Usrname', '工號': 'BR_per_code',
    # '使用天數': 'useday',
    '領用日期': 'Btime', '歸還日期': 'Rtime', #'備註': 'Comment', #"超期天數": "Overday"实时计算出来的


    '上一任使用人姓名': 'Last_BR_per', '上一任使用人工號': 'Last_BR_per_code',
    '上一次領用日期': 'Last_Borrow_date', '上一次歸還日期': 'Last_Return_date',
    '接收人員工號': 'Receive_per_code', '簽核人員工號': 'Sign_per_code',
}

@csrf_exempt
def BorrowedComputer(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/BorrowedDevice"
    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]

    selectUnifiedNumber = [
        # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
    ]
    for i in ComputerLNV.objects.all().values("NID").order_by("NID"):
        selectUnifiedNumber.append({"value": i["NID"]})

    allMachineStatus = [

    ]
    for i in ComputerLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
        allMachineStatus.append(i["BrwStatus"])

    errMessage = ""
    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            NID = request.POST.get('UnifiedNumber')
            BrwStatus = request.POST.get('MachineStatus')
            BR_per_code = request.POST.get('Number')
            check_dic = {}
            if NID:
                check_dic["NID"] = NID
            if BrwStatus:
                check_dic["BrwStatus"] = BrwStatus
            if BR_per_code:
                check_dic["BR_per_code"] = BR_per_code

            if check_dic:
                mock_datalist = ComputerLNV.objects.filter(**check_dic)
            else:
                mock_datalist = ComputerLNV.objects.all()
            for i in mock_datalist:

                Years = ''
                Btime_str = ''
                if i.Btime:
                    Btime_str = str(i.Btime)
                    if datetime.datetime.now().date() > i.Btime:
                        Years = round(
                            float(
                                str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                    0]) / 365,
                            2)
                Rtime_str = ''
                if i.Rtime:
                    Rtime_str = str(i.Rtime)
                else:
                    Rtime_str = ''
                Last_Borrow_date_str = ''
                if i.Last_Borrow_date:
                    Last_Borrow_date_str = str(i.Last_Borrow_date)
                else:
                    Last_Borrow_date_str = ''
                Last_Return_date_str = ''
                if i.Last_Return_date:
                    Last_Return_date_str = str(i.Last_Return_date)
                else:
                    Last_Return_date_str = ''

                mock_data.append(
                    {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                     "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                     "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                     "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                     "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                     "MachineStatus": i.BrwStatus,
                     "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                )

        if 'SEARCH' in str(request.body):
            NID = request.POST.get('UnifiedNumber')
            BrwStatus = request.POST.get('MachineStatus')
            BR_per_code = request.POST.get('Number')
            check_dic = {}
            if NID:
                check_dic["NID"] = NID
            if BrwStatus:
                check_dic["BrwStatus"] = BrwStatus
            if BR_per_code:
                check_dic["BR_per_code"] = BR_per_code

            if check_dic:
                mock_datalist = ComputerLNV.objects.filter(**check_dic)
            else:
                mock_datalist = ComputerLNV.objects.all()
            for i in mock_datalist:

                Years = ''
                Btime_str = ''
                if i.Btime:
                    Btime_str = str(i.Btime)
                    if datetime.datetime.now().date() > i.Btime:
                        Years = round(
                            float(
                                str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                    0]) / 365,
                            2)
                Rtime_str = ''
                if i.Rtime:
                    Rtime_str = str(i.Rtime)
                else:
                    Rtime_str = ''
                Last_Borrow_date_str = ''
                if i.Last_Borrow_date:
                    Last_Borrow_date_str = str(i.Last_Borrow_date)
                else:
                    Last_Borrow_date_str = ''
                Last_Return_date_str = ''
                if i.Last_Return_date:
                    Last_Return_date_str = str(i.Last_Return_date)
                else:
                    Last_Return_date_str = ''

                mock_data.append(
                    {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                     "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                     "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                     "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                     "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                     "MachineStatus": i.BrwStatus,
                     "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                )
        if 'EnsureInfo' in str(request.body):
            # print(1)
            NID = request.POST.get('UnifiedNumber')
            BrwStatus = request.POST.get('MachineStatus')
            BR_per_code = request.POST.get('Number')


            BorrowedID = request.POST.get('ID')
            # print(BorrowedID, type(BorrowedID),NID)
            # print(json.loads(BorrowedID))
            # print(BorrowedID.split(','))
            updatedic = {
                # 'ProjectCode': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                         'BrwStatus': '申請確認中', 'Usrname': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'),
                         # 'Plandate': request.POST.get('Predict_return'),
                'Btime': None, 'Rtime': None,
            }
            # print(updatedic)
            for i in BorrowedID.split(','):
                # print(i)
                try:
                    with transaction.atomic():
                        # print(updatedic)
                        ComputerLNV.objects.filter(id=i).update(**updatedic)
                        # alert = 0
                except:
                    # print('2')
                    alert = '此数据%s正被其他使用者编辑中...' % i
                    errMessage = '此数据%s正被其他使用者编辑中...' % i

            # mock_data
            check_dic = {}
            if NID:
                check_dic["NID"] = NID
            if BrwStatus:
                check_dic["BrwStatus"] = BrwStatus
            if BR_per_code:
                check_dic["BR_per_code"] = BR_per_code

            if check_dic:
                mock_datalist = ComputerLNV.objects.filter(**check_dic)
            else:
                mock_datalist = ComputerLNV.objects.all()
            for i in mock_datalist:

                Years = ''
                Btime_str = ''
                if i.Btime:
                    Btime_str = str(i.Btime)
                    if datetime.datetime.now().date() > i.Btime:
                        Years = round(
                            float(
                                str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                    0]) / 365,
                            2)
                Rtime_str = ''
                if i.Rtime:
                    Rtime_str = str(i.Rtime)
                else:
                    Rtime_str = ''
                Last_Borrow_date_str = ''
                if i.Last_Borrow_date:
                    Last_Borrow_date_str = str(i.Last_Borrow_date)
                else:
                    Last_Borrow_date_str = ''
                Last_Return_date_str = ''
                if i.Last_Return_date:
                    Last_Return_date_str = str(i.Last_Return_date)
                else:
                    Last_Return_date_str = ''

                mock_data.append(
                    {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                     "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                     "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                     "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                     "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                     "MachineStatus": i.BrwStatus,
                     "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                )
        data = {
            "content": mock_data,
            "selectUnifiedNumber": selectUnifiedNumber,
            "allMachineStatus": allMachineStatus,
            "errMessage": errMessage,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/BorrowedComputer.html', locals())


@csrf_exempt
def R_Borrowed(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/R_Borrowed"
    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]

    selectUnifiedNumber = [
        # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
    ]
    for i in ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
        BR_per_code=request.session.get('account_DMS'), BrwStatus__in=['使用中', '閑置中']).values("NID").distinct().order_by("NID"):
        selectUnifiedNumber.append({"value": i["NID"]})
    #
    selectNumber = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        if i["account"] != request.session.get('account_DMS'):
            selectNumber.append({"value": i["account"], "number": i["CNname"]})
    #既然是转账，就无需转给自己
    # del selectNumber['语文']
    #
    # allMachineStatus = ["使用中", "閑置中"]


    # if ComputerLNV.objects.all():
    #     for i in ComputerLNV.objects.values("BrwStatus").distinct().order_by("BrwStatus"):
    #         allDevStatus.append(i["BrwStatus"])

    errMessage = ""

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                         BR_per_code=request.session.get('account_DMS'), BrwStatus__in=['使用中', '閑置中'])
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('isGetData') == 'SEARCH':
                UnifiedNumber = request.POST.get('UnifiedNumber')
                check_dic = {}
                if UnifiedNumber:
                    check_dic["NID"] = UnifiedNumber

                if check_dic:
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                         BR_per_code=request.session.get('account_DMS'), BrwStatus__in=['使用中', '閑置中']).filter(**check_dic)
                else:
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                         BR_per_code=request.session.get('account_DMS'), BrwStatus__in=['使用中', '閑置中'])
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('isGetData') == 'Scrap':
                updatedic = {'BrwStatus': '歸還確認中',
                             # 'BR_per': request.session.get('CNname'),
                             # 'Predict_return': None,
                             # 'Borrow_date': None,'Return_date': None,
                             }

                try:
                    with transaction.atomic():
                        ComputerLNV.objects.filter(id=request.POST.get('ID')).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % request.POST.get('ID')

                UnifiedNumber = request.POST.get('UnifiedNumber')
                check_dic = {}
                if UnifiedNumber:
                    check_dic["NID"] = UnifiedNumber

                if check_dic:
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus__in=['使用中', '閑置中']).filter(**check_dic)
                else:
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus__in=['使用中', '閑置中'])
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('isGetData') == 'Transfer':
                Receive_per_code = request.POST.get('Number')
                EFormNo = request.POST.get('FormNumber')
                updatedic = {'BrwStatus': '轉帳確認中',
                             # 'BR_per': request.session.get('CNname'),
                             # 'Predict_return': None,
                             # 'Borrow_date': None,'Return_date': None,
                             'Transefer_per_code': ComputerLNV.objects.filter(id=request.POST.get('ID')).first().BR_per_code,
                             'Receive_per_code': Receive_per_code,
                             'EFormNo': EFormNo,
                             'Btime': None, 'Rtime': None,
                             }
                print(updatedic)

                try:
                    with transaction.atomic():
                        ComputerLNV.objects.filter(id=request.POST.get('ID')).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % request.POST.get('ID')

                UnifiedNumber = request.POST.get('UnifiedNumber')
                check_dic = {}
                if UnifiedNumber:
                    check_dic["NID"] = UnifiedNumber

                if check_dic:
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus__in=['使用中', '閑置中']).filter(**check_dic)
                else:
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus__in=['使用中', '閑置中'])
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i


                    # mock_data
                    checkAdaPowfirst = {'Usrname': request.session.get('CNname_DMS'),
                                        'BR_per_code': request.session.get('account_DMS'), 'BrwStatus': '使用中'}
                    checkAdaPow = {}
                    IntfCtgry = responseData['IntfCtgry']
                    # if IntfCtgry and IntfCtgry != "All":
                    #     checkAdaPow['IntfCtgry'] = IntfCtgry
                    DevCtgry = responseData['DevCtgry']
                    if DevCtgry and DevCtgry != "All":
                        checkAdaPow['DevCtgry'] = DevCtgry
                    Devproperties = request.POST.get('Devproperties')
                    # if Devproperties and Devproperties != "All":
                    #     checkAdaPow['Devproperties'] = Devproperties
                    DevVendor = responseData['DevVendor']
                    if DevVendor and DevVendor != "All":
                        checkAdaPow['DevVendor'] = DevVendor
                    Devsize = responseData['Devsize']
                    if Devsize and Devsize != "All":
                        checkAdaPow['Devsize'] = Devsize

                    # mock_data
                    if IntfCtgry and IntfCtgry != "All" and Devproperties and Devproperties != "All":
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=IntfCtgry) & Q(Devproperties__icontains=Devproperties))
                    elif IntfCtgry and IntfCtgry != "All" and (not Devproperties or Devproperties == "All"):
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPowfirst).filter(
                            Q(IntfCtgry__icontains=IntfCtgry))
                    elif (not IntfCtgry or IntfCtgry == "All") and (Devproperties and Devproperties != "All"):
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPowfirst).filter(
                            Q(Devproperties__icontains=Devproperties))
                    else:
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPowfirst)
                    if checkAdaPow:
                        # print(checkAdaPow)
                        # mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
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
            "content": mock_data,
            "selectUnifiedNumber": selectUnifiedNumber,
            "selectNumber": selectNumber,
            # "allMachineStatus": allMachineStatus,
            "errMessage": errMessage,


        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/R_Borrowed.html', locals())

@csrf_exempt
def R_Return(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/R_Return"
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
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "閑置中", "Usrname": "單桂萍",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "2020-01-26", "Overday": ""},
    ]


    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'), BR_per_code=request.session.get('account_DMS'), BrwStatus='歸還確認中')
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                    updatedic = {'BrwStatus': '使用中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['Return']:
                        try:
                            with transaction.atomic():
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus='歸還確認中')
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
        data = {

            "content": mock_data,
            # "options": options

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/R_Return.html', locals())

@csrf_exempt
def R_Destine(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/R_Destine"
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
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "閑置中", "Usrname": "單桂萍",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "2020-01-26", "Overday": ""},
    ]

    if request.method == "POST":
        if request.POST:
            # print(request.body)
            if 'first' in str(request.body):
                # mock_data
                mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'), BR_per_code=request.session.get('account_DMS'), BrwStatus='申請確認中')
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                if 'CancelApply' in str(request.body):
                    # print(request.body)
                    responseData = json.loads(request.body)
                    # print(responseData)

                    updatedic = {'BrwStatus': '閑置中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Plandate': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['Apply']:
                        # print(i)
                        updatedic['Usrname'] = ComputerLNV.objects.filter(id=i).first().Last_BR_per
                        updatedic['BR_per_code'] = ComputerLNV.objects.filter(id=i).first().Last_BR_per_code
                        # updatedic['ProjectCode'] = ComputerLNV.objects.filter(id=i).first().Last_ProjectCode
                        # updatedic['Phase'] = ComputerLNV.objects.filter(id=i).first().Last_Phase
                        # updatedic['Predict_return'] = ComputerLNV.objects.filter(id=i).first().Last_Predict_return
                        updatedic['Btime'] = ComputerLNV.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Rtime'] = ComputerLNV.objects.filter(id=i).first().Last_Return_date
                        # print(updatedic)
                        try:
                            with transaction.atomic():
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus='申請確認中')
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
            # print(request.POST)

        data = {
            "content": mock_data,
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/R_Destine.html', locals())

@csrf_exempt
def R_Receive(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/R_Receive"
    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]

    selectOptions = ["待轉賬", "待退庫"]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '轉帳確認中', "Receive_per_code": request.session.get('account_DMS')}
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                         "Receive_per_code": i.Receive_per_code,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('action') == 'Accept':
                IdleStatus = request.POST.get('IdleState')
                ID = request.POST.get('ID')
                NID = request.POST.get('UnifiedNumber')
                linshi_BrwStatus = request.POST.get('MachineStatus')
                print(linshi_BrwStatus)
                updatedic = {'BrwStatus': '接收確認中',
                            'linshi_BrwStatus': linshi_BrwStatus,
                            'IdleStatus': IdleStatus,
                             # 'BR_per': request.session.get('CNname'),
                             # 'Predict_return': None,
                             # 'Borrow_date': None,'Return_date': None,

                             }
                try:
                    with transaction.atomic():
                        # print(1)
                        ComputerLNV.objects.filter(id=request.POST.get('ID')).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % request.POST.get('ID')
                # mock_data
                checkAdaPow = {'BrwStatus': '轉帳確認中', "Receive_per_code": request.session.get('account_DMS')}
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                         "Receive_per_code": i.Receive_per_code,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                pass
        data = {
            "content": mock_data,
            "selectOptions": selectOptions,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/R_Receive.html', locals())

@csrf_exempt
def R_Transfer(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/R_Transfer"
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
        #  "Comment": "", "uscyc": "100", "UsrTimes": "12", "DevStatus": "Good", "BrwStatus": "閑置中", "Usrname": "單桂萍",
        #  "Plandate": "2020-01-26", "useday": "1", "Btime": "2020-01-25", "Rtime": "2020-01-26", "Overday": ""},
    ]

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                         BR_per_code=request.session.get('account_DMS'), BrwStatus__in=["轉帳確認中", '接收確認中'])
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                if 'CancelTransfer' in str(request.body):

                    responseData = json.loads(request.body)

                    updatedic = {'BrwStatus': '使用中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 "Transefer_per_code": "",
                                 "Receive_per_code": ""
                                 }
                    for i in responseData['Transfer']:

                        updatedic['Btime'] = ComputerLNV.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Rtime'] = ComputerLNV.objects.filter(id=i).first().Last_Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    mock_datalist = ComputerLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus='轉帳確認中')
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                             "Transefer_per_code": i.Transefer_per_code,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
        data = {
            "content": mock_data,
            # "options": options

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/R_Transfer.html', locals())

@csrf_exempt
def M_Borrow(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/M_Borrow"

        # print(i)
    selectItem = [
        # {"value": "12345678", "number": "姚麗麗"}, {"value": "11111111", "number": "張亞萍"},
        # {"value": "20800413", "number": "錢剛"},
    ]
    for i in ComputerLNV.objects.filter(BrwStatus='申請確認中').values('Usrname', 'BR_per_code').distinct().order_by('BR_per_code'):
        selectItem.append({"value": i["BR_per_code"], "number": i["Usrname"]})
    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '申請確認中'}
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BrwStatus': '申請確認中'}
                if request.POST.get('Name'):
                    checkAdaPow['Usrname'] = request.POST.get('Name')
                    if request.POST.get('Number', None):
                        checkAdaPow['BR_per_code'] = request.POST.get('Number')
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
                # checkAdaPow = {'BrwStatus': '申請確認中'}
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                if 'ApplyConfirm' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BrwStatus': '申請確認中'}
                    if responseData['Name']:
                        checkAdaPow['Usrname'] = responseData['Name']
                    if "Number" in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['Number']

                    updatedic = {'BrwStatus': '使用中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }
                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)
                        updatedic['Last_BR_per'] = ComputerLNV.objects.filter(id=i).first().Usrname
                        updatedic['Last_BR_per_code'] = ComputerLNV.objects.filter(id=i).first().BR_per_code
                        # updatedic['Last_ProjectCode'] = ComputerLNV.objects.filter(id=i).first().ProjectCode
                        # updatedic['Last_Phase'] = ComputerLNV.objects.filter(id=i).first().Phase
                        # updatedic['Last_Predict_return'] = ComputerLNV.objects.filter(id=i).first().Plandate
                        updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = ComputerLNV.objects.filter(id=i).first().Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    # checkAdaPow = {'BrwStatus': '申請確認中'}
                    if checkAdaPow:
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = ComputerLNV.objects.all()
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
        data = {
            # "selectItem": selectItem,
            "content": mock_data,
            "select": selectItem,

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/M_Borrow.html', locals())

@csrf_exempt
def M_Return(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/R_Destine"
    selectItem = [
        # {"value": "12345678", "number": "姚麗麗"}, {"value": "11111111", "number": "張亞萍"},
        # {"value": "20800413", "number": "錢剛"},
    ]
    for i in ComputerLNV.objects.filter(BrwStatus='歸還確認中').values("BR_per_code", "Usrname").distinct():
        selectItem.append({"value": i["BR_per_code"], "number": i["Usrname"]})
    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                checkAdaPow = {'BrwStatus': '歸還確認中'}
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BrwStatus': '歸還確認中'}
                if request.POST.get('Name'):
                    checkAdaPow['Usrname'] = request.POST.get('Name')
                if request.POST.get('Number', None):
                    checkAdaPow['BR_per_code'] = request.POST.get('Number')

                # mock_data
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                if 'ReturnConfirm' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BrwStatus': '歸還確認中'}
                    if responseData['Name']:
                        checkAdaPow['Usrname'] = responseData['Name']
                    if 'Number' in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['Number']

                    updatedic = {
                                'BrwStatus': '已報廢',
                                # 'BrwStatus': '閑置中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': datetime.datetime.now().date(),
                                 'Rtime': datetime.datetime.now().date(),
                                 # "Last_uscyc": '',
                                 }

                    for i in responseData['params']:
                        # print(i)
                        # updatedic['Last_BR_per'] = ComputerLNV.objects.filter(id=i).first().BR_per
                        # updatedic['Last_Predict_return'] = ComputerLNV.objects.filter(id=i).first().Predict_return
                        # updatedic['Last_Borrow_date'] = datetime.datetime.now().date(),
                        updatedic['Last_Return_date'] = datetime.datetime.now().date()

                        # if ComputerLNV.objects.filter(id=i).first().uscyc:
                        #     uscyc = int(ComputerLNV.objects.filter(id=i).first().uscyc)
                        # else:
                        #     uscyc = 0
                        # if ComputerLNV.objects.filter(id=i).first().UsrTimes:
                        #     UsrTimes = int(ComputerLNV.objects.filter(id=i).first().UsrTimes)
                        # else:
                        #     UsrTimes = 0
                        # updatedic['uscyc'] = str(uscyc + int(ComputerLNV.objects.filter(id=i).first().Last_uscyc))
                        # updatedic['UsrTimes'] = str(UsrTimes + 1)

                        Devicebyid = ComputerLNV.objects.filter(id=i).first()
                        # print(Devicebyid)
                        updatedic_His = {
                            "NID": Devicebyid.NID, "EFormNo": Devicebyid.EFormNo,
                            "Area": Devicebyid.Area, "Carryif": Devicebyid.Carryif, "Plant": Devicebyid.Plant, "Purpose": Devicebyid.Purpose,
                            # "uscyc": ComputerLNV.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date,
                            # "Plandate": Devicebyid.Last_Predict_return,
                            "Rtime": datetime.datetime.now().date(),
                            "Usrname": Devicebyid.Last_BR_per, "BR_per_code": Devicebyid.Last_BR_per_code,
                            # "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            # "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }
                        updatedic_His_check = {
                            "NID": Devicebyid.NID, "EFormNo": Devicebyid.EFormNo,
                            "Area": Devicebyid.Area, "Carryif": Devicebyid.Carryif, "Plant": Devicebyid.Plant, "Purpose": Devicebyid.Purpose,
                            # "uscyc": ComputerLNV.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date,
                            # "Plandate": Devicebyid.Last_Predict_return,
                            # "Rtime": datetime.datetime.now().date(),#重新操作時，時間不一樣，不能以操作當下的時間作爲檢查條件
                            "Usrname": Devicebyid.Last_BR_per, "BR_per_code": Devicebyid.Last_BR_per_code,
                            # "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            # "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }
                        # print(updatedic_His_check)
                        try:
                            with transaction.atomic():
                                # print('1', ComputerLNVHis.objects.filter(**updatedic_His_check))
                                if ComputerLNVHis.objects.filter(**updatedic_His_check):
                                    # print("2")
                                    pass#防止历史记录存成功了，Device更新失败，需要重复操作。
                                else:
                                    # print("3")
                                    ComputerLNVHis.objects.create(**updatedic_His)
                                    # print(updatedic_His)
                                # print(updatedic)
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = ComputerLNV.objects.all()
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
        data = {
            "select": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/M_Return.html', locals())

@csrf_exempt
def M_Transfer(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/M_Keep"

    selectItem = [
        # {"value": "12345678", "number": "姚麗麗"}, {"value": "11111111", "number": "張亞萍"},
        # {"value": "20800413", "number": "錢剛"},
    ]
    for i in ComputerLNV.objects.filter(BrwStatus='接收確認中').values("BR_per_code", "Usrname").distinct():
        selectItem.append({"value": i["BR_per_code"], "number": i["Usrname"]})
    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '接收確認中'}
                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                         "Receive_per_code": i.Receive_per_code,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('isGetData') == 'SEARCH':
                # mock_data
                checkAdaPow = {'BrwStatus': '接收確認中'}
                if request.POST.get('Name'):
                    checkAdaPow['Usrname'] = request.POST.get('Name')
                if request.POST.get('Number', None):
                    checkAdaPow['BR_per_code'] = request.POST.get('Number')

                if checkAdaPow:
                    mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                         "Receive_per_code": i.Receive_per_code,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
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
                if 'TransferConfirm' in str(request.body):
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BrwStatus': '接收確認中'}
                    if responseData['Name']:
                        checkAdaPow['Usrname'] = responseData['Name']
                    if 'Number' in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['Number']

                    updatedic = {
                                'BrwStatus': '使用中',
                                'linshi_BrwStatus': '',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }

                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)
                        updatedic['Usrname'] = UserInfo.objects.filter(account=ComputerLNV.objects.filter(id=i).first().Receive_per_code).first().CNname
                        updatedic['BR_per_code'] = ComputerLNV.objects.filter(id=i).first().Receive_per_code
                        updatedic['BrwStatus'] = ComputerLNV.objects.filter(id=i).first().linshi_BrwStatus
                        # updatedic['ProjectCode'] = ComputerLNV.objects.filter(id=i).first().Last_ProjectCode
                        # updatedic['Phase'] = ComputerLNV.objects.filter(id=i).first().Last_Phase
                        # updatedic['Predict_return'] = ComputerLNV.objects.filter(id=i).first().Last_Predict_return
                        # updatedic['Last_BR_per'] = ComputerLNV.objects.filter(id=i).first().Usrname
                        # updatedic['Last_BR_per_code'] = ComputerLNV.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = ComputerLNV.objects.filter(id=i).first().Return_date

                        Devicebyid = ComputerLNV.objects.filter(id=i).first()
                        updatedic_His = {
                            "NID": Devicebyid.NID, "EFormNo": Devicebyid.EFormNo,
                            "Area": Devicebyid.Area, "Carryif": Devicebyid.Carryif, "Plant": Devicebyid.Plant,
                            "Purpose": Devicebyid.Purpose,
                            # "uscyc": ComputerLNV.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date,
                            # "Plandate": Devicebyid.Last_Predict_return,
                            "Rtime": datetime.datetime.now().date(),
                            "Usrname": Devicebyid.Usrname, "BR_per_code": Devicebyid.BR_per_code,
                            "Transefer_per_code": Devicebyid.Transefer_per_code, "Receive_per_code": Devicebyid.Receive_per_code,
                            # "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            # "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }
                        updatedic_His_check = {
                            "NID": Devicebyid.NID, "EFormNo": Devicebyid.EFormNo,
                            "Area": Devicebyid.Area, "Carryif": Devicebyid.Carryif, "Plant": Devicebyid.Plant,
                            "Purpose": Devicebyid.Purpose,
                            # "uscyc": ComputerLNV.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date,
                            # "Plandate": Devicebyid.Last_Predict_return,
                            # "Rtime": datetime.datetime.now().date(),#重新操作時，時間不一樣，不能以操作當下的時間作爲檢查條件
                            "Usrname": Devicebyid.Usrname, "BR_per_code": Devicebyid.BR_per_code,
                            "Transefer_per_code": Devicebyid.Transefer_per_code, "Receive_per_code": Devicebyid.Receive_per_code,
                            # "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            # "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }

                        try:
                            with transaction.atomic():
                                print(updatedic)
                                print(updatedic_His)
                                if ComputerLNVHis.objects.filter(**updatedic_His_check):
                                    pass#防止历史记录存成功了，Device更新失败，需要重复操作。
                                else:
                                    ComputerLNVHis.objects.create(**updatedic_His)
                                ComputerLNV.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = ComputerLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = ComputerLNV.objects.all()
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                             "Receive_per_code": i.Receive_per_code,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
        data = {
            "select": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/M_Transfer.html', locals())

@csrf_exempt
def M_edit(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ComputerLNV/M_upload"

    mock_data = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "Number": "0301507", "Name": "劉鑫", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "2", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027576",
        #  "Number": "C140QUN", "Name": "孫永浪", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
        # {"id": "3", "CollectDate": "2019-2-11", "UnifiedNumber": "GI031837",
        #  "Number": "20800848", "Name": "張柯", "MaterialPN": "ELZP3010009",
        #  "CPU": "1.8G", "RAM": "8G", "HDD": "512G", "Wireless": "Y", "LCD": "13.3", "OCR": "Y",
        #  "Battery": "Y", "Adaptor": "Y", "Region": "TF01", "Factory": "M",
        #  "OutPlant": "Y", "ComputerUse": "個人辦公", "Category": "NB", "MachineStatus": "使用中",
        #  "IdleState": "", "Years": "", "FormNumber": "2443389"},
    ]

    selectUnifiedNumber = [
        # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
    ]
    for i in ComputerLNV.objects.all().values("NID").order_by("NID"):
        selectUnifiedNumber.append({"value": i["NID"]})

    selectNumber = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    # for i in ComputerLNV.objects.all().values("Usrname", "BR_per_code").distinct().order_by("BR_per_code"):
    #     selectNumber.append({"value": i["Usrname"], "number": i["BR_per_code"]})
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        selectNumber.append({"value": i["account"], "number": i["CNname"]})

    # 歷史記錄
    tableData = [
        # {
        #     "id": "1", "UnifiedNumber": "GI031825", "Number": "20800848", "Name": "張柯",
        #     "CollectDate": "2019-2-11", "ReturnDate": "2020-2-11"
        # },
    ]

    allMachineStatus = [
        "使用中",
        "閑置中", "已報廢", "申請確認中", "歸還確認中", "轉帳確認中", "接收確認中",
        # "申請中", "歸還中", "轉帳中",
    ]


    sectionIdleState = [
        "待轉賬", "待退庫"
    ]


    errMsg = ''
    errMsgNumber = ''  # 新增弹框



    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if request.POST:
            # if request.POST.get('isGetData') == 'first':
            #     # mock_data
            #     mock_datalist = ComputerLNV.objects.all()
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
            if request.POST.get('isGetData') == "SEARCH":
                NID = request.POST.get('UnifiedNumber')
                BrwStatus = request.POST.get('MachineStatus')
                BR_per_code = request.POST.get('Number')
                check_dic = {}
                if NID:
                    check_dic["NID"] = NID
                if BrwStatus:
                    check_dic["BrwStatus"] = BrwStatus
                if BR_per_code:
                    check_dic["BR_per_code"] = BR_per_code

                if check_dic:
                    mock_datalist = ComputerLNV.objects.filter(**check_dic)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0])/365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category, "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
            if request.POST.get('action') == "addSubmit":
                Btime = request.POST.get('CollectDate')
                if not Btime or Btime == 'null':
                    Btime = None  # 日期爲空
                NID = request.POST.get('UnifiedNumber')
                BR_per_code = request.POST.get('Number')
                Usrname = request.POST.get('Name')
                MaterialPN = request.POST.get('MaterialPN')
                CPU = request.POST.get('CPU')
                RAM = request.POST.get('RAM')
                HDD = request.POST.get('HDD')
                Wireless = request.POST.get('Wireless')
                LCD = request.POST.get('LCD')
                OCR = request.POST.get('OCR')
                Battery = request.POST.get('Battery')
                Adaptor = request.POST.get('Adaptor')
                Area = request.POST.get('Region')
                Plant = request.POST.get('Factory')
                Carryif = request.POST.get('OutPlant')
                Purpose = request.POST.get('ComputerUse')
                Category = request.POST.get('Category')
                BrwStatus = request.POST.get('MachineStatus')
                IdleStatus = request.POST.get('IdleState')
                EFormNo = request.POST.get('FormNumber')
                createdic = {
                    "Btime": Btime, "NID": NID,
                    "BR_per_code": BR_per_code, "Usrname": Usrname, "MaterialPN": MaterialPN,
                    "CPU": CPU, "RAM": RAM, "HDD": HDD,
                    "Wireless": Wireless, "LCD": LCD,
                    "OCR": OCR,
                    "Battery": Battery, "Adaptor": Adaptor, "Area": Area,
                    "Plant": Plant,
                    "Carryif": Carryif, "Purpose": Purpose, "Category": Category,
                    "BrwStatus": BrwStatus,
                    "IdleStatus": IdleStatus,
                    "EFormNo": EFormNo,
                             }
                # print(createdic)
                if ComputerLNV.objects.filter(NID=NID):
                    errMsgNumber = """統一編號已存在"""
                else:
                    # print(createdic)
                    ComputerLNV.objects.create(**createdic)
                    # print(Photo)
                    # if Photo:
                    #     for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                    #         # print(f)
                    #         empt = PICS()
                    #         # 增加其他字段应分别对应填写
                    #         empt.single = f
                    #         empt.pic = f
                    #         empt.save()
                    #         ComputerLNV.objects.filter(Number=Number).first().Photo.add(empt)

                # mock_data
                NID = request.POST.get('UnifiedNumberSearch')
                BrwStatus = request.POST.get('MachineStatusSearch')
                BR_per_code = request.POST.get('NumberSearch')
                check_dic = {}
                if NID:
                    check_dic["NID"] = NID
                if BrwStatus:
                    check_dic["BrwStatus"] = BrwStatus
                if BR_per_code:
                    check_dic["BR_per_code"] = BR_per_code

                if check_dic:
                    mock_datalist = ComputerLNV.objects.filter(**check_dic)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            # print((datetime.datetime.now().date() - i.Btime))
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
                selectUnifiedNumber = [
                    # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
                ]
                for i in ComputerLNV.objects.all().values("NID").order_by("NID"):
                    selectUnifiedNumber.append({"value": i["NID"]})

                # selectNumber = [
                #     # {"value": "張宵凌", "number": "20795434"}, {"value": "劉婭茹", "number": "20720831"},
                # ]
                # for i in ComputerLNV.objects.all().values("Usrname", "BR_per_code").distinct().order_by(
                #         "BR_per_code"):
                #     selectNumber.append({"value": i["Usrname"], "number": i["BR_per_code"]})
            if request.POST.get('action') == "updateSubmit":
                id = request.POST.get('id')
                Btime = request.POST.get('CollectDate')
                if not Btime or Btime == 'null':
                    Btime = None  # 日期爲空
                NID = request.POST.get('UnifiedNumber')
                BR_per_code = request.POST.get('Number')
                Usrname = request.POST.get('Name')
                MaterialPN = request.POST.get('MaterialPN')
                CPU = request.POST.get('CPU')
                RAM = request.POST.get('RAM')
                HDD = request.POST.get('HDD')
                Wireless = request.POST.get('Wireless')
                LCD = request.POST.get('LCD')
                OCR = request.POST.get('OCR')
                Battery = request.POST.get('Battery')
                Adaptor = request.POST.get('Adaptor')
                Area = request.POST.get('Region')
                Plant = request.POST.get('Factory')
                Carryif = request.POST.get('OutPlant')
                Purpose = request.POST.get('ComputerUse')
                Category = request.POST.get('Category')
                BrwStatus = request.POST.get('MachineStatus')
                IdleStatus = request.POST.get('IdleState')
                EFormNo = request.POST.get('FormNumber')
                updatedic = {
                    "Btime": Btime, "NID": NID,
                    "BR_per_code": BR_per_code, "Usrname": Usrname, "MaterialPN": MaterialPN,
                    "CPU": CPU, "RAM": RAM, "HDD": HDD,
                    "Wireless": Wireless, "LCD": LCD,
                    "OCR": OCR,
                    "Battery": Battery, "Adaptor": Adaptor, "Area": Area,
                    "Plant": Plant,
                    "Carryif": Carryif, "Purpose": Purpose, "Category": Category,
                    "BrwStatus": BrwStatus,
                    "IdleStatus": IdleStatus,
                    "EFormNo": EFormNo,
                             }
                print(updatedic)
                if ComputerLNV.objects.filter(NID=NID) and ComputerLNV.objects.filter(id=id).first().NID != NID:
                    errMsgNumber = """統一編號已存在"""
                    # print(1)
                else:

                    try:
                        with transaction.atomic():
                            # print(2)
                            ComputerLNV.objects.filter(id=id).update(**updatedic)
                            alert = 0
                    except:
                        alert = '此数据%s正被其他使用者编辑中...' % id

                # mock_data
                NID = request.POST.get('UnifiedNumberSearch')
                BrwStatus = request.POST.get('MachineStatusSearch')
                BR_per_code = request.POST.get('NumberSearch')
                check_dic = {}
                if NID:
                    check_dic["NID"] = NID
                if BrwStatus:
                    check_dic["BrwStatus"] = BrwStatus
                if BR_per_code:
                    check_dic["BR_per_code"] = BR_per_code

                if check_dic:
                    mock_datalist = ComputerLNV.objects.filter(**check_dic)
                else:
                    mock_datalist = ComputerLNV.objects.all()
                for i in mock_datalist:

                    Years = ''
                    Btime_str = ''
                    if i.Btime:
                        Btime_str = str(i.Btime)
                        if datetime.datetime.now().date() > i.Btime:
                            # print((datetime.datetime.now().date() - i.Btime))
                            Years = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                        0]) / 365,
                                2)
                    Rtime_str = ''
                    if i.Rtime:
                        Rtime_str = str(i.Rtime)
                    else:
                        Rtime_str = ''
                    Last_Borrow_date_str = ''
                    if i.Last_Borrow_date:
                        Last_Borrow_date_str = str(i.Last_Borrow_date)
                    else:
                        Last_Borrow_date_str = ''
                    Last_Return_date_str = ''
                    if i.Last_Return_date:
                        Last_Return_date_str = str(i.Last_Return_date)
                    else:
                        Last_Return_date_str = ''

                    mock_data.append(
                        {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                         "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                         "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                         "OCR": i.OCR,
                         "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                         "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                         "MachineStatus": i.BrwStatus,
                         "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                    )
                selectUnifiedNumber = [
                    # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
                ]
                for i in ComputerLNV.objects.all().values("NID").order_by("NID"):
                    selectUnifiedNumber.append({"value": i["NID"]})

                # selectNumber = [
                #     # {"value": "張宵凌", "number": "20795434"}, {"value": "劉婭茹", "number": "20720831"},
                # ]
                # for i in ComputerLNV.objects.all().values("Usrname", "BR_per_code").distinct().order_by(
                #         "BR_per_code"):
                #     selectNumber.append({"value": i["Usrname"], "number": i["BR_per_code"]})
            if request.POST.get('isGetData') == "alertData":
                # id = request.POST.get('ID')
                NID = request.POST.get('UnifiedNumber')
                # print(NID)
                if ComputerLNVHis.objects.filter(NID=NID):
                    for i in ComputerLNVHis.objects.filter(NID=NID):
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        tableData.append({
                                "id": i.id, "UnifiedNumber": i.NID, "EFormNo": i.EFormNo, "Carryif": i.Carryif,
                                "Area": i.Area, "Plant": i.Plant, "Purpose": i.Purpose,
                                "Name": i.Usrname,
                                "Number": i.BR_per_code, "CollectDate": Btime_str, "ReturnDate": Rtime_str, "Comments": i.Comments,
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
                    NID = responseData['UnifiedNumber']
                    BrwStatus = responseData['MachineStatus']
                    BR_per_code = responseData['Number']

                    for i in responseData['params']:
                        # print(i)
                        ComputerLNV.objects.get(id=i).delete()

                    # mock_data

                    check_dic = {}
                    if NID:
                        check_dic["NID"] = NID
                    if BrwStatus:
                        check_dic["BrwStatus"] = BrwStatus
                    if BR_per_code:
                        check_dic["BR_per_code"] = BR_per_code

                    if check_dic:
                        mock_datalist = ComputerLNV.objects.filter(**check_dic)
                    else:
                        mock_datalist = ComputerLNV.objects.all()
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
                    selectUnifiedNumber = [
                        # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
                    ]
                    for i in ComputerLNV.objects.all().values("NID").order_by("NID"):
                        selectUnifiedNumber.append({"value": i["NID"]})

                    # selectNumber = [
                    #     # {"value": "張宵凌", "number": "20795434"}, {"value": "劉婭茹", "number": "20720831"},
                    # ]
                    # for i in ComputerLNV.objects.all().values("Usrname", "BR_per_code").distinct().order_by(
                    #         "BR_per_code"):
                    #     selectNumber.append({"value": i["Usrname"], "number": i["BR_per_code"]})

                if 'ExcelData' in str(request.body):
                    responseData = json.loads(request.body)
                    # print(responseData)
                    # print(responseData['historyYear'],type(responseData['historyYear']))

                    NID = responseData['UnifiedNumber']
                    BrwStatus = responseData['MachineStatus']
                    BR_per_code = responseData['Number']

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
                            if key in headermodel_Computer.keys():
                                modeldata[headermodel_Computer[key]] = value
                        if 'NID' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，統一編號不能爲空
                                                                            """ % rownum
                            break
                        if 'MaterialPN' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，MaterialPN不能爲空
                                                                            """ % rownum
                            break
                        if 'CPU' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，CPU不能爲空
                                                                            """ % rownum
                            break
                        if 'RAM' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，RAM不能爲空
                                                                            """ % rownum
                            break
                        if 'HDD' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，HDD不能爲空
                                                                            """ % rownum
                            break
                        if 'Wireless' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Wireless不能爲空
                                                                            """ % rownum
                            break
                        if 'LCD' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，LCD不能爲空
                                                                            """ % rownum
                            break
                        if 'OCR' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，OCR不能爲空
                                                                            """ % rownum
                            break
                        if 'Battery' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Battery不能爲空
                                                                            """ % rownum
                            break
                        if 'Adaptor' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Adaptor不能爲空
                                                                            """ % rownum
                            break
                        if 'Area' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Area能爲空
                                                                            """ % rownum
                            break
                        if 'Carryif' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Carryif不能爲空
                                                                            """ % rownum
                            break
                        if 'Plant' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Plant不能爲空
                                                                            """ % rownum
                            break
                        if 'Purpose' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Purpose不能爲空
                                                                            """ % rownum
                            break
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
                        if 'BrwStatus' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，BrwStatus不能爲空
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
                        if 'Last_Borrow_date' in modeldata.keys():
                            if len(modeldata['Last_Borrow_date']) >= 8 and len(modeldata['Last_Borrow_date']) <= 10:
                                modeldata['Last_Borrow_date'] = modeldata['Last_Borrow_date'].replace('/', '-')
                                modeldata['Last_Borrow_date'] = modeldata['Last_Borrow_date'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，上一次領用日期格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['Last_Borrow_date'] = None  # 日期爲空
                        if 'Last_Return_date' in modeldata.keys():
                            if len(modeldata['Last_Return_date']) >= 8 and len(modeldata['Last_Return_date']) <= 10:
                                modeldata['Last_Return_date'] = modeldata['Last_Return_date'].replace('/', '-')
                                modeldata['Last_Return_date'] = modeldata['Last_Return_date'].replace('.', '-')
                                startupload = 1
                            else:
                                # canEdit = 0
                                startupload = 0
                                err_ok = 2
                                errMsg = err_msg = """
                                                            第"%s"條數據，上一次歸還日期格式不對，請確認是否是文字格式YYYY-MM-DD
                                                                                """ % rownum
                                break
                        else:
                            modeldata['Last_Return_date'] = None  # 日期爲空

                        uploadxlsxlist.append(modeldata)
                    # print(startupload)
                    #让数据可以从有值更新为无值
                    DevieModelfiedlist = []
                    for i in ComputerLNV._meta.fields:
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
                            #     if key in headermodel_Computer.keys():
                            #         if headermodel_Computer[key] == "Predict_return" or headermodel_Computer[
                            #             key] == "Borrow_date" or headermodel_Computer[key] == "Return_date":
                            #             print(value)
                            #             modeldata[headermodel_Computer[key]] = value.split("/")[2] + "-" + \
                            #                                                        value.split("/")[0] + "-" + \
                            #                                                        value.split("/")[1]
                            #         else:
                            #             modeldata[headermodel_Computer[key]] = value
                            Check_dic = {
                                'NID': i['NID'],
                            }
                            # print(modeldata)
                            # print(i)
                            # Check_dic_Gantt['Test_Start'] = None  # 日期格式为空NULL不能用空字符
                            if ComputerLNV.objects.filter(**Check_dic):#已经存在覆盖
                                pass
                                # ComputerLNV.objects.filter(
                                #     **Check_dic).update(**i)
                            else:#新增
                                ComputerLNV.objects.create(**i)
                        errMsg = '上傳成功'

                    # mock_data

                    check_dic = {}
                    if NID:
                        check_dic["NID"] = NID
                    if BrwStatus:
                        check_dic["BrwStatus"] = BrwStatus
                    if BR_per_code:
                        check_dic["BR_per_code"] = BR_per_code

                    if check_dic:
                        mock_datalist = ComputerLNV.objects.filter(**check_dic)
                    else:
                        mock_datalist = ComputerLNV.objects.all()
                    for i in mock_datalist:

                        Years = ''
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                            if datetime.datetime.now().date() > i.Btime:
                                Years = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Btime)).split(' ')[
                                            0]) / 365,
                                    2)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        else:
                            Rtime_str = ''
                        Last_Borrow_date_str = ''
                        if i.Last_Borrow_date:
                            Last_Borrow_date_str = str(i.Last_Borrow_date)
                        else:
                            Last_Borrow_date_str = ''
                        Last_Return_date_str = ''
                        if i.Last_Return_date:
                            Last_Return_date_str = str(i.Last_Return_date)
                        else:
                            Last_Return_date_str = ''

                        mock_data.append(
                            {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                             "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                             "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD,
                             "OCR": i.OCR,
                             "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                             "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                             "MachineStatus": i.BrwStatus,
                             "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                        )
                    selectUnifiedNumber = [
                        # {"value": "GI027569"}, {"value": "GI027570"}, {"value": "GI027571"},
                    ]
                    for i in ComputerLNV.objects.all().values("NID").order_by("NID"):
                        selectUnifiedNumber.append({"value": i["NID"]})

                    # selectNumber = [
                    #     # {"value": "張宵凌", "number": "20795434"}, {"value": "劉婭茹", "number": "20720831"},
                    # ]
                    # for i in ComputerLNV.objects.all().values("Usrname", "BR_per_code").distinct().order_by(
                    #         "BR_per_code"):
                    #     selectNumber.append({"value": i["Usrname"], "number": i["BR_per_code"]})


        data = {
            "content": mock_data,
            "tableData": tableData,
            "selectUnifiedNumber": selectUnifiedNumber,
            "selectNumber": selectNumber,
            "allMachineStatus": allMachineStatus,
            "sectionIdleState": sectionIdleState,
            "errMsg": errMsg,
            "errMsgNumber": errMsgNumber,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ComputerMS/M_edit.html', locals())


