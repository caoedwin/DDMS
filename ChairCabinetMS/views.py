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
from .models import ChairCabinetLNV, ChairCabinetLNVHis
from app01.models import UserInfo

headermodel_ChairCabinet = {
    '統一編號': 'NID',
    '產品類別': 'Category',
    '位置': 'Area',
    '使用狀態': 'BrwStatus', '用途': 'Purpose', '保管人工號': 'OAPcode', '保管人': 'OAP',
    '領用日期': 'Btime', '使用人工號': 'BR_per_code', '使用人': 'Usrname', '歸還日期': 'Rtime',

    '上一任使用人姓名': 'Last_BR_per', '上一任使用人工號': 'Last_BR_per_code',
    '上一次領用日期': 'Last_Borrow_date', '上一次歸還日期': 'Last_Return_date',
    '轉賬人員工號': 'Transefer_per_code',
    '接收人員工號': 'Receive_per_code', '簽核人員工號': 'Sign_per_code',
}

@csrf_exempt
def BorrowedChairCabinet(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/BorrowedDevice"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]

    selectGYNumber = [
        # {"value": "DQA-C-001"}, {"value": "DQA-C-002"}, {"value": "DQA-C-004"},
    ]
    for i in ChairCabinetLNV.objects.all().values("NID").distinct().order_by("NID"):
        selectGYNumber.append({"value": i["NID"]})

    selectNumber = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        selectNumber.append({"value": i["account"], "number": i["CNname"]})

    allUseStatus = [
        # "使用中", "申請中", "歸還中", "轉帳中", "接收中", "閑置中", "已損壞", "申請確認中", "歸還確認中", "轉帳確認中"
    ]
    for i in ChairCabinetLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
        allUseStatus.append(i["BrwStatus"])

    allCategory = [
        # "椅子", "櫃子"
    ]
    for i in ChairCabinetLNV.objects.all().values("Category").distinct().order_by("Category"):
        allCategory.append(i["Category"])


    errMessage = ""
    if request.method == "POST":
        if 'first' in str(request.body):
            # mock_data
            NID = request.POST.get('GYNumber')
            BrwStatus = request.POST.get('UseStatus')
            BR_per_code = request.POST.get('Number')
            Category = request.POST.get('Category')

            check_dic = {}
            if NID:
                check_dic["NID"] = NID
            if BrwStatus:
                check_dic["BrwStatus"] = BrwStatus
            if BR_per_code:
                check_dic["BR_per_code"] = BR_per_code
            if Category:
                check_dic["Category"] = Category

            if check_dic:
                mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
            else:
                mock_datalist = ChairCabinetLNV.objects.all()
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
                    {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                     "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                     "User": i.Usrname, "UserNumber": i.BR_per_code,

                     "Position": i.Area, "Purpose": i.Purpose,
                     "UseStatus": i.BrwStatus,
                     "CollectDate": Btime_str,
                     "Rtime": Rtime_str,
                     "Transefer_per_code": i.Transefer_per_code,
                     "Receive_per_code": i.Receive_per_code,
                     "Sign_per_code": i.Sign_per_code,
                     }
                )
        if 'SEARCH' in str(request.body):
            # mock_data
            NID = request.POST.get('GYNumber')
            BrwStatus = request.POST.get('UseStatus')
            BR_per_code = request.POST.get('Number')
            Category = request.POST.get('Category')

            check_dic = {}
            if NID:
                check_dic["NID"] = NID
            if BrwStatus:
                check_dic["BrwStatus"] = BrwStatus
            if BR_per_code:
                check_dic["BR_per_code"] = BR_per_code
            if Category:
                check_dic["Category"] = Category

            if check_dic:
                mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
            else:
                mock_datalist = ChairCabinetLNV.objects.all()
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
                    {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                     "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                     "User": i.Usrname, "UserNumber": i.BR_per_code,

                     "Position": i.Area, "Purpose": i.Purpose,
                     "UseStatus": i.BrwStatus,
                     "CollectDate": Btime_str,
                     "Rtime": Rtime_str,
                     "Transefer_per_code": i.Transefer_per_code,
                     "Receive_per_code": i.Receive_per_code,
                     "Sign_per_code": i.Sign_per_code,
                     }
                )
        if 'EnsureInfo' in str(request.body):
            # print(1)



            BorrowedID = request.POST.get('BorrowID')
            linshi_Area = request.POST.get('Position')
            linshi_Purpose = request.POST.get('Purpose')
            # print(BorrowedID, type(BorrowedID),NID)
            # print(json.loads(BorrowedID))
            # print(BorrowedID.split(','))
            updatedic = {
                # 'ProjectCode': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                         'BrwStatus': '申請確認中', 'Usrname': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'),
                         'linshi_Area': linshi_Area, 'linshi_Purpose': linshi_Purpose,
                         # 'OAP': request.session.get('CNname'), 'OAPcode': request.session.get('account'),
                         # 'Plandate': request.POST.get('Predict_return'),
                'Btime': None, 'Rtime': None,
            }
            # print(updatedic)
            for i in BorrowedID.split(','):
                # print(i)
                try:
                    with transaction.atomic():
                        # print(updatedic)
                        ChairCabinetLNV.objects.filter(id=i).update(**updatedic)
                        # alert = 0
                except:
                    # print('2')
                    alert = '此数据%s正被其他使用者编辑中...' % i
                    errMessage = '此数据%s正被其他使用者编辑中...' % i

            # mock_data
            NID = request.POST.get('GYNumber')
            BrwStatus = request.POST.get('UseStatus')
            BR_per_code = request.POST.get('Number')
            Category = request.POST.get('Category')

            check_dic = {}
            if NID:
                check_dic["NID"] = NID
            if BrwStatus:
                check_dic["BrwStatus"] = BrwStatus
            if BR_per_code:
                check_dic["BR_per_code"] = BR_per_code
            if Category:
                check_dic["Category"] = Category

            if check_dic:
                mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
            else:
                mock_datalist = ChairCabinetLNV.objects.all()
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
                    {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                     "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                     "User": i.Usrname, "UserNumber": i.BR_per_code,

                     "Position": i.Area, "Purpose": i.Purpose,
                     "UseStatus": i.BrwStatus,
                     "CollectDate": Btime_str,
                     "Rtime": Rtime_str,
                     "Transefer_per_code": i.Transefer_per_code,
                     "Receive_per_code": i.Receive_per_code,
                     "Sign_per_code": i.Sign_per_code,
                     }
                )
        data = {
            "content": mock_data,
            "selectGYNumber": selectGYNumber,
            "allUseStatus": allUseStatus,
            "allCategory": allCategory,
            "errMessage": errMessage,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/BorrowedChairCabinet.html', locals())


@csrf_exempt
def R_Borrowed(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/R_Borrowed"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]


    #
    selectNumber = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        if i["account"] != request.session.get('account_DMS'):
            selectNumber.append({"value": i["account"], "number": i["CNname"]})
    #既然是转账，就无需转给自己


    errMessage = ""
    # 轉賬時是保管人OAP發起， 使用人可能爲空，（閑置時）
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = ChairCabinetLNV.objects.filter(OAP=request.session.get('CNname_DMS'),
                                                         OAPcode=request.session.get('account_DMS'), BrwStatus__in=['使用中', '閑置中'])
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
            if request.POST.get('isGetData') == 'SAVE':
                ID = request.POST.get('ID')
                Position = request.POST.get('Position')

                updatedic = {
                    "Area": Position
                }
                try:
                    with transaction.atomic():
                        print(updatedic)
                        ChairCabinetLNV.objects.filter(id=ID).update(**updatedic)
                        # print('1')
                        alert = 0
                except Exception as e:
                    # print(e)
                    alert = '此数据%s正被其他使用者编辑中...' % i

                # mock_data
                checkAdaPow = {
                    'BrwStatus__in': ['使用中', '閑置中'],
                    "OAP": request.session.get('CNname_DMS'),
                    "OAPcode": request.session.get('account_DMS'),
                }
                print(checkAdaPow)
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
            if request.POST.get('isGetData') == 'Transfer':
                Receive_per_code = request.POST.get('Number')
                updatedic = {'BrwStatus': '轉帳確認中',
                             # 'BR_per': request.session.get('CNname'),
                             # 'Predict_return': None,
                             # 'Borrow_date': None,'Return_date': None,
                             # 'Transefer_per_code': ChairCabinetLNV.objects.filter(id=request.POST.get('ID')).first().BR_per_code,#转账人可能为空，从而导致转账人为空，转账人应当是保管人，保管人肯定不为空。
                             'Transefer_per_code': ChairCabinetLNV.objects.filter(id=request.POST.get('ID')).first().OAPcode,
                             'Receive_per_code': Receive_per_code,
                             'Last_BrwStatus': ChairCabinetLNV.objects.filter(id=request.POST.get('ID')).first().BrwStatus,
                             'Btime': None, 'Rtime': None,
                             }
                # print(updatedic)

                try:
                    with transaction.atomic():
                        ChairCabinetLNV.objects.filter(id=request.POST.get('ID')).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % request.POST.get('ID')

                UnifiedNumber = request.POST.get('UnifiedNumber')
                check_dic = {}
                if UnifiedNumber:
                    check_dic["NID"] = UnifiedNumber

                if check_dic:
                    mock_datalist = ChairCabinetLNV.objects.filter(OAP=request.session.get('CNname_DMS'),
                                                               OAPcode=request.session.get('account_DMS'),
                                                               BrwStatus__in=['使用中', '閑置中']).filter(**check_dic)
                else:
                    mock_datalist = ChairCabinetLNV.objects.filter(OAP=request.session.get('CNname_DMS'),
                                                               OAPcode=request.session.get('account_DMS'),
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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
            # "selectUnifiedNumber": selectUnifiedNumber,
            "selectNumber": selectNumber,
            # "allMachineStatus": allMachineStatus,
            "errMessage": errMessage,


        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/R_Borrowed.html', locals())

@csrf_exempt
def R_Destine(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/R_Destine"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]
    #此時使用二五年就是申請人，保管人就是管理員
    if request.method == "POST":
        if request.POST:
            # print(request.body)
            if 'first' in str(request.body):
                # mock_data
                mock_datalist = ChairCabinetLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus__in=['申請確認中', '申請核准中'])
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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
                    for i in responseData['Return']:
                        # print(i)
                        updatedic['Usrname'] = ChairCabinetLNV.objects.filter(id=i).first().Last_BR_per
                        updatedic['BR_per_code'] = ChairCabinetLNV.objects.filter(id=i).first().Last_BR_per_code
                        # updatedic['ProjectCode'] = ChairCabinetLNV.objects.filter(id=i).first().Last_ProjectCode
                        # updatedic['Phase'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Phase
                        # updatedic['Predict_return'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Predict_return
                        updatedic['Btime'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Rtime'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Return_date
                        # print(updatedic)
                        try:
                            with transaction.atomic():
                                ChairCabinetLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    mock_datalist = ChairCabinetLNV.objects.filter(Usrname=request.session.get('CNname_DMS'),
                                                               BR_per_code=request.session.get('account_DMS'),
                                                               BrwStatus__in=['申請確認中', '申請核准中'])
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
                            {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                             "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                             "User": i.Usrname, "UserNumber": i.BR_per_code,

                             "Position": i.Area, "Purpose": i.Purpose,
                             "UseStatus": i.BrwStatus,
                             "CollectDate": Btime_str,
                             "Rtime": Rtime_str,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per_code": i.Receive_per_code,
                             "Sign_per_code": i.Sign_per_code,
                             }
                        )
            # print(request.POST)

        data = {
            "content": mock_data,
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/R_Destine.html', locals())

@csrf_exempt
def BG_Borrow(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/R_Destine"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {
                    'BrwStatus': '申請確認中',
                    "OAP": request.session.get('CNname_DMS'),
                    "OAPcode": request.session.get('account_DMS'),
                }
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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
                if 'Apply' in str(request.body):
                    responseData = json.loads(request.body)


                    updatedic = {'BrwStatus': '申請核准中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }
                    # print(updatedic)
                    for i in responseData['Return']:
                        # print(i)
                        # updatedic['Last_BR_per'] = ChairCabinetLNV.objects.filter(id=i).first().Usrname
                        # updatedic['Last_BR_per_code'] = ChairCabinetLNV.objects.filter(id=i).first().BR_per_code
                        # # updatedic['Last_ProjectCode'] = ChairCabinetLNV.objects.filter(id=i).first().ProjectCode
                        # # updatedic['Last_Phase'] = ChairCabinetLNV.objects.filter(id=i).first().Phase
                        # # updatedic['Last_Predict_return'] = ChairCabinetLNV.objects.filter(id=i).first().Plandate
                        # updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = ChairCabinetLNV.objects.filter(id=i).first().Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                ChairCabinetLNV.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    checkAdaPow = {
                        'BrwStatus': '申請確認中',
                        "OAP": request.session.get('CNname_DMS'),
                        "OAPcode": request.session.get('account_DMS'),
                    }
                    if checkAdaPow:
                        mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = ChairCabinetLNV.objects.all()
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
                            {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                             "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                             "User": i.Usrname, "UserNumber": i.BR_per_code,

                             "Position": i.Area, "Purpose": i.Purpose,
                             "UseStatus": i.BrwStatus,
                             "CollectDate": Btime_str,
                             "Rtime": Rtime_str,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per_code": i.Receive_per_code,
                             "Sign_per_code": i.Sign_per_code,
                             }
                        )
        data = {
            # "select": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/BG_Borrow.html', locals())

@csrf_exempt
def M_Borrow(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/M_Borrow"

        # print(i)


    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]

    selectItem = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    for i in ChairCabinetLNV.objects.filter(BrwStatus='申請核准中').values('Usrname', 'BR_per_code').distinct().order_by('BR_per_code'):
        selectItem.append({"value": i["BR_per_code"], "number": i["Usrname"]})

    errMessage = ""
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '申請核准中'}
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BrwStatus': '申請核准中'}
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
                # checkAdaPow = {'BrwStatus': '申請核准中'}
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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
                    checkAdaPow = {'BrwStatus': '申請核准中'}
                    if responseData['Name']:
                        checkAdaPow['Usrname'] = responseData['Name']
                    if "Number" in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['Number']

                    updatedic = {
                                'BrwStatus': '使用中',
                                'linshi_Area': '',
                                'linshi_Purpose': '',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }
                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)
                        updatedic['Area'] = ChairCabinetLNV.objects.filter(id=i).first().linshi_Area
                        updatedic['Purpose'] = ChairCabinetLNV.objects.filter(id=i).first().linshi_Purpose
                        updatedic['OAP'] = ChairCabinetLNV.objects.filter(id=i).first().Usrname
                        updatedic['OAPcode'] = ChairCabinetLNV.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_BR_per'] = ChairCabinetLNV.objects.filter(id=i).first().Usrname
                        updatedic['Last_BR_per_code'] = ChairCabinetLNV.objects.filter(id=i).first().BR_per_code
                        # updatedic['Last_ProjectCode'] = ChairCabinetLNV.objects.filter(id=i).first().ProjectCode
                        # updatedic['Last_Phase'] = ChairCabinetLNV.objects.filter(id=i).first().Phase
                        # updatedic['Last_Predict_return'] = ChairCabinetLNV.objects.filter(id=i).first().Plandate
                        updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = ChairCabinetLNV.objects.filter(id=i).first().Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                ChairCabinetLNV.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    # checkAdaPow = {'BrwStatus': '申請核准中'}
                    if checkAdaPow:
                        mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = ChairCabinetLNV.objects.all()
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
            "selectItem": selectItem,

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/M_Borrow.html', locals())


@csrf_exempt
def R_Transfer(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/R_Transfer"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]
    # 轉賬時是保管人OAP發起， 使用人可能爲空，（閑置時）
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = ChairCabinetLNV.objects.filter(OAP=request.session.get('CNname_DMS'),
                                                            OAPcode=request.session.get('account_DMS'),
                                                               BrwStatus__in=["轉帳確認中", '接收確認中'])
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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
                                 "Receive_per_code": "",
                                'Last_BrwStatus': '',
                                 }
                    for i in responseData['Transfer']:

                        updatedic['BrwStatus'] = ChairCabinetLNV.objects.filter(id=i).first().Last_BrwStatus
                        updatedic['Btime'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Rtime'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                ChairCabinetLNV.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    mock_datalist = ChairCabinetLNV.objects.filter(OAP=request.session.get('CNname_DMS'),
                                                                   OAPcode=request.session.get('account_DMS'),
                                                                   BrwStatus__in=["轉帳確認中", '接收確認中'])
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
                            {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                             "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                             "User": i.Usrname, "UserNumber": i.BR_per_code,

                             "Position": i.Area, "Purpose": i.Purpose,
                             "UseStatus": i.BrwStatus,
                             "CollectDate": Btime_str,
                             "Rtime": Rtime_str,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per_code": i.Receive_per_code,
                             "Sign_per_code": i.Sign_per_code,
                             }
                        )
        data = {
            "content": mock_data,
            # "options": options

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/R_Transfer.html', locals())

@csrf_exempt
def R_Receive(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/R_Receive"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]

    allUseStatus = ["使用中", "閑置中", ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '轉帳確認中', "Receive_per_code": request.session.get('account_DMS')}
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
            if request.POST.get('action') == 'Receive':
                linshi_BrwStatus = request.POST.get('UseStatus')
                linshi_Area = request.POST.get('Position')
                linshi_Purpose = request.POST.get('Purpose')
                ID = request.POST.get('ID')
                NID = request.POST.get('GYNumber')
                updatedic = {'BrwStatus': '接收確認中',
                            'linshi_BrwStatus': linshi_BrwStatus,
                            'linshi_Area': linshi_Area,
                            'linshi_Purpose': linshi_Purpose,
                             # 'BR_per': request.session.get('CNname'),
                             # 'Predict_return': None,
                             # 'Borrow_date': None,'Return_date': None,

                             }
                # print(updatedic)
                try:
                    with transaction.atomic():
                        # print(1)
                        ChairCabinetLNV.objects.filter(id=request.POST.get('ID')).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % request.POST.get('ID')
                # mock_data
                checkAdaPow = {'BrwStatus': '轉帳確認中', "Receive_per_code": request.session.get('account_DMS')}
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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
            "allUseStatus": allUseStatus,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/R_Receive.html', locals())

@csrf_exempt
def M_Transfer(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/M_Keep"

    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "UserNumber": "2019234", "Position": "V2FA-33", "UseStatus": "使用中",
        #  "Purpose": "個人使用", "Borrower": "王巧遇", "BorrowerNum": "2019234", "CollectDate": "2019-2-11"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "UserNumber": "2019235",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "王星晨",
        #  "BorrowerNum": "2019235", "CollectDate": "2019-2-11"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "UserNumber": "2019236",
        #  "UseStatus": "使用中", "Purpose": "個人使用", "Borrower": "張玉悅",
        #  "BorrowerNum": "2019236", "CollectDate": "2019-2-11"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #  "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #  "BorrowerNum": "2019237", "CollectDate": "2019-2-11"},
    ]

    selectItem = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    # 轉賬時是保管人OAP發起， 使用人可能爲空，（閑置時）
    for i in ChairCabinetLNV.objects.filter(BrwStatus='接收確認中').values("OAPcode", "OAP").distinct():
        selectItem.append({"value": i["OAPcode"], "number": i["OAP"]})
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                checkAdaPow = {'BrwStatus': '接收確認中'}
                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         # "Transefer_per": UserInfo.objects.filter(account=i.OAPcode).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
            if request.POST.get('isGetData') == 'SEARCH':
                # mock_data
                checkAdaPow = {'BrwStatus': '接收確認中'}
                if request.POST.get('Name'):
                    checkAdaPow['OAP'] = request.POST.get('Name')
                if request.POST.get('Number', None):
                    checkAdaPow['OAPcode'] = request.POST.get('Number')

                if checkAdaPow:
                    mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
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


                    updatedic = {
                                # 'BrwStatus': '使用中',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'linshi_BrwStatus': '',
                                 'linshi_Area': '',
                                 'linshi_Purpose': '',
                                 'Btime': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }

                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)
                        updatedic['OAP'] = UserInfo.objects.filter(account=ChairCabinetLNV.objects.filter(id=i).first().Receive_per_code).first().CNname
                        updatedic['OAPcode'] = ChairCabinetLNV.objects.filter(id=i).first().Receive_per_code
                        BrwStatus = ChairCabinetLNV.objects.filter(id=i).first().linshi_BrwStatus
                        updatedic['BrwStatus'] = BrwStatus
                        updatedic['Area'] = ChairCabinetLNV.objects.filter(id=i).first().linshi_Area
                        updatedic['Purpose'] = ChairCabinetLNV.objects.filter(id=i).first().linshi_Purpose
                        if BrwStatus == "使用中": # 闲置就没有使用人只有保管人
                            updatedic['Usrname'] = UserInfo.objects.filter(
                                account=ChairCabinetLNV.objects.filter(id=i).first().Receive_per_code).first().CNname
                            updatedic['BR_per_code'] = ChairCabinetLNV.objects.filter(id=i).first().Receive_per_code
                        else:
                            updatedic['Usrname'] = ''
                            updatedic['BR_per_code'] = ''
                        # updatedic['ProjectCode'] = ChairCabinetLNV.objects.filter(id=i).first().Last_ProjectCode
                        # updatedic['Phase'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Phase
                        # updatedic['Predict_return'] = ChairCabinetLNV.objects.filter(id=i).first().Last_Predict_return
                        # updatedic['Last_BR_per'] = ChairCabinetLNV.objects.filter(id=i).first().Usrname
                        # updatedic['Last_BR_per_code'] = ChairCabinetLNV.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = ChairCabinetLNV.objects.filter(id=i).first().Return_date

                        Devicebyid = ChairCabinetLNV.objects.filter(id=i).first()
                        updatedic_His = {
                            "NID": Devicebyid.NID, "Category": Devicebyid.Category,
                            "Area": Devicebyid.Area,
                            "Purpose": Devicebyid.Purpose,
                            "OAP": Devicebyid.OAP,
                            "OAPcode": Devicebyid.OAPcode,
                            "BrwStatus": Devicebyid.BrwStatus,
                            # "uscyc": ChairCabinetLNV.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date,
                            # "Plandate": Devicebyid.Last_Predict_return,
                            "Rtime": datetime.datetime.now().date(),
                            "Changetime": datetime.datetime.now().date(),
                            "Usrname": Devicebyid.Usrname, "BR_per_code": Devicebyid.BR_per_code,
                            "Transefer_per_code": Devicebyid.Transefer_per_code, "Receive_per_code": Devicebyid.Receive_per_code,
                            # "ProjectCode": Devicebyid.Last_ProjectCode, "Phase": Devicebyid.Last_Phase,
                            # "Devstatus": "已歸還",
                            # "Result": '',
                            # "Comments": '',
                        }
                        updatedic_His_check = {
                            "NID": Devicebyid.NID, "Category": Devicebyid.Category,
                            "Area": Devicebyid.Area,
                            "Purpose": Devicebyid.Purpose,
                            "OAP": Devicebyid.OAP,
                            "OAPcode": Devicebyid.OAPcode,
                            "BrwStatus": Devicebyid.Last_BrwStatus,
                            # "uscyc": ChairCabinetLNV.objects.filter(id=i).first().Last_uscyc,
                            "Btime": Devicebyid.Last_Borrow_date,
                            # "Plandate": Devicebyid.Last_Predict_return,
                            # "Rtime": datetime.datetime.now().date(),
                            "Changetime": datetime.datetime.now().date(),
                            "Usrname": Devicebyid.Usrname, "BR_per_code": Devicebyid.BR_per_code,
                            "Transefer_per_code": Devicebyid.Transefer_per_code, "Receive_per_code": Devicebyid.Receive_per_code,
                        }

                        try:
                            with transaction.atomic():
                                print(updatedic)
                                print(updatedic_His)
                                if ChairCabinetLNVHis.objects.filter(**updatedic_His_check):
                                    pass#防止历史记录存成功了，Device更新失败，需要重复操作。
                                else:
                                    ChairCabinetLNVHis.objects.create(**updatedic_His)
                                ChairCabinetLNV.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    checkAdaPow = {'BrwStatus': '接收確認中'}
                    if responseData['Name']:
                        checkAdaPow['OAP'] = responseData['Name']
                    if 'Number' in responseData.keys():
                        checkAdaPow['OAPcode'] = responseData['Number']
                    if checkAdaPow:
                        mock_datalist = ChairCabinetLNV.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = ChairCabinetLNV.objects.all()
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
                            {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                             "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                             "User": i.Usrname, "UserNumber": i.BR_per_code,

                             "Position": i.Area, "Purpose": i.Purpose,
                             "UseStatus": i.BrwStatus,
                             "CollectDate": Btime_str,
                             "Rtime": Rtime_str,
                             "Transefer_per": UserInfo.objects.filter(account=i.Transefer_per_code).first().CNname,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per": UserInfo.objects.filter(account=i.Receive_per_code).first().CNname,
                             "Receive_per_code": i.Receive_per_code,
                             "Sign_per_code": i.Sign_per_code,
                             }
                        )
        data = {
            "content": mock_data,
            "selectItem": selectItem,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/M_Transfer.html', locals())

@csrf_exempt
def M_edit(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "ChairCabinetLNV/M_upload"
    mock_data = [
        # {"id": "1", "GYNumber": "DQA-C-001", "Category": "椅子",
        #  "User": "王巧遇", "Position": "V2FA-33", "Custodian": "王巧遇",
        #  "UseStatus": "使用中", "Purpose": "個人使用"},
        # {"id": "2", "GYNumber": "DQA-C-002", "Category": "椅子",
        #  "User": "王星晨", "Position": "V2FA-29", "Custodian": "王星晨",
        #  "UseStatus": "閒置", "Purpose": "會議室使用"},
        # {"id": "3", "GYNumber": "DQA-G-001", "Category": "櫃子",
        #  "User": "張玉悅", "Position": "V2FA-28", "Custodian": "張玉悅",
        #  "UseStatus": "使用中", "Purpose": "個人使用"},
        # {"id": "4", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #  "User": "殷開欣", "Position": "V2FA-26", "Custodian": "殷開欣",
        #  "UseStatus": "閒置", "Purpose": "會議室使用"},
    ]

    selectGYNumber = [
        # {"value": "DQA-C-001"}, {"value": "DQA-C-002"}, {"value": "DQA-C-004"},
    ]
    for i in ChairCabinetLNV.objects.all().values("NID").distinct().order_by("NID"):
        selectGYNumber.append({"value": i["NID"]})

    selectNumber = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        selectNumber.append({"value": i["account"], "number": i["CNname"]})

    # 歷史記錄
    tableData = [
        # {
        #     "id": "1", "GYNumber": "DQA-G-002", "Category": "櫃子",
        #     "User": "殷開欣", "Position": "V2FA-26", "UserNumber": "2019237",
        #     "UseStatus": "閑置中", "Purpose": "會議室使用", "Borrower": "殷開欣",
        #     "BorrowerNum": "2019237", "CollectDate": "2019-2-11", "ModifyDate": "2019-2-11"
        # },
    ]

    allUseStatus = [
        "使用中", "轉帳確認中", "接收確認中", "閑置中", "已損壞", "維修中", "申請確認中", "申請核准中",
    ]
    # for i in ChairCabinetLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
    #     allUseStatus.append(i["BrwStatus"])

    allCategory = [
        # "椅子", "櫃子"
                   ]
    for i in ChairCabinetLNV.objects.all().values("Category").distinct().order_by("Category"):
        allCategory.append(i["Category"])


    errMsg = ''
    errMsgNumber = ''  # 新增弹框

    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if request.POST:
            # if request.POST.get('isGetData') == 'first':
            #     # mock_data
            #     mock_datalist = ChairCabinetLNV.objects.all()
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
                # mock_data
                NID = request.POST.get('GYNumber')
                BrwStatus = request.POST.get('UseStatus')
                BR_per_code = request.POST.get('Number')
                Category = request.POST.get('Category')

                check_dic = {}
                if NID:
                    check_dic["NID"] = NID
                if BrwStatus:
                    check_dic["BrwStatus"] = BrwStatus
                if BR_per_code:
                    check_dic["BR_per_code"] = BR_per_code
                if Category:
                    check_dic["Category"] = Category

                if check_dic:
                    mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
            if request.POST.get('action') == "addSubmit":
                Btime = request.POST.get('CollectDate')
                if not Btime or Btime == 'null':
                    Btime = None  # 日期爲空
                NID = request.POST.get('GYNumber')
                OAPcode = request.POST.get('BorrowerNum')
                OAP = request.POST.get('Borrower')
                Category = request.POST.get('Category')
                Area = request.POST.get('Position')
                BR_per_code = request.POST.get('UserNumber')
                Usrname = request.POST.get('User')
                BrwStatus = request.POST.get('UseStatus')
                Purpose = request.POST.get('Purpose')

                createdic = {
                    "Btime": Btime, "NID": NID,
                    "BR_per_code": BR_per_code, "Usrname": Usrname, "Category": Category,
                    "Area": Area, "OAPcode": OAPcode, "OAP": OAP,
                    "Purpose": Purpose,
                    "BrwStatus": BrwStatus,
                             }
                # print(createdic)
                if ChairCabinetLNV.objects.filter(NID=NID):
                    errMsgNumber = """統一編號已存在"""
                else:
                    # print(createdic)
                    ChairCabinetLNV.objects.create(**createdic)
                    # print(Photo)
                    # if Photo:
                    #     for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                    #         # print(f)
                    #         empt = PICS()
                    #         # 增加其他字段应分别对应填写
                    #         empt.single = f
                    #         empt.pic = f
                    #         empt.save()
                    #         ChairCabinetLNV.objects.filter(Number=Number).first().Photo.add(empt)

                # mock_data
                NID = request.POST.get('GYNumberSearch')
                BrwStatus = request.POST.get('UseStatusSearch')
                Category = request.POST.get('CategorySearch')
                BR_per_code = request.POST.get('NumberSearch')
                check_dic = {}
                if NID:
                    check_dic["NID"] = NID
                if BrwStatus:
                    check_dic["BrwStatus"] = BrwStatus
                if BR_per_code:
                    check_dic["BR_per_code"] = BR_per_code
                if Category:
                    check_dic["Category"] = Category

                if check_dic:
                    mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
                selectGYNumber = [
                    # {"value": "DQA-C-001"}, {"value": "DQA-C-002"}, {"value": "DQA-C-004"},
                ]
                for i in ChairCabinetLNV.objects.all().values("NID").distinct().order_by("NID"):
                    selectGYNumber.append({"value": i["NID"]})

                selectNumber = [
                    # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
                ]
                for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
                    selectNumber.append({"value": i["account"], "number": i["CNname"]})
                # allUseStatus = [
                #     # "使用中", "申請中", "歸還中", "轉帳中", "接收中", "閑置中", "已損壞", "申請確認中", "歸還確認中", "轉帳確認中"
                # ]
                # for i in ChairCabinetLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
                #     allUseStatus.append(i["BrwStatus"])

                allCategory = [
                    # "椅子", "櫃子"
                ]
                for i in ChairCabinetLNV.objects.all().values("Category").distinct().order_by("Category"):
                    allCategory.append(i["Category"])
            if request.POST.get('action') == "updateSubmit":
                id = request.POST.get('id')
                Btime = request.POST.get('CollectDate')
                if not Btime or Btime == 'null':
                    Btime = None  # 日期爲空
                NID = request.POST.get('GYNumber')
                OAPcode = request.POST.get('BorrowerNum')
                OAP = request.POST.get('Borrower')
                Category = request.POST.get('Category')
                Area = request.POST.get('Position')
                BR_per_code = request.POST.get('UserNumber')
                Usrname = request.POST.get('User')
                BrwStatus = request.POST.get('UseStatus')
                Purpose = request.POST.get('Purpose')
                updatedic = {
                    "Btime": Btime, "NID": NID,
                    "BR_per_code": BR_per_code, "Usrname": Usrname, "Category": Category,
                    "Area": Area, "OAPcode": OAPcode, "OAP": OAP,
                    "Purpose": Purpose,
                    "BrwStatus": BrwStatus,
                             }
                # print(updatedic)
                if ChairCabinetLNV.objects.filter(NID=NID) and ChairCabinetLNV.objects.filter(id=id).first().NID != NID:
                    errMsgNumber = """統一編號已存在"""
                    # print(1)
                else:

                    try:
                        with transaction.atomic():
                            # print(2)
                            ChairCabinetLNV.objects.filter(id=id).update(**updatedic)
                            alert = 0
                    except:
                        alert = '此数据%s正被其他使用者编辑中...' % id

                # mock_data
                NID = request.POST.get('GYNumberSearch')
                BrwStatus = request.POST.get('UseStatusSearch')
                Category = request.POST.get('CategorySearch')
                BR_per_code = request.POST.get('NumberSearch')
                check_dic = {}
                if NID:
                    check_dic["NID"] = NID
                if BrwStatus:
                    check_dic["BrwStatus"] = BrwStatus
                if BR_per_code:
                    check_dic["BR_per_code"] = BR_per_code
                if Category:
                    check_dic["Category"] = Category

                if check_dic:
                    mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
                else:
                    mock_datalist = ChairCabinetLNV.objects.all()
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
                        {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                         "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                         "User": i.Usrname, "UserNumber": i.BR_per_code,

                         "Position": i.Area, "Purpose": i.Purpose,
                         "UseStatus": i.BrwStatus,
                         "CollectDate": Btime_str,
                         "Rtime": Rtime_str,
                         "Transefer_per_code": i.Transefer_per_code,
                         "Receive_per_code": i.Receive_per_code,
                         "Sign_per_code": i.Sign_per_code,
                         }
                    )
                selectGYNumber = [
                    # {"value": "DQA-C-001"}, {"value": "DQA-C-002"}, {"value": "DQA-C-004"},
                ]
                for i in ChairCabinetLNV.objects.all().values("NID").distinct().order_by("NID"):
                    selectGYNumber.append({"value": i["NID"]})

                selectNumber = [
                    # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
                ]
                for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
                    selectNumber.append({"value": i["account"], "number": i["CNname"]})
                # allUseStatus = [
                #     # "使用中", "申請中", "歸還中", "轉帳中", "接收中", "閑置中", "已損壞", "申請確認中", "歸還確認中", "轉帳確認中"
                # ]
                # for i in ChairCabinetLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
                #     allUseStatus.append(i["BrwStatus"])

                allCategory = [
                    # "椅子", "櫃子"
                ]
                for i in ChairCabinetLNV.objects.all().values("Category").distinct().order_by("Category"):
                    allCategory.append(i["Category"])
            if request.POST.get('isGetData') == "alertData":
                # id = request.POST.get('ID')
                NID = request.POST.get('UnifiedNumber')
                # print(NID)
                if ChairCabinetLNVHis.objects.filter(NID=NID):
                    for i in ChairCabinetLNVHis.objects.filter(NID=NID):
                        Btime_str = ''
                        if i.Btime:
                            Btime_str = str(i.Btime)
                        Rtime_str = ''
                        if i.Rtime:
                            Rtime_str = str(i.Rtime)
                        Changetime_str = ''
                        if i.Changetime:
                            Changetime_str = str(i.Changetime)

                        tableData.append({
                                "id": i.id, "GYNumber": i.NID, "Category": i.Category,
                                "Position": i.Area, "Purpose": i.Purpose,
                                "Borrower": i.OAP, "BorrowerNum": i.OAPcode,
                                "User": i.Usrname, "UserNumber": i.BR_per_code,
                                "UseStatus": i.BrwStatus,
                                "CollectDate": Btime_str, "ModifyDate": Rtime_str,  "Changetime": Changetime_str,
                                "Transefer_per_code": i.Transefer_per_code,
                                "Receive_per_code": i.Receive_per_code,
                                "Comments": i.Comments,
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
                    NID = responseData['GYNumber']
                    BrwStatus = responseData['UseStatus']
                    BR_per_code = responseData['Number']
                    Category = responseData['Category']

                    for i in responseData['params']:
                        # print(i)
                        ChairCabinetLNV.objects.get(id=i).delete()

                    # mock_data

                    check_dic = {}
                    if NID:
                        check_dic["NID"] = NID
                    if BrwStatus:
                        check_dic["BrwStatus"] = BrwStatus
                    if BR_per_code:
                        check_dic["BR_per_code"] = BR_per_code
                    if Category:
                        check_dic["Category"] = Category

                    if check_dic:
                        mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
                    else:
                        mock_datalist = ChairCabinetLNV.objects.all()
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
                            {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                             "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                             "User": i.Usrname, "UserNumber": i.BR_per_code,

                             "Position": i.Area, "Purpose": i.Purpose,
                             "UseStatus": i.BrwStatus,
                             "CollectDate": Btime_str,
                             "Rtime": Rtime_str,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per_code": i.Receive_per_code,
                             "Sign_per_code": i.Sign_per_code,
                             }
                        )
                    selectGYNumber = [
                        # {"value": "DQA-C-001"}, {"value": "DQA-C-002"}, {"value": "DQA-C-004"},
                    ]
                    for i in ChairCabinetLNV.objects.all().values("NID").distinct().order_by("NID"):
                        selectGYNumber.append({"value": i["NID"]})

                    selectNumber = [
                        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
                    ]
                    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
                        selectNumber.append({"value": i["account"], "number": i["CNname"]})
                    # allUseStatus = [
                    #     # "使用中", "申請中", "歸還中", "轉帳中", "接收中", "閑置中", "已損壞", "申請確認中", "歸還確認中", "轉帳確認中"
                    # ]
                    # for i in ChairCabinetLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
                    #     allUseStatus.append(i["BrwStatus"])

                    allCategory = [
                        # "椅子", "櫃子"
                    ]
                    for i in ChairCabinetLNV.objects.all().values("Category").distinct().order_by("Category"):
                        allCategory.append(i["Category"])
                if 'ExcelData' in str(request.body):
                    responseData = json.loads(request.body)
                    # print(responseData)
                    # print(responseData['historyYear'],type(responseData['historyYear']))

                    NID = responseData['GYNumber']
                    BrwStatus = responseData['UseStatus']
                    BR_per_code = responseData['Number']
                    Category = responseData['Category']

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
                            if key in headermodel_ChairCabinet.keys():
                                modeldata[headermodel_ChairCabinet[key]] = value
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
                        if 'Category' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，產品類別不能爲空
                                                                            """ % rownum
                            break
                        if 'Area' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，位置不能爲空
                                                                            """ % rownum
                            break
                        if 'Purpose' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，用途不能爲空
                                                                            """ % rownum
                            break
                        if 'BrwStatus' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，使用狀態不能爲空
                                                                            """ % rownum
                            break


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
                    for i in ChairCabinetLNV._meta.fields:
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
                            #     if key in headermodel_ChairCabinet.keys():
                            #         if headermodel_ChairCabinet[key] == "Predict_return" or headermodel_ChairCabinet[
                            #             key] == "Borrow_date" or headermodel_ChairCabinet[key] == "Return_date":
                            #             print(value)
                            #             modeldata[headermodel_ChairCabinet[key]] = value.split("/")[2] + "-" + \
                            #                                                        value.split("/")[0] + "-" + \
                            #                                                        value.split("/")[1]
                            #         else:
                            #             modeldata[headermodel_ChairCabinet[key]] = value
                            Check_dic = {
                                'NID': i['NID'],
                            }
                            # print(modeldata)
                            # print(i)
                            # Check_dic_Gantt['Test_Start'] = None  # 日期格式为空NULL不能用空字符
                            if ChairCabinetLNV.objects.filter(**Check_dic):#已经存在覆盖
                                pass
                                # ChairCabinetLNV.objects.filter(
                                #     **Check_dic).update(**i)
                            else:#新增
                                ChairCabinetLNV.objects.create(**i)
                        errMsg = '上傳成功'

                    # mock_data

                    check_dic = {}
                    if NID:
                        check_dic["NID"] = NID
                    if BrwStatus:
                        check_dic["BrwStatus"] = BrwStatus
                    if BR_per_code:
                        check_dic["BR_per_code"] = BR_per_code
                    if Category:
                        check_dic["Category"] = Category

                    if check_dic:
                        mock_datalist = ChairCabinetLNV.objects.filter(**check_dic)
                    else:
                        mock_datalist = ChairCabinetLNV.objects.all()
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
                            {"id": i.id, "GYNumber": i.NID, "Category": i.Category,
                             "BorrowerNum": i.OAPcode, "Borrower": i.OAP,
                             "User": i.Usrname, "UserNumber": i.BR_per_code,

                             "Position": i.Area, "Purpose": i.Purpose,
                             "UseStatus": i.BrwStatus,
                             "CollectDate": Btime_str,
                             "Rtime": Rtime_str,
                             "Transefer_per_code": i.Transefer_per_code,
                             "Receive_per_code": i.Receive_per_code,
                             "Sign_per_code": i.Sign_per_code,
                             }
                        )
                    selectGYNumber = [
                        # {"value": "DQA-C-001"}, {"value": "DQA-C-002"}, {"value": "DQA-C-004"},
                    ]
                    for i in ChairCabinetLNV.objects.all().values("NID").distinct().order_by("NID"):
                        selectGYNumber.append({"value": i["NID"]})

                    selectNumber = [
                        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
                    ]
                    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
                        selectNumber.append({"value": i["account"], "number": i["CNname"]})
                    # allUseStatus = [
                    #     # "使用中", "申請中", "歸還中", "轉帳中", "接收中", "閑置中", "已損壞", "申請確認中", "歸還確認中", "轉帳確認中"
                    # ]
                    # for i in ChairCabinetLNV.objects.all().values("BrwStatus").distinct().order_by("BrwStatus"):
                    #     allUseStatus.append(i["BrwStatus"])

                    allCategory = [
                        # "椅子", "櫃子"
                    ]
                    for i in ChairCabinetLNV.objects.all().values("Category").distinct().order_by("Category"):
                        allCategory.append(i["Category"])

                    # selectNumber = [
                    #     # {"value": "張宵凌", "number": "20795434"}, {"value": "劉婭茹", "number": "20720831"},
                    # ]
                    # for i in ChairCabinetLNV.objects.all().values("Usrname", "BR_per_code").distinct().order_by(
                    #         "BR_per_code"):
                    #     selectNumber.append({"value": i["Usrname"], "number": i["BR_per_code"]})

        data = {
            "content": mock_data,
            "tableData": tableData,
            "selectGYNumber": selectGYNumber,
            "selectNumber": selectNumber,
            "allUseStatus": allUseStatus,
            "allCategory": allCategory,
            "errMsg": errMsg,
            "errMsgNumber": errMsgNumber,
        }
        # print(data)
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'ChairCabinetMS/M_edit.html', locals())


