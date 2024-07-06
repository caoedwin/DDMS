from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime,os, json, requests
from requests_ntlm import HttpNtlmAuth
from django.http import JsonResponse
from .models import AdapterPowerCodeBR, PICS
from service.init_permission import init_permission
from DMS import settings
from django.core.mail import send_mail, send_mass_mail
from django.core.mail import EmailMultiAlternatives
from app01 import tasks
from app01.models import UserInfo
def mailattach(subject,from_email, to_email, message, attachname):
    # subject 主题 content 内容 to_addr 是一个列表，发送给哪些人
    # msg = EmailMultiAlternatives('邮件标题', '邮件内容', '发送方', ['接收方'])
    msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
    msg.content_subtype = "html"
    # 添加附件（可选）
    # msg.attach_file('test.txt')
    msg.attach_file(attachname)
    # 发送
    msg.send()

def send_email(subject,from_email, to_email, message):
    #send_mail 每次发邮件都会建立一个连接，发多封邮件时建立多个连接。而 send_mass_mail 是建立单个连接发送多封邮件，所以一次性发送多封邮件时 send_mass_mail 要优于 send_mail。
    # subject = 'C语言中文网链接'  # 主题
    # from_email = settings.EMAIL_FROM  # 发件人，在settings.py中已经配置
    # to_email = 'xxxxx@qq.com'  # 邮件接收者列表
    # # 发送的消息
    # message = 'c语言中文网欢迎你点击登录 http://c.biancheng.net/'  # 发送普通的消息使用的时候message
    # meg_html = '<a href="http://www.baidu.com">点击跳转</a>'  # 发送的是一个html消息 需要指定
    send_mail(subject, message, from_email, [to_email])
    # subject：邮件主题；
    # message：邮件正文内容；
    # from_email：发送邮件者；
    # recipient_list：邮件接受者列表；
    # html_message：带有标签格式的HTML文本。
    return HttpResponse('OK,邮件已经发送成功!')

def sendmass_email(messages):
    #我们还可以调用 mail 的 send_mass_mail 方法实现一次性发送多条消息，demo 如下：
    # message1 = ('Subject here', 'Here is the message', 'from@example.com', ['first@example.com', 'other@example.com'])
    # message2 = ('Another Subject', 'Here is another message', 'from@example.com', ['second@test.com'])
    # 接收元组作为参数
    # send_mass_mail((message1, message2), fail_silently=False)  # 开始发送多封邮件
    send_mass_mail(messages, fail_silently=False)  # fail_silentl运行异常的时候是否报错，默认为True不报错

def ProjectSyncview():
    print("Start")
    mock_data = []
    mock_datalist = AdapterPowerCodeBR.objects.all()
    for i in mock_datalist:
        Photolist = []
        for h in i.Photo.all():
            Photolist.append(
                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
        if i.Predict_return and not i.Return_date:
            if datetime.datetime.now().date() > i.Predict_return:
                Exceed_days = round(
                    float(
                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                            0]),
                    0)
            else:
                Exceed_days = ''
        else:
            Exceed_days = ''
        Predict_return_str = ''
        if i.Predict_return:
            Predict_return_str = str(i.Predict_return)
        else:
            Predict_return_str = ''
        Borrow_date_str = ''
        if i.Borrow_date:
            Borrow_date_str = str(i.Borrow_date)
        else:
            Borrow_date_str = ''
        Return_date_str = ''
        if i.Return_date:
            Return_date_str = str(i.Return_date)
        else:
            Return_date_str = ''
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
            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
             "Description": i.Description,
             "Power": i.Power,
             "Number": i.Number, "Location": i.Location,
             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
             "Customer": i.Customer,
             "Project_Code": i.Project_Code,
             "Phase": i.Phase,
             "OAP": i.OAP, "OAPcode": i.OAPcode,
             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per, "BR_per_code": i.BR_per_code,
             "Predict_return": Predict_return_str,
             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
             "Last_BR_per": i.Last_BR_per,
             "Last_Borrow_date": Last_Borrow_date_str,
             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
             "fileListO": Photolist},
        )
    # print(mock_data)
    for i in mock_data:
        # print(i)
        if i['Exceed_days']:
            Exceed_day = i['Exceed_days']
            devicechaoqi = i['Number']
            chaoqizhe = i['BR_per']

            subject = '【DMS】设备超期提醒'
            message = """Dear %s:
                        您的设备：%s, 已经超期%s， 请尽快处理
            """ % (chaoqizhe, devicechaoqi, Exceed_day)
            from_email = '416434871@qq.com'
            to_email = []
            if UserInfo.objects.filter(account=i['BR_per_code']).first():
                if UserInfo.objects.filter(account=i['BR_per_code']).first().email:
                    to_email.append(UserInfo.objects.filter(account=i['BR_per_code']).first().email)
                    message1 = (subject, message, from_email, to_email)
                    message2 = ('邮件标题2', '邮件标题2测试内容', '416434871@qq.com', ['brotherxd@126.com'])
                    messages = (
                        message1,
                        # message2
                    )
                    # print(message1)
                    # print(message2)
                    print(messages)
                    sendmass_email(messages)
    # importPrjResult = ImportProjectinfoFromDCT()
    # if True:
    #     return "OK"
    # else:
    #     return "无超期"

def LNVTUMINFOTotal():
    LNVTUNINfo = {
        # 'Adapter': {"Total": 10, "Bi": 3, "Detail": [{"Customer": "C38", "siteName": "CN55"}, ]},
        # 'PowerCode': {}
    }
    url = r'http://192.168.1.10/dct/api/ClientSvc/GetParts?siteName=CN55'
    requests.adapters.DEFAULT_RETRIES = 1
    # s = requests.session()
    # s.keep_alive = False  # 关闭多余连接
    # getTestSpec=requests.get(url)
    headers = {'Connection': 'close'}
    try:
        r = requests.get(url, headers=headers)
        getTestSpec = requests.get(url)
        # print (getTestSpec.url)
    except:
        # time.sleep(0.1)
        print("Can't connect to DCT Server")
        return 0
    targetURL = getTestSpec.url
    # url=r"http://127.0.0.1"

    url.split('\n')[0]
    # print url
    # 输入用户名和密码python requests实现windows身份验证登录
    try:
        getTestSpec = requests.get(targetURL, auth=HttpNtlmAuth('DCT\\administrator', 'DQA3`2018'))
    except:
        # time.sleep(0.1)
        print("try request agian")
        return 0
    # print(type(getTestSec.json()), getTestSpec.json())
    AdapterTotal = 0 #多少笔记录但不完全等同于多少给PN号
    AdapterTotalNum = 0
    AdapterDtail = []
    PowerCodeTotal = 0 #多少笔记录但不完全等同于多少给PN号
    PowerCodeTotalNum = 0
    PowerCodeDetail = []
    for i in getTestSpec.json():
        # print(i)
        if i["PN"][:6] == "PK1000":
            AdapterTotal += 1
            AdapterTotalNum += i['Qty']
            AdapterDtail.append(i)
        elif i["PN"][:6] == "GA0000":
            PowerCodeTotal += 1
            PowerCodeTotalNum += i['Qty']
            PowerCodeDetail.append(i)
    LNVTUNINfo["Adapter"] = {"Total": AdapterTotalNum, "Bi": AdapterTotal, "Detail": AdapterDtail}
    LNVTUNINfo["PowerCode"] = {"Total": PowerCodeTotalNum, "Bi": PowerCodeTotal, "Detail": PowerCodeDetail}

        # print(localPrjCre)

    return LNVTUNINfo

headermodel_Adapter = {
    '廠家': 'Changjia', 'MaterialPN': 'MaterialPN', 'Description': 'Description', '功率': 'Power', '編號': 'Number',
    'Model': 'Model', '品名': 'Pinming', '類別': 'Leibie',
    'Location': 'Location', '客戶別': 'Customer', 'ProjectCode': 'Project_Code', 'Phase': 'Phase', '掛賬人': 'OAP',
    '掛賬人工號': 'OAPcode',
    '設備狀態': 'Device_Status', '借還狀態': 'BR_Status', '借還人員': 'BR_per', '借還人員工號': 'BR_per_code', '預計歸還日期': 'Predict_return',
    '借用日期': 'Borrow_date', '歸還日期': 'Return_date',
}

@csrf_exempt
def BorrowedAdapter(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/BorrowedAdapter"
    # selectItem = {
    #     # "C38(NB)": [{"Changjia": "天丞", "PN": ["156", "656", "635"]},
    #     #             {"Changjia": "A", "PN": ["87356", "C(SIT)", "785"]},
    #     #             {"Changjia": "B", "PN": ["5", "C(SIT)", "456"]},
    #     #             {"Changjia": "C", "PN": ["8", "6", "INV"]}],
    #     # "C38(AIO)": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
    #     #              {"Changjia": "B", "PN": ["852", "C(SIT)", "INV"]},
    #     #              {"Changjia": "C", "PN": ["123", "C(SIT)", "INV"]},
    #     #              {"Changjia": "D", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
    #     # "A39": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
    #     #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
    #     #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
    #     #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
    #     # "T88(AIO)": [{"Project": "D", "PN": ["365", "C(SIT)", "INV"]},
    #     #              {"Project": "F", "PN": ["B(FVT)", "C(SIT)", "INV"]},
    #     #              {"Project": "C", "PN": ["56", "C(SIT)", "INV"]}]
    # }
    # powerOptions = [
    #     # "60W", "120W", "180W", "200W"
    # ]
    options = [
        # ["124356545", "43245332", "20564438", "tgvcertrhtgrf", "gfrtgf", "ygbtfews"],
        #        ["可借用", "續借確認中", "已借出", "歸還確認中", "借用確認中"]
               ]
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "", "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]
    # options = [
    #     # ["GLY5U", "FLY00", "GLA41"],
    #     #        ["B(FVT)", "C(SIT)"]
    # ]

    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "12345678"},
    ]
    for i in AdapterPowerCodeBR.objects.all().values('OAP', 'OAPcode').distinct().order_by(
            'OAPcode'):
        selectItem.append({"value": str(i['OAP']), "number": str(i["OAPcode"])})
    MaterialPNlist = []
    for i in AdapterPowerCodeBR.objects.all().values("MaterialPN").distinct().order_by("MaterialPN"):
        MaterialPNlist.append(i['MaterialPN'])
    BR_Statuslist = []
    for i in AdapterPowerCodeBR.objects.all().values("BR_Status").distinct().order_by("BR_Status"):
        BR_Statuslist.append(i['BR_Status'])
    options.append(MaterialPNlist)
    options.append(BR_Statuslist)
    # for i in AdapterPowerCodeBR.objects.all().values("Customer").distinct().order_by("Customer"):
    #     customerchajialist = []
    #     for j in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"]).values("Changjia").distinct().order_by(
    #             "Changjia"):
    #         changjiapnlist = []
    #         for k in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"], Changjia=j["Changjia"]).values(
    #                 "MaterialPN").distinct().order_by("MaterialPN"):
    #             changjiapnlist.append((k["MaterialPN"]))
    #         customerchajialist.append({"Changjia": j['Changjia'], "PN": changjiapnlist})
    #     selectItem[i["Customer"]] = customerchajialist
    # for i in AdapterPowerCodeBR.objects.all().values("Power").distinct().order_by("Power"):
    #     powerOptions.append(i['Power'])

    if request.method == "POST":
        if request.POST.get('isGetData') == 'first':
            # message1 = ('邮件标题1', '邮件标题1测试内容', '416434871@qq.com', ['brotherxd@126.com', 'edwin_cao@compal.com'])
            # message2 = ('邮件标题2', '邮件标题2测试内容', '416434871@qq.com', ['brotherxd@126.com'])
            # messages = (message1, message2)
            # sendmass_email(messages)
            # mock_data
            # res = tasks.ProjectSync.delay()
            # 任务逻辑
            # ProjectSyncview()

            # mock_datalist = AdapterPowerCodeBR.objects.all()
            mock_datalist = AdapterPowerCodeBR.objects.filter(BR_Status='可借用')
            for i in mock_datalist:
                Photolist = []
                for h in i.Photo.all():
                    Photolist.append(
                        {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                if i.Predict_return and not i.Return_date:
                    if datetime.datetime.now().date() > i.Predict_return:
                        Exceed_days = round(
                            float(
                                str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                    0]),
                            0)
                    else:
                        Exceed_days = ''
                else:
                    Exceed_days = ''
                Predict_return_str = ''
                if i.Predict_return:
                    Predict_return_str = str(i.Predict_return)
                else:
                    Predict_return_str = ''
                Borrow_date_str = ''
                if i.Borrow_date:
                    Borrow_date_str = str(i.Borrow_date)
                else:
                    Borrow_date_str = ''
                Return_date_str = ''
                if i.Return_date:
                    Return_date_str = str(i.Return_date)
                else:
                    Return_date_str = ''
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
                    {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                     "Description": i.Description,
                     "Power": i.Power,
                     "Number": i.Number, "Location": i.Location,
                     "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                     "Customer": i.Customer,
                     "Project_Code": i.Project_Code,
                     "Phase": i.Phase,
                     "OAP": i.OAP, "OAPcode": i.OAPcode,
                     "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                     "Predict_return": Predict_return_str,
                     "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                     "Last_BR_per": i.Last_BR_per,
                     "Last_Borrow_date": Last_Borrow_date_str,
                     "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                     "fileListO": Photolist},
                )
            Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
            kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
            jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
            guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        if request.POST.get('isGetData') == 'SEARCH':
            checkAdaPow = {}
            OAPNumsearch = request.POST.get('OAPNum')
            if OAPNumsearch and OAPNumsearch != "All":
                checkAdaPow['OAPcode'] = OAPNumsearch
            Changjiasearch = request.POST.get('Changjia')
            if Changjiasearch and Changjiasearch != "All":
                checkAdaPow['Changjia'] = Changjiasearch
            Customerserach = request.POST.get('Customer')
            if Customerserach and Customerserach != "All":
                checkAdaPow['Customer'] = Customerserach
            PNsearch = request.POST.get('PN')
            if PNsearch and PNsearch != "All":
                checkAdaPow['MaterialPN'] = PNsearch
            Powersearch = request.POST.get('Power')
            if Powersearch and Powersearch != "All":
                checkAdaPow['Power'] = Powersearch
            BR_Status = request.POST.get('Status')
            if BR_Status and BR_Status != "All":
                checkAdaPow['BR_Status'] = BR_Status

            # mock_data
            if checkAdaPow:
                mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
            else:
                mock_datalist = AdapterPowerCodeBR.objects.all()
            for i in mock_datalist:
                Photolist = []
                for h in i.Photo.all():
                    Photolist.append(
                        {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                if i.Predict_return and not i.Return_date:
                    if datetime.datetime.now().date() > i.Predict_return:
                        Exceed_days = round(
                            float(
                                str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                    0]),
                            0)
                    else:
                        Exceed_days = ''
                else:
                    Exceed_days = ''
                Predict_return_str = ''
                if i.Predict_return:
                    Predict_return_str = str(i.Predict_return)
                else:
                    Predict_return_str = ''
                Borrow_date_str = ''
                if i.Borrow_date:
                    Borrow_date_str = str(i.Borrow_date)
                else:
                    Borrow_date_str = ''
                Return_date_str = ''
                if i.Return_date:
                    Return_date_str = str(i.Return_date)
                else:
                    Return_date_str = ''
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
                    {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                     "Description": i.Description,
                     "Power": i.Power,
                     "Number": i.Number, "Location": i.Location,
                     "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                     "Customer": i.Customer,
                     "Project_Code": i.Project_Code,
                     "Phase": i.Phase,
                     "OAP": i.OAP,  "OAPcode": i.OAPcode,
                     "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                     "Predict_return": Predict_return_str,
                     "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                     "Last_BR_per": i.Last_BR_per,
                     "Last_Borrow_date": Last_Borrow_date_str,
                     "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                     "fileListO": Photolist},
                )
            Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
            kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
            jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
            guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        if request.POST.get('isGetData') == 'BORROW':
            checkAdaPow = {}
            Changjiasearch = request.POST.get('Changjia')
            if Changjiasearch and Changjiasearch != "All":
                checkAdaPow['Changjia'] = Changjiasearch
            Customerserach = request.POST.get('Customer')
            if Customerserach and Customerserach != "All":
                checkAdaPow['Customer'] = Customerserach
            PNsearch = request.POST.get('PN')
            if PNsearch and PNsearch != "All":
                checkAdaPow['MaterialPN'] = PNsearch
            Powersearch = request.POST.get('Power')
            if Powersearch and Powersearch != "All":
                checkAdaPow['Power'] = Powersearch
            BR_Status = request.POST.get('Status')
            if BR_Status and BR_Status != "All":
                checkAdaPow['BR_Status'] = BR_Status
            BorrowedID = request.POST.get('BorrowId')
            # print(BorrowedID, type(BorrowedID))
            # print(json.loads(BorrowedID))
            # print(BorrowedID.split(','))
            updatedic = {'Project_Code': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                         'BR_Status': '預定確認', 'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'),
                         'Predict_return': request.POST.get('Predict_return'), 'Borrow_date': None, 'Return_date': None, }
            # print(updatedic)
            for i in BorrowedID.split(','):
                # print(i)
                try:
                    with transaction.atomic():
                        # print(updatedic)
                        AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                        alert = 0
                except:
                    # print('2')
                    alert = '此数据%s正被其他使用者编辑中...' % i

            # mock_data
            if checkAdaPow:
                mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
            else:
                mock_datalist = AdapterPowerCodeBR.objects.all()
            for i in mock_datalist:
                Photolist = []
                for h in i.Photo.all():
                    Photolist.append(
                        {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                if i.Predict_return and not i.Return_date:
                    if datetime.datetime.now().date() > i.Predict_return:
                        Exceed_days = round(
                            float(
                                str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                    0]),
                            0)
                    else:
                        Exceed_days = ''
                else:
                    Exceed_days = ''
                Predict_return_str = ''
                if i.Predict_return:
                    Predict_return_str = str(i.Predict_return)
                else:
                    Predict_return_str = ''
                Borrow_date_str = ''
                if i.Borrow_date:
                    Borrow_date_str = str(i.Borrow_date)
                else:
                    Borrow_date_str = ''
                Return_date_str = ''
                if i.Return_date:
                    Return_date_str = str(i.Return_date)
                else:
                    Return_date_str = ''
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
                    {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                     "Description": i.Description,
                     "Power": i.Power,
                     "Number": i.Number, "Location": i.Location,
                     "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                     "Customer": i.Customer,
                     "Project_Code": i.Project_Code,
                     "Phase": i.Phase,
                     "OAP": i.OAP,  "OAPcode": i.OAPcode,
                     "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                     "Predict_return": Predict_return_str,
                     "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                     "Last_BR_per": i.Last_BR_per,
                     "Last_Borrow_date": Last_Borrow_date_str,
                     "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                     "fileListO": Photolist},
                )
            Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
            kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
            jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
            guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "selectItem": selectItem,
            # "powerOptions": powerOp   tions,
            "content": mock_data,
            "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/BorrowedAdapter.html', locals())

# @csrf_exempt
# def BorrowedPowerCode(request):
#     if not request.session.get('is_login', None):
#         # print(request.session.get('is_login', None))
#         return redirect('/login/')
#     weizhi = "AdapterPowerCode/BorrowedPowerCode"
#     return render(request, 'AdapterPowerCode/BorrowedPowerCode.html', locals())

@csrf_exempt
def R_Borrowed(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/R_Borrowed"
    selectItem = {
        # "C38(NB)": [{"Changjia": "天丞", "PN": ["156", "656", "635"]},
        #             {"Changjia": "A", "PN": ["87356", "C(SIT)", "785"]},
        #             {"Changjia": "B", "PN": ["5", "C(SIT)", "456"]},
        #             {"Changjia": "C", "PN": ["8", "6", "INV"]}],
        # "C38(AIO)": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Changjia": "B", "PN": ["852", "C(SIT)", "INV"]},
        #              {"Changjia": "C", "PN": ["123", "C(SIT)", "INV"]},
        #              {"Changjia": "D", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "A39": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "T88(AIO)": [{"Project": "D", "PN": ["365", "C(SIT)", "INV"]},
        #              {"Project": "F", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Project": "C", "PN": ["56", "C(SIT)", "INV"]}]
    }
    powerOptions = [
        # "60W", "120W", "180W", "200W"
                    ]
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]
    options = [
        # ["GLY5U", "FLY00", "GLA41"],
        #        ["B(FVT)", "C(SIT)"]
    ]
    for i in AdapterPowerCodeBR.objects.all().values("Customer").distinct().order_by("Customer"):
        customerchajialist = []
        for j in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"]).values("Changjia").distinct().order_by("Changjia"):
            changjiapnlist = []
            for k in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"],Changjia=j["Changjia"]).values("MaterialPN").distinct().order_by("MaterialPN"):
                changjiapnlist.append((k["MaterialPN"]))
            customerchajialist.append({"Changjia": j['Changjia'], "PN": changjiapnlist})
        selectItem[i["Customer"]] = customerchajialist
    for i in AdapterPowerCodeBR.objects.all().values("Power").distinct().order_by("Power"):
        powerOptions.append(i['Power'])

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                # print(request.session.get('CNname'),request.session.get('account'))
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_per=request.session.get('CNname_DMS'), BR_per_code=request.session.get('account_DMS'), BR_Status='已借出')
                # print(mock_datalist)
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP,  "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '已借出'}
                Changjiasearch = request.POST.get('Changjia')
                # print(len(Changjiasearch))
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customer')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PN')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Power')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch

                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    # print(len(i.Changjia))
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP,  "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'RENEW':
                checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '已借出'}
                Changjiasearch = request.POST.get('Changjia')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customer')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PN')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Power')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch
                RenewId = request.POST.get('RenewId')
                # print(BorrowedID, type(BorrowedID))
                # print(json.loads(BorrowedID))
                # print(BorrowedID.split(','))
                updatedic = {'Project_Code': request.POST.get('Project'), 'Phase': request.POST.get('Phase'),
                             'BR_Status': '續借確認', 'BR_per': request.session.get('CNname_DMS'),'BR_per_code': request.session.get('account_DMS'),
                             'Predict_return': request.POST.get('Predict_return'), 'Borrow_date': None,
                             'Return_date': None, }
                # print(updatedic)
                for i in RenewId.split(','):
                    updatedic['Last_BR_per'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per
                    updatedic['Last_BR_per_code'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per_code
                    updatedic['Last_Predict_return'] = AdapterPowerCodeBR.objects.filter(id=i).first().Predict_return
                    updatedic['Last_Borrow_date'] = AdapterPowerCodeBR.objects.filter(id=i).first().Borrow_date
                    updatedic['Last_Return_date'] = datetime.datetime.now().date()
                    try:
                        with transaction.atomic():
                            AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                            alert = 0
                    except:
                        alert = '此数据%s正被其他使用者编辑中...' % i

                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP,  "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '已借出'}
                    Changjiasearch = responseData['Changjia']
                    if Changjiasearch and Changjiasearch != "All":
                        checkAdaPow['Changjia'] = Changjiasearch
                    Customerserach = responseData['Customer']
                    if Customerserach and Customerserach != "All":
                        checkAdaPow['Customer'] = Customerserach
                    PNsearch = responseData['PN']
                    if PNsearch and PNsearch != "All":
                        checkAdaPow['MaterialPN'] = PNsearch
                    Powersearch = responseData['Power']
                    if Powersearch and Powersearch != "All":
                        checkAdaPow['Power'] = Powersearch
                    updatedic = {'BR_Status': '歸還確認',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['ReturnId']:
                        try:
                            with transaction.atomic():
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    print(checkAdaPow)
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP,  "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "selectItem": selectItem,
            "powerOptions": powerOptions,
            "content": mock_data,
            "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/R_Borrowed.html', locals())

@csrf_exempt
def R_Return(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/R_Return"
    selectItem = {
        # "C38(NB)": [{"Changjia": "天丞", "PN": ["156", "656", "635"]},
        #             {"Changjia": "A", "PN": ["87356", "C(SIT)", "785"]},
        #             {"Changjia": "B", "PN": ["5", "C(SIT)", "456"]},
        #             {"Changjia": "C", "PN": ["8", "6", "INV"]}],
        # "C38(AIO)": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Changjia": "B", "PN": ["852", "C(SIT)", "INV"]},
        #              {"Changjia": "C", "PN": ["123", "C(SIT)", "INV"]},
        #              {"Changjia": "D", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "A39": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "T88(AIO)": [{"Project": "D", "PN": ["365", "C(SIT)", "INV"]},
        #              {"Project": "F", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Project": "C", "PN": ["56", "C(SIT)", "INV"]}]
    }
    powerOptions = [
        # "60W", "120W", "180W", "200W"
    ]
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]

    for i in AdapterPowerCodeBR.objects.all().values("Customer").distinct().order_by("Customer"):
        customerchajialist = []
        for j in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"]).values("Changjia").distinct().order_by(
                "Changjia"):
            changjiapnlist = []
            for k in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"], Changjia=j["Changjia"]).values(
                    "MaterialPN").distinct().order_by("MaterialPN"):
                changjiapnlist.append((k["MaterialPN"]))
            customerchajialist.append({"Changjia": j['Changjia'], "PN": changjiapnlist})
        selectItem[i["Customer"]] = customerchajialist
    for i in AdapterPowerCodeBR.objects.all().values("Power").distinct().order_by("Power"):
        powerOptions.append(i['Power'])

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_per=request.session.get('CNname_DMS'), BR_per_code=request.session.get('account_DMS'), BR_Status='歸還確認')
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '歸還確認'}
                Changjiasearch = request.POST.get('Changjia')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customer')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PN')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Power')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch

                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '歸還確認'}
                    Changjiasearch = responseData['Changjia']
                    if Changjiasearch and Changjiasearch != "All":
                        checkAdaPow['Changjia'] = Changjiasearch
                    Customerserach = responseData['Customer']
                    if Customerserach and Customerserach != "All":
                        checkAdaPow['Customer'] = Customerserach
                    PNsearch = responseData['PN']
                    if PNsearch and PNsearch != "All":
                        checkAdaPow['MaterialPN'] = PNsearch
                    Powersearch = responseData['Power']
                    if Powersearch and Powersearch != "All":
                        checkAdaPow['Power'] = Powersearch
                    updatedic = {'BR_Status': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['ReturnId']:
                        try:
                            with transaction.atomic():
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    # print(checkAdaPow)
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP,  "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "selectItem": selectItem,
            "powerOptions": powerOptions,
            "content": mock_data,
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/R_Return.html', locals())

@csrf_exempt
def R_Keep(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/R_Keep"
    selectItem = {
        # "C38(NB)": [{"Changjia": "天丞", "PN": ["156", "656", "635"]},
        #             {"Changjia": "A", "PN": ["87356", "C(SIT)", "785"]},
        #             {"Changjia": "B", "PN": ["5", "C(SIT)", "456"]},
        #             {"Changjia": "C", "PN": ["8", "6", "INV"]}],
        # "C38(AIO)": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Changjia": "B", "PN": ["852", "C(SIT)", "INV"]},
        #              {"Changjia": "C", "PN": ["123", "C(SIT)", "INV"]},
        #              {"Changjia": "D", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "A39": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "T88(AIO)": [{"Project": "D", "PN": ["365", "C(SIT)", "INV"]},
        #              {"Project": "F", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Project": "C", "PN": ["56", "C(SIT)", "INV"]}]
    }
    powerOptions = [
        # "60W", "120W", "180W", "200W"
                    ]
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
        ]

    for i in AdapterPowerCodeBR.objects.all().values("Customer").distinct().order_by("Customer"):
        customerchajialist = []
        for j in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"]).values("Changjia").distinct().order_by(
                "Changjia"):
            changjiapnlist = []
            for k in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"], Changjia=j["Changjia"]).values(
                    "MaterialPN").distinct().order_by("MaterialPN"):
                changjiapnlist.append((k["MaterialPN"]))
            customerchajialist.append({"Changjia": j['Changjia'], "PN": changjiapnlist})
        selectItem[i["Customer"]] = customerchajialist
    for i in AdapterPowerCodeBR.objects.all().values("Power").distinct().order_by("Power"):
        powerOptions.append(i['Power'])

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_per=request.session.get('CNname_DMS'), BR_per_code=request.session.get('account_DMS'),BR_Status='續借確認')
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP,  "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '續借確認'}
                Changjiasearch = request.POST.get('Changjia')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customer')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PN')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Power')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch

                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '續借確認'}
                    Changjiasearch = responseData['Changjia']
                    if Changjiasearch and Changjiasearch != "All":
                        checkAdaPow['Changjia'] = Changjiasearch
                    Customerserach = responseData['Customer']
                    if Customerserach and Customerserach != "All":
                        checkAdaPow['Customer'] = Customerserach
                    PNsearch = responseData['PN']
                    if PNsearch and PNsearch != "All":
                        checkAdaPow['MaterialPN'] = PNsearch
                    Powersearch = responseData['Power']
                    if Powersearch and Powersearch != "All":
                        checkAdaPow['Power'] = Powersearch
                    updatedic = {'BR_Status': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['Renew']:
                        updatedic['BR_per'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_BR_per
                        updatedic['BR_per_code'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_BR_per_code
                        updatedic['Predict_return'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_Predict_return
                        updatedic['Borrow_date'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Return_date'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_Return_date
                        try:
                            with transaction.atomic():
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    # print(checkAdaPow)
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "selectItem": selectItem,
            "powerOptions": powerOptions,
            "content": mock_data,
            # "options": options
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/R_Keep.html', locals())

@csrf_exempt
def R_Destine(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/R_Destine"
    selectItem = {
        # "C38(NB)": [{"Changjia": "天丞", "PN": ["156", "656", "635"]},
        #             {"Changjia": "A", "PN": ["87356", "C(SIT)", "785"]},
        #             {"Changjia": "B", "PN": ["5", "C(SIT)", "456"]},
        #             {"Changjia": "C", "PN": ["8", "6", "INV"]}],
        # "C38(AIO)": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Changjia": "B", "PN": ["852", "C(SIT)", "INV"]},
        #              {"Changjia": "C", "PN": ["123", "C(SIT)", "INV"]},
        #              {"Changjia": "D", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "A39": [{"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #         {"Changjia": "A", "PN": ["B(FVT)", "C(SIT)", "INV"]}],
        # "T88(AIO)": [{"Project": "D", "PN": ["365", "C(SIT)", "INV"]},
        #              {"Project": "F", "PN": ["B(FVT)", "C(SIT)", "INV"]},
        #              {"Project": "C", "PN": ["56", "C(SIT)", "INV"]}]
    }
    powerOptions = [
        # "60W", "120W", "180W", "200W"
    ]
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]

    for i in AdapterPowerCodeBR.objects.all().values("Customer").distinct().order_by("Customer"):
        customerchajialist = []
        for j in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"]).values("Changjia").distinct().order_by(
                "Changjia"):
            changjiapnlist = []
            for k in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"], Changjia=j["Changjia"]).values(
                    "MaterialPN").distinct().order_by("MaterialPN"):
                changjiapnlist.append((k["MaterialPN"]))
            customerchajialist.append({"Changjia": j['Changjia'], "PN": changjiapnlist})
        selectItem[i["Customer"]] = customerchajialist
    for i in AdapterPowerCodeBR.objects.all().values("Power").distinct().order_by("Power"):
        powerOptions.append(i['Power'])

    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_per=request.session.get('CNname_DMS'), BR_per_code=request.session.get('account_DMS'), BR_Status='預定確認')
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '預定確認'}
                Changjiasearch = request.POST.get('Changjia')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customer')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PN')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Power')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch

                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    responseData = json.loads(request.body)
                    checkAdaPow = {'BR_per': request.session.get('CNname_DMS'), 'BR_per_code': request.session.get('account_DMS'), 'BR_Status': '預定確認'}
                    Changjiasearch = responseData['Changjia']
                    if Changjiasearch and Changjiasearch != "All":
                        checkAdaPow['Changjia'] = Changjiasearch
                    Customerserach = responseData['Customer']
                    if Customerserach and Customerserach != "All":
                        checkAdaPow['Customer'] = Customerserach
                    PNsearch = responseData['PN']
                    if PNsearch and PNsearch != "All":
                        checkAdaPow['MaterialPN'] = PNsearch
                    Powersearch = responseData['Power']
                    if Powersearch and Powersearch != "All":
                        checkAdaPow['Power'] = Powersearch
                    updatedic = {'BR_Status': '可借用',
                                 # 'BR_per': request.session.get('CNname'),
                                 'Predict_return': None,
                                 # 'Borrow_date': None,'Return_date': None,
                                 }
                    for i in responseData['BookId']:
                        updatedic['BR_per'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_BR_per
                        updatedic['BR_per_code'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_BR_per_code
                        # updatedic['Predict_return'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_Predict_return
                        updatedic['Borrow_date'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_Borrow_date
                        updatedic['Return_date'] = AdapterPowerCodeBR.objects.filter(id=i).first().Last_Return_date
                        try:
                            with transaction.atomic():
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中

        data = {
            "selectItem": selectItem,
            "powerOptions": powerOptions,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/R_Destine.html', locals())

@csrf_exempt
def M_Borrow(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/M_Borrow"
    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "12345678"},
    ]
    for i in AdapterPowerCodeBR.objects.filter(BR_Status='預定確認').values('BR_per', 'BR_per_code').distinct().order_by('BR_per_code'):
        selectItem.append({"value": i['BR_per'], "number": i["BR_per_code"]})
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_Status='預定確認', OAPcode=request.session.get('account_DMS'),)
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_Status': '預定確認', 'OAPcode': request.session.get('account_DMS')}
                if request.POST.get('BorrowerNum'):
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
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP,  "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    checkAdaPow = {'BR_Status': '預定確認'}
                    # if responseData['Borrower']:
                    #     checkAdaPow['BR_per'] = responseData['Borrower']
                    if "BorrowerNum" in responseData.keys():
                        checkAdaPow['BR_per'] = responseData['BorrowerNum']

                    updatedic = {'BR_Status': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Borrow_date': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }
                    # print(updatedic)
                    for i in responseData['params']:
                        # print(i)
                        updatedic['Last_BR_per'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per
                        updatedic['Last_BR_per_code'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_Predict_return'] = AdapterPowerCodeBR.objects.filter(id=i).first().Predict_return
                        updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        updatedic['OAP'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per
                        updatedic['OAPcode'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per_code
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "selectItem": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/M_Borrow.html', locals())

@csrf_exempt
def M_Return(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/R_Destine"
    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "12345678"},
    ]
    for i in AdapterPowerCodeBR.objects.filter(BR_Status='歸還確認').values('BR_per', 'BR_per_code').distinct().order_by('BR_per_code'):
        selectItem.append({"value": i['BR_per'], "number": i["BR_per_code"]})
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_Status='歸還確認', OAPcode=request.session.get('account_DMS'),)
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_Status': '歸還確認', 'OAPcode': request.session.get('account_DMS')}
                if request.POST.get('BorrowerNum'):
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
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    checkAdaPow = {'BR_Status': '歸還確認'}
                    # if responseData['Borrower']:
                    #     checkAdaPow['BR_per'] = responseData['Borrower']
                    if "BorrowerNum" in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['BorrowerNum']

                    updatedic = {'BR_Status': '可借用',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 # 'Borrow_date': datetime.datetime.now().date(),
                                 'Return_date': datetime.datetime.now().date(),
                                 }
                    for i in responseData['params']:
                        # updatedic['Last_BR_per'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per
                        # updatedic['Last_Predict_return'] = AdapterPowerCodeBR.objects.filter(id=i).first().Predict_return
                        # updatedic['Last_Borrow_date'] = datetime.datetime.now().date(),
                        updatedic['Last_Return_date'] = datetime.datetime.now().date()
                        try:
                            with transaction.atomic():
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                alert = 0
                        except:
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "select": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/M_Return.html', locals())

@csrf_exempt
def M_upload(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/M_upload"
    return render(request, 'AdapterPowerCode/M_upload.html', locals())

@csrf_exempt
def M_edit(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/M_upload"
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "PK10001GM20",
        #  "Description": "AC ADAP LITE ON PA-1650-41LR 65W 2P A39", "Power": "65W", "Number": "GM20-1",
        #  "Location": "A1-1",
        #  "Customer": "C38(NB)", "Project_Code": "GLMA0", "Phase": "NPI", "OAP": "姚麗麗", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "姚麗麗",
        #  "Predict_return": "2020/12/23", "Borrow_date": "2020/10/25", "Return_date": "2020/10/25", "Exceed_days": "2"},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]
    # selectItem = [
    #     {"value": "姚麗麗"}, {"value": "張亞萍"}, {"value": " 錢剛"}, {"value": "洪大慶"}
    # ]

    selectItem = {
        # "C38(NB)": [{"Changjia": "Liteon", "PN": ["PK10001GM20", "PK10001GI20", "PK10001GN00", "PK10001GJ00"]},
        #     {"Changjia": "API", "PN": ["PK10001GN00", "PK10001GI20"]},
        #     {"Changjia": "Delta", "PN": ["PK10001GJ00"]}],
    }

    # selectOption = {
    #     "Liteon": [{"PN": "PK10001GM20"}, {"PN": "PK10001GI20"}, {"PN": "PK10001GN00"}, {"PN": "PK10001GJ00"}],
    #     "Delta": [{"PN": "PK10001GI20"}, {"PN": "PK10001GN00"}],
    #     "API": [{"PN": "PK10001GJ00"}],
    # }

    selectPower = [
        # "45W", "65W", "95W", "120W", "150W"
    ]

    sectionCustomer = [
        "C38(NB)", "T88(AIO)", "C38(AIO)", "A39"
    ]
    sectionPhase = [
        "NPI",
    ]
    sectionStatus = [
        "已借出", "可借用", "預定確認", "歸還確認", "續借確認", "Close"
    ]
    sectionDeviceStatus = [
        "固定設備", "已損壞", '正常',
    ]
    sectionOAP = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "123456789"},
    ]

    sectionNumber = [
        # {"value": "GM20-1"}, {"value": "GM20-009"},
    ]

    for i in AdapterPowerCodeBR.objects.all().values('OAP', 'OAPcode').distinct().order_by(
            'OAPcode'):
        sectionOAP.append({"value": str(i['OAP']), "number": str(i["OAPcode"])})

    for i in AdapterPowerCodeBR.objects.all().values("Number").distinct().order_by(
            'Number'):
        sectionNumber.append({"value": str(i['Number']), "number": str(i["Number"])})

    for i in AdapterPowerCodeBR.objects.all().values("Customer").distinct().order_by("Customer"):
        customerchajialist = []
        for j in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"]).values("Changjia").distinct().order_by("Changjia"):
            changjiapnlist = []
            for k in AdapterPowerCodeBR.objects.filter(Customer=i["Customer"],Changjia=j["Changjia"]).values("MaterialPN").distinct().order_by("MaterialPN"):
                changjiapnlist.append((k["MaterialPN"]))
            customerchajialist.append({"Changjia": j['Changjia'], "PN": changjiapnlist})
        selectItem[i["Customer"]] = customerchajialist
    for i in AdapterPowerCodeBR.objects.all().values("Power").distinct().order_by("Power"):
        selectPower.append(i['Power'])

    Lent = ''  # 已借出
    kejieyong = ''  # 可借用
    jieyongyuding = ''  # 預定確認中
    guihuanqueren = ''  # 歸還確認中
    errMsg = ''
    errMsgNumber = ''#新增弹框
    # print(request.method)
    if request.method == "POST":
        # print(request.POST)
        # print(request.body)
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "BR_per_code": i.BR_per_code,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
                # print(mock_data)
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {}
                Changjiasearch = request.POST.get('Changjia')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customer')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PN')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Power')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch
                Number = request.POST.get('Number')
                if Number and Number != "All":
                    checkAdaPow['Number'] = Number
                OAPcode = request.POST.get('OAPNum')
                if OAPcode and OAPcode != "All":
                    checkAdaPow['OAPcode'] = OAPcode

                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "BR_per_code": i.BR_per_code,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('action') == "submit":
                Customer = request.POST.get('Customer')
                Description = request.POST.get('Description')
                MaterialPN = request.POST.get('MaterialPN')
                Power = request.POST.get('Power')
                OAP = request.POST.get('OAP')
                OAPcode = request.POST.get('OAPcode')
                Changjia = request.POST.get('Changjia')
                Number = request.POST.get('Number')
                Location = request.POST.get('Location')
                Model = request.POST.get('Model')
                Pinming = request.POST.get('Pinming')
                Leibie = request.POST.get('Leibie')
                Photo = request.FILES.getlist("Image", "")
                checkAdaPow = {}
                Changjiasearch = request.POST.get('Changjiasearch')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('Customerserach')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PNsearch')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('Powersearch')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch
                createdic = {
                     'Customer': Customer, 'Description': Description, 'MaterialPN': MaterialPN,
                     'Power': Power, 'OAP': OAP, 'OAPcode': OAPcode, 'Changjia': Changjia, 'Number': Number, 'Location': Location,
                     'Model': Model, 'Pinming': Pinming, 'Leibie': Leibie
                             }
                if AdapterPowerCodeBR.objects.filter(Number=Number):
                    errMsgNumber = """编号已存在"""
                else:
                    # print(createdic)
                    AdapterPowerCodeBR.objects.create(**createdic)
                    # print(Photo)
                    if Photo:
                        for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                            # print(f)
                            empt = PICS()
                            # 增加其他字段应分别对应填写
                            empt.single = f
                            empt.pic = f
                            empt.save()
                            AdapterPowerCodeBR.objects.filter(Number=Number).first().Photo.add(empt)


                # mock_data
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "BR_per_code": i.BR_per_code,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('action') == "submit1":
                id = request.POST.get('id')
                Customer = request.POST.get('Customer')
                Description = request.POST.get('Description')
                MaterialPN = request.POST.get('MaterialPN')
                Power = request.POST.get('Power')
                OAP = request.POST.get('OAP')
                OAPcode = request.POST.get('OAPcode')
                Changjia = request.POST.get('Changjia')
                Number = request.POST.get('Number')
                Location = request.POST.get('Location')
                Model = request.POST.get('Model')
                Pinming = request.POST.get('Pinming')
                Leibie = request.POST.get('Leibie')
                Device_Status = request.POST.get('Device_Status')
                if Device_Status == 'null':
                    Device_Status = ''
                Project_Code = request.POST.get('ProjectCode')
                Phase = request.POST.get('Phase')
                BR_Status = request.POST.get('BR_Status')
                if BR_Status == 'null':
                    BR_Status = ''
                BR_per = request.POST.get('BR_per')
                BR_per_code = request.POST.get('BR_per_code')
                Borrow_date = request.POST.get('Borrow_date')
                if not Borrow_date or Borrow_date == 'null-null-null':
                    Borrow_date = None #日期爲空
                Predict_return = request.POST.get('Predict_return')
                if not Predict_return or Predict_return == 'null-null-null':
                    Predict_return = None #日期爲空
                Return_date = request.POST.get('Return_date')
                if not Return_date or Return_date == 'null-null-null':
                    Return_date = None #日期爲空
                Photo = request.FILES.getlist("Image", "")
                checkAdaPow = {}
                Changjiasearch = request.POST.get('ChangjiaSearch')
                if Changjiasearch and Changjiasearch != "All":
                    checkAdaPow['Changjia'] = Changjiasearch
                Customerserach = request.POST.get('CustomerSerach')
                if Customerserach and Customerserach != "All":
                    checkAdaPow['Customer'] = Customerserach
                PNsearch = request.POST.get('PNSearch')
                if PNsearch and PNsearch != "All":
                    checkAdaPow['MaterialPN'] = PNsearch
                Powersearch = request.POST.get('PowerSearch')
                if Powersearch and Powersearch != "All":
                    checkAdaPow['Power'] = Powersearch
                updatedic = {
                     'Customer': Customer, 'Description': Description, 'MaterialPN': MaterialPN,
                     'Power': Power, 'OAP': OAP, 'OAPcode': OAPcode, 'Changjia': Changjia, 'Number': Number, 'Location': Location,
                    'Model': Model, 'Pinming': Pinming, 'Leibie': Leibie,
                    'Device_Status': Device_Status, 'Project_Code': Project_Code, 'Phase': Phase, 'BR_Status': BR_Status,
                    'BR_per': BR_per, 'BR_per_code': BR_per_code, 'Borrow_date': Borrow_date, 'Predict_return': Predict_return,
                    'Return_date': Return_date,
                             }
                # if AdapterPowerCodeBR.objects.filter(Number=Number):
                #     errMsgNumber = """编号已存在"""
                # else:
                # print(updatedic)
                try:
                    with transaction.atomic():
                        AdapterPowerCodeBR.objects.filter(id=id).update(**updatedic)
                        alert = 0
                except:
                    alert = '此数据%s正被其他使用者编辑中...' % id
                # print(Photo)
                if Photo:
                    for m in AdapterPowerCodeBR.objects.filter(id=id).first().Photo.all():  # 每次接受图片前清除原来的图片，而不是叠加
                        # print(m.id)
                        PICS.objects.filter(
                            id=m.id).delete()
                    for f in Photo:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                        # print(f)
                        empt = PICS()
                        # 增加其他字段应分别对应填写
                        empt.single = f
                        empt.pic = f
                        empt.save()
                        AdapterPowerCodeBR.objects.filter(id=id).first().Photo.add(empt)


                # mock_data
                # print(checkAdaPow)
                if checkAdaPow:
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "BR_per_code": i.BR_per_code,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                # print(mock_data)
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中

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
                    Changjiasearch = responseData['Changjia']
                    if Changjiasearch and Changjiasearch != "All":
                        checkAdaPow['Changjia'] = Changjiasearch
                    Customerserach = responseData['Customer']
                    if Customerserach and Customerserach != "All":
                        checkAdaPow['Customer'] = Customerserach
                    PNsearch = responseData['PN']
                    if PNsearch and PNsearch != "All":
                        checkAdaPow['MaterialPN'] = PNsearch
                    Powersearch = responseData['Power']
                    if Powersearch and Powersearch != "All":
                        checkAdaPow['Power'] = Powersearch
                    for i in responseData['params']:
                        # print(i)
                        AdapterPowerCodeBR.objects.get(id=i).delete()

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "BR_per_code": i.BR_per_code,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
                if 'ExcelData' in str(request.body):
                    responseData = json.loads(request.body)
                    # print(responseData['historyYear'],type(responseData['historyYear']))
                    checkAdaPow = {}
                    Changjia = responseData['Changjia']
                    if Changjia and Changjia != "All":
                        checkAdaPow['Changjia'] = Changjia
                    Customer = responseData['Customer']
                    if Customer and Customer != "All":
                        checkAdaPow['Customer'] = Customer
                    PN = responseData['PN']
                    if PN and PN != "All":
                        checkAdaPow['MaterialPN'] = PN
                    Power = responseData['Power']
                    if Power and Power != "All":
                        checkAdaPow['Power'] = Power
                    xlsxlist = json.loads(responseData['ExcelData'])
                    Adapterlist = [
                        {
                            'Number': '編號', }
                    ]
                    rownum = 0
                    startupload = 0
                    # print(xlsxlist)
                    uploadxlsxlist = []
                    for i in xlsxlist:
                        # print(type(i),i)
                        rownum += 1
                        modeldata = {}
                        for key, value in i.items():
                            if key in headermodel_Adapter.keys():
                                modeldata[headermodel_Adapter[key]] = value
                        if 'Changjia' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，廠家不能爲空
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
                        if 'Description' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Description不能爲空
                                                                            """ % rownum
                            break
                        if 'Power' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，功率不能爲空
                                                                            """ % rownum
                            break
                        if 'Number' in modeldata.keys():
                            startupload = 1
                            if 'MaterialPN' in modeldata.keys():
                                if modeldata['MaterialPN'][-4:] != modeldata['Number'][:4]:
                                    # print(modeldata['MaterialPN'][-4:], modeldata['Number'][:4])
                                    startupload = 0
                                    errMsg = err_msg = """
                                                        第"%s"條數據，編號:%s的前四位与MaterialPN:%s的后四位不一致
                                                                            """ % (rownum, modeldata['Number'], modeldata['MaterialPN'])
                                    break
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，編號不能爲空
                                                                            """ % rownum
                            break
                        if 'Location' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，Location不能爲空
                                                                            """ % rownum
                            break
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
                        if 'OAPcode' in modeldata.keys():
                            startupload = 1
                        else:
                            # canEdit = 0
                            startupload = 0
                            err_ok = 2
                            errMsg = err_msg = """
                                                        第"%s"條數據，掛賬人工號不能爲空
                                                                            """ % rownum
                            break
                            # 让数据可以从有值更新为无值
                        uploadxlsxlist.append(modeldata)
                    DevieModelfiedlist = []
                    for i in AdapterPowerCodeBR._meta.fields:
                        if i.name != 'id':
                            DevieModelfiedlist.append([i.name, i.get_internal_type()])
                    # print(1,DevieModelfiedlist)
                    for i in uploadxlsxlist:
                        for j in DevieModelfiedlist:
                            if j[0] not in i.keys():
                                # print(j)
                                if j[1] == "DateField":
                                    i[j[0]] = None
                                else:
                                    i[j[0]] = ''
                    if startupload:

                        scnum = 0
                        cznum = 0
                        xznum = 0
                        for i in uploadxlsxlist:
                            # print(i)
                            scnum += 1
                            # print(scnum)
                            modeldata = {}
                            for key, value in i.items():
                                if key == "Predict_return" or key == "Borrow_date" or key == "Return_date":
                                    # print(value)
                                    if value:
                                        modeldata[key] = value.split("/")[2] + "-" + \
                                                                                   value.split("/")[0] + "-" + \
                                                                                   value.split("/")[1]
                                    else:
                                        modeldata[key] = value
                                else:
                                    modeldata[key] = value
                            # print(3,modeldata)

                            Check_dic = {
                                'Number': modeldata['Number'],
                            }
                            # print(modeldata)
                            # Check_dic_Gantt['Test_Start'] = None  # 日期格式为空NULL不能用空字符
                            if AdapterPowerCodeBR.objects.filter(**Check_dic):#已经存在覆盖
                                cznum += 1
                                # AdapterPowerCodeBR.objects.filter(
                                #     **Check_dic).update(**modeldata)
                            else:#新增
                                xznum += 1
                                AdapterPowerCodeBR.objects.create(**modeldata)
                        errMsg = """共： %s 条, <br/>
                                    新增设备:    %s 条, <br/>
                                    编号重复:    %s 条（请确认一物有且仅有一料号原则）""" % (scnum, xznum, cznum)

                    #mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "BR_per_code": i.BR_per_code,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中



        data = {
            "content": mock_data,
            "select": selectItem,
            "selectPower": selectPower,
            # "selectOption": selectOption,
            "sectionCustomer": sectionCustomer,
            "sectionPhase": sectionPhase,
            "sectionStatus": sectionStatus,
            "sectionDeviceStatus": sectionDeviceStatus,
            "Lent": Lent,
            "kejieyong": kejieyong,
            "jieyongyuding": jieyongyuding,
            "guihuanqueren": guihuanqueren,
            "errMsg": errMsg,
            "errMsgNumber": errMsgNumber,
            "sectionOAP": sectionOAP,
            "sectionNumber": sectionNumber,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/M_edit.html', locals())

@csrf_exempt
def M_Keep(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/M_Keep"
    selectItem = [
        # {"value": "姚麗麗", "number": "12345678"}, {"value": "張亞萍", "number": "12345678"},
    ]
    for i in AdapterPowerCodeBR.objects.filter(BR_Status='續借確認').values('BR_per', 'BR_per_code').distinct().order_by('BR_per_code'):
        selectItem.append({"value": i['BR_per'],'number': i['BR_per_code']})
    mock_data = [
        # {"id": "1", "Changjia": "123", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "",
        #  "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "2", "Changjia": "456", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "89", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "3", "Changjia": "XCVBNM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "XCGVHJBJKN", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "",
        #  "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "4", "Changjia": "CFVGBHJNKM", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "5", "Changjia": "VGBHJNK", "MaterialPN": "", "Description": "", "Power": "", "Number": "",
        #  "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "6", "Changjia": "DFGHJ", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "7", "Changjia": "FGHJK", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""},
        # {"id": "8", "Changjia": "JM", "MaterialPN": "", "Description": "", "Power": "", "Number": "", "Location": "",
        #  "Customer": "", "Project_Code": "", "Phase": "", "OAP": "", "Device_Status": "", "BR_Status": "已借用",
        #  "BR_per": "", "Predict_return": "", "Borrow_date": "", "Return_date": "", "Exceed_days": ""}
    ]
    if request.method == "POST":
        if request.POST:
            if request.POST.get('isGetData') == 'first':
                # mock_data
                mock_datalist = AdapterPowerCodeBR.objects.filter(BR_Status='續借確認', OAPcode=request.session.get('account_DMS'),)
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
            if request.POST.get('isGetData') == 'SEARCH':
                checkAdaPow = {'BR_Status': '續借確認', 'OAPcode': request.session.get('account_DMS')}
                if request.POST.get('BorrowerNum'):
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
                    mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                else:
                    mock_datalist = AdapterPowerCodeBR.objects.all()
                for i in mock_datalist:
                    Photolist = []
                    for h in i.Photo.all():
                        Photolist.append(
                            {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                    if i.Predict_return and not i.Return_date:
                        if datetime.datetime.now().date() > i.Predict_return:
                            Exceed_days = round(
                                float(
                                    str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                        0]),
                                0)
                        else:
                            Exceed_days = ''
                    else:
                        Exceed_days = ''
                    Predict_return_str = ''
                    if i.Predict_return:
                        Predict_return_str = str(i.Predict_return)
                    else:
                        Predict_return_str = ''
                    Borrow_date_str = ''
                    if i.Borrow_date:
                        Borrow_date_str = str(i.Borrow_date)
                    else:
                        Borrow_date_str = ''
                    Return_date_str = ''
                    if i.Return_date:
                        Return_date_str = str(i.Return_date)
                    else:
                        Return_date_str = ''
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
                        {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                         "Description": i.Description,
                         "Power": i.Power,
                         "Number": i.Number, "Location": i.Location,
                         "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                         "Customer": i.Customer,
                         "Project_Code": i.Project_Code,
                         "Phase": i.Phase,
                         "OAP": i.OAP, "OAPcode": i.OAPcode,
                         "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                         "Predict_return": Predict_return_str,
                         "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                         "Last_BR_per": i.Last_BR_per,
                         "Last_Borrow_date": Last_Borrow_date_str,
                         "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                         "fileListO": Photolist},
                    )
                Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
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
                    checkAdaPow = {'BR_Status': '續借確認'}
                    # if responseData['BR_per']:
                    #     checkAdaPow['BR_per'] = responseData['BR_per']
                    if 'BR_per_code' in responseData.keys():
                        checkAdaPow['BR_per_code'] = responseData['BR_per_code']

                    updatedic = {'BR_Status': '已借出',
                                 # 'BR_per': request.session.get('CNname'),
                                 # 'Predict_return': None,
                                 'Borrow_date': datetime.datetime.now().date(),
                                 # 'Return_date': None,
                                 }
                    # print(updatedic)
                    for i in responseData['RenewId']:
                        # print(i)
                        updatedic['Last_BR_per'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per
                        updatedic['Last_BR_per_code'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per_code
                        updatedic['Last_Predict_return'] = AdapterPowerCodeBR.objects.filter(id=i).first().Predict_return
                        updatedic['OAP'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per
                        updatedic['OAPcode'] = AdapterPowerCodeBR.objects.filter(id=i).first().BR_per_code
                        # updatedic['Last_Borrow_date'] = datetime.datetime.now().date()
                        # updatedic['Last_Return_date'] = AdapterPowerCodeBR.objects.filter(id=i).first().Return_date
                        try:
                            with transaction.atomic():
                                # print(updatedic)
                                AdapterPowerCodeBR.objects.filter(id=i).update(**updatedic)
                                # print('1')
                                alert = 0
                        except Exception as e:
                            # print(e)
                            alert = '此数据%s正被其他使用者编辑中...' % i

                    # mock_data
                    if checkAdaPow:
                        mock_datalist = AdapterPowerCodeBR.objects.filter(**checkAdaPow)
                    else:
                        mock_datalist = AdapterPowerCodeBR.objects.all()
                    for i in mock_datalist:
                        Photolist = []
                        for h in i.Photo.all():
                            Photolist.append(
                                {'name': '', 'url': '/media/' + h.pic.name})  # fileListO需要的是对象列表而不是字符串列表
                        if i.Predict_return and not i.Return_date:
                            if datetime.datetime.now().date() > i.Predict_return:
                                Exceed_days = round(
                                    float(
                                        str((datetime.datetime.now().date() - i.Predict_return)).split(' ')[
                                            0]),
                                    0)
                            else:
                                Exceed_days = ''
                        else:
                            Exceed_days = ''
                        Predict_return_str = ''
                        if i.Predict_return:
                            Predict_return_str = str(i.Predict_return)
                        else:
                            Predict_return_str = ''
                        Borrow_date_str = ''
                        if i.Borrow_date:
                            Borrow_date_str = str(i.Borrow_date)
                        else:
                            Borrow_date_str = ''
                        Return_date_str = ''
                        if i.Return_date:
                            Return_date_str = str(i.Return_date)
                        else:
                            Return_date_str = ''
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
                            {"id": i.id, "Changjia": i.Changjia, "MaterialPN": i.MaterialPN,
                             "Description": i.Description,
                             "Power": i.Power,
                             "Number": i.Number, "Location": i.Location,
                             "Model": i.Model, "Pinming": i.Pinming, "Leibie": i.Leibie,
                             "Customer": i.Customer,
                             "Project_Code": i.Project_Code,
                             "Phase": i.Phase,
                             "OAP": i.OAP, "OAPcode": i.OAPcode,
                             "Device_Status": i.Device_Status, "BR_Status": i.BR_Status, "BR_per": i.BR_per,
                             "Predict_return": Predict_return_str,
                             "Borrow_date": Borrow_date_str, "Return_date": Return_date_str,
                             "Last_BR_per": i.Last_BR_per,
                             "Last_Borrow_date": Last_Borrow_date_str,
                             "Last_Return_date": Last_Return_date_str, "Exceed_days": Exceed_days,
                             "fileListO": Photolist},
                        )
                    Lent = mock_datalist.filter(BR_Status="已借出").count()  # 已借出
                    kejieyong = mock_datalist.filter(BR_Status="可借用").count()  # 可借用
                    jieyongyuding = mock_datalist.filter(BR_Status="預定確認").count()  # 預定確認中
                    guihuanqueren = mock_datalist.filter(BR_Status="歸還確認").count()  # 歸還確認中
        data = {
            "BR_perOptions": selectItem,
            "content": mock_data,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/M_Keep.html', locals())

@csrf_exempt
def Summary(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "AdapterPowerCode/Summary"
    mock_data = [
        # {"id": "1", "Leibie": "werfg", "Pinming": "a", "Total": "11", "TUM": "", "Chazhi": "-1"},
        # {"id": "2", "Leibie": "wregtf", "Pinming": "b", "Total": "12", "TUM": "", "Chazhi": "0"},
        # {"id": "3", "Leibie": "rqegw", "Pinming": "c", "Total": "1324", "TUM": "", "Chazhi": "-1"},
        # {"id": "4", "Leibie": "reftg", "Pinming": "d", "Total": "423", "TUM": "", "Chazhi": "NA"},
    ]
    tableContent1 = [
        # {"id": "6", "Pinming": "e", "Liaohao": "try", "Total": "23", "TUM": "3", "Chazhi": "0"},
        # {"id": "7", "Pinming": "f", "Liaohao": "tyg", "Total": "65", "TUM": "2", "Chazhi": "-1"},
        # {"id": "8", "Pinming": "g", "Liaohao": "werf", "Total": "34", "TUM": "42", "Chazhi": "0"},
        # {"id": "9", "Pinming": "h", "Liaohao": "nhgt", "Total": "8", "TUM": "2", "Chazhi": "-1"},
        # {"id": "10", "Pinming": "j", "Liaohao": "hgf", "Total": "876", "TUM": "1", "Chazhi": "-1"},
    ]
    heBingNum2 = [
        # 3, 2
    ]

    if request.method == "POST":
        LNVTUNINfo = {}
        LNVTUNINfo = LNVTUMINFOTotal()
        # print(LNVTUNINfo)
        if AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="一類"):
            adapterTotal = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="一類").count()
        else:
            adapterTotal = 0
        if AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="一類"):
            PowerCodeTotal = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="一類").count()
        else:
            PowerCodeTotal = 0

        if AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="二類"):
            freeadapterTotal = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="二類").count()
        else:
            freeadapterTotal = 0
        if AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="二類"):
            freePowerCodeTotal = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="二類").count()
        else:
            freePowerCodeTotal = 0

        if LNVTUNINfo:
            if LNVTUNINfo["Adapter"]:
                guaAdapterTum = int(LNVTUNINfo["Adapter"]["Total"])
                guaAdapterChazhi = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="一類").count()-guaAdapterTum
            else:
                guaAdapterTum = "Can't access TUM"
                guaAdapterChazhi = "Can't access TUM"
            if LNVTUNINfo["PowerCode"]:
                guaPowerCodeTum = int(LNVTUNINfo["PowerCode"]["Total"])
                guaPowerCodeChazhi = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="一類").count() - guaPowerCodeTum
            else:
                guaPowerCodeTum = "Can't access TUM"
                guaPowerCodeChazhi = "Can't access TUM"
        else:
            guaAdapterTum = "Can't access TUM"
            guaAdapterChazhi = "Can't access TUM"
            guaPowerCodeTum = "Can't access TUM"
            guaPowerCodeChazhi = "Can't access TUM"
        mock_data.append({"id": "", "Leibie": "挂賬", "Pinming": "Adapter",
                          "Total": adapterTotal,
                          "TUM": guaAdapterTum,
                          "Chazhi": guaAdapterChazhi})
        mock_data.append({"id": "", "Leibie": "挂賬", "Pinming": "PowerCode",
                          "Total": PowerCodeTotal,
                          "TUM": guaPowerCodeTum,
                          "Chazhi": guaPowerCodeChazhi})
        mock_data.append({"id": "", "Leibie": "Free", "Pinming": "Adapter",
                          "Total": freeadapterTotal,
                          "TUM": "NA",
                          "Chazhi": "NA"})
        mock_data.append({"id": "", "Leibie": "Free", "Pinming": "PowerCode",
                          "Total": freePowerCodeTotal,
                          "TUM": "NA",
                          "Chazhi": "NA"})
        TUMAdapterPNlist = []
        DMSadapterPNList = []
        TUMPowerCodePNList = []
        DMSPowerCodePNList = []
        for i in AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="一類").values('MaterialPN').distinct().order_by('MaterialPN'):
            DMSadapterPNList.append(i["MaterialPN"])
        if LNVTUNINfo:
            for i in LNVTUNINfo["Adapter"]['Detail']:
                TUMAdapterPNlist.append(i['PN'])
        adapterPNlist = list(set(TUMAdapterPNlist).union(set(DMSadapterPNList)))
        for i in AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="一類").values('MaterialPN').distinct().order_by('MaterialPN'):
            DMSPowerCodePNList.append(i["MaterialPN"])
        if LNVTUNINfo:
            for i in LNVTUNINfo["PowerCode"]['Detail']:
                TUMPowerCodePNList.append(i['PN'])
        PowerCodePNlist = list(set(TUMPowerCodePNList).union(set(DMSPowerCodePNList)))
        adapternum = 0
        PowerCodenum = 0
        for i in adapterPNlist:
            adapternum += 1
            DMSadapterPNnum = "NA"
            TUMadapterPNnum = "NA"
            adapterChazhi = "NA"
            if AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="一類", MaterialPN=i):
                DMSadapterPNnum = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="Adapter", Leibie="一類", MaterialPN=i).count()
            if LNVTUNINfo:
                TUMadapterPNnum = 0
                for j in LNVTUNINfo["Adapter"]['Detail']:
                    if j['PN'] == i:
                        TUMadapterPNnum += j['Qty']
            else:
                TUMadapterPNnum = "Can't access TUM"
            if DMSadapterPNnum != "NA" and TUMadapterPNnum != "NA" and TUMadapterPNnum != "Can't access TUM":
                adapterChazhi = int(DMSadapterPNnum) - int(TUMadapterPNnum)
            tableContent1.append({"id": "", "Pinming": "Adapter", "Liaohao": i, "Total": DMSadapterPNnum, "TUM": TUMadapterPNnum, "Chazhi": adapterChazhi})
        for i in PowerCodePNlist:
            PowerCodenum += 1
            DMSPowerCodePNnum = "NA"
            TUMPowerCodePNnum = "NA"
            PowerCodeChazhi = "NA"
            if AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="一類", MaterialPN=i):
                DMSPowerCodePNnum = AdapterPowerCodeBR.objects.exclude(BR_Status="Close").filter(Pinming="PowerCode", Leibie="一類", MaterialPN=i).count()
            if LNVTUNINfo:
                TUMPowerCodePNnum = 0
                for j in LNVTUNINfo["PowerCode"]['Detail']:
                    if j['PN'] == i:
                        TUMPowerCodePNnum += j['Qty']
            else:
                TUMPowerCodePNnum = "Can't access TUM"
            if DMSPowerCodePNnum != "NA" and TUMPowerCodePNnum != "NA" and TUMPowerCodePNnum != "Can't access TUM":
                PowerCodeChazhi = int(DMSPowerCodePNnum) - int(TUMPowerCodePNnum)
            tableContent1.append({"id": "", "Pinming": "PowerCode", "Liaohao": i, "Total": DMSPowerCodePNnum, "TUM": TUMPowerCodePNnum, "Chazhi": PowerCodeChazhi})
        heBingNum2 = [adapternum, PowerCodenum]
        data = {
            "content": mock_data,
            "tableContent1": tableContent1,
            "heBingNum2": heBingNum2
        }
        print(data, type(data))
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'AdapterPowerCode/Summary.html', locals())