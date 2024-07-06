from django.shortcuts import render,redirect,HttpResponse
from .models import UserInfo,Role,Permission,Menu,Imgs
from django.views.decorators.csrf import csrf_exempt
import datetime,os
from service.init_permission import init_permission
from django.conf import settings
# Create your views here.
from django.forms import forms
from DjangoUeditor.forms import UEditorField
from django.conf import settings
import datetime,json,requests,time,simplejson
from requests_ntlm import HttpNtlmAuth
from DeviceLNV.models import DeviceLNV
from DeviceABO.models import DeviceABO
from DeviceA39.models import DeviceA39
from ComputerMS.models import ComputerLNV
from ChairCabinetMS.models import ChairCabinetLNV
from app01 import tasks

# from app01.templatetags.custom_tag import *

# class TestUEditorForm(forms.Form):
#     content = UEditorField('Solution/Action', width=800, height=500,
#                             toolbars="full", imagePath="upimg/", filePath="upfile/",
#                             upload_settings={"imageMaxSize": 1204000},
#                             settings={}, command=None#, blank=True
#                             )
# import logging
#
# logger = logging.getLogger('Django')
# logger.debug('Debug')
# logger.info('Info')
# logger.warning('Warning')
# logger.error('Error')
# logger.critical('Critical')
import pprint
def ImportPersonalInfo(Customer='', SAPNum='', GroupNum='', Status='', DepartmentCode=''):
    url = r'http://127.0.0.1:8002/PersonalInfo/api_Per/login/'
    url2 = r'http://127.0.0.1:8002/PersonalInfo/Perapi/?'
    requests.adapters.DEFAULT_RETRIES = 1
    # s = requests.session()
    # s.keep_alive = False  # 关闭多余连接
    # getTestSpec=requests.get(url)
    # headers = {'Connection': 'close'}
    try:
        headers = \
            {
                "Content-Type": "application/json;charset=UTF-8"
            }
        body = \
            {
                "username": "API_CQM", "password": "Qs!3m6Tc7"
            }
        r = requests.post(url, headers=headers, data=json.dumps(body))
    except:
        # time.sleep(0.1)
        print("Can't connect to DDIS Sercer or get token failed")
        return 0
    # print(json.loads(r.text)["token"])
    if json.loads(r.text)["token"]:
        Auth_token = "Bearer " + json.loads(r.text)["token"]
        try:
            # GroupNum = "C1010S3"
            headers = \
                {
                    "Authorization": Auth_token
                }
            content = \
                {
                    "Customer": Customer,
                    "SAPNum": SAPNum,
                    "GroupNum": GroupNum,
                    "Status": Status,
                    "DepartmentCode": DepartmentCode,
                }
            getTestSpec = requests.get(url2, headers=headers, params=content)
        except:
            # time.sleep(0.1)
            print("Got nothing, try request agian")
            return 0
        # print(getTestSpec.json())
        # pprint.pprint(getTestSpec.json())
        # print(type(getTestSpec.json()), len(getTestSpec.json()))
    # print(type(getTestSpec.json()), getTestSpec.json())
    #     for i in getTestSpec.json():
    #         print(i)
        return getTestSpec.json()

@csrf_exempt
def login(request):
    # 不允许重复登录
    # print(request.COOKIES)
    # print(request.session.get('is_login_DMS', None),"is_login_DMS")
    if request.session.get('is_login_DMS', None):
        # return redirect('/index/')
        # print(request.COOKIES)
        try:
            return redirect(request.COOKIES['current_page_DMS'])
        except:
            return redirect('/index/')
    # print(request.method)
    # print('test')

    if request.method == "POST":
        # login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        # if login_form.is_valid():
        Account = request.POST.get('inputEmail')
        Password = request.POST.get('inputPassword')
        user_obj = UserInfo.objects.filter(account=Account, password=Password).first()
        # print (Account)
        # print (Password)
        # print (user_obj)
        # print(request.user)
        # print(request.user.type)
        # t= UserInfo.objects.get(account=Account)
        user = UserInfo.objects.filter(account=Account).first()
        # print(type(user),type(user_obj))
        if user:

            # print (user.password)
            if user.password == Password:
                # 往session字典内写入用户状态和数据,你完全可以往里面写任何数据，不仅仅限于用户相关！
                request.session['is_login_DMS'] = True
                request.session['user_id_DSM'] = user.id
                request.session['user_name_DMS'] = user.username
                request.session['CNname_DMS'] = user.CNname
                request.session['account_DMS'] = Account
                # request.session['Skin'] = "/static/src/blue.jpg"
                request.session.set_expiry(12*60*60)
                # print('11')
                Skin = request.COOKIES.get('Skin_raw')
                # print(Skin)
                if not Skin:
                    Skin = "/static/src/blue.jpg"
                init_permission(request, user_obj)  # 调用init_permission，初始化权限
                # print('21')
                # print(settings.MEDIA_ROOT,settings.MEDIA_URL)
                # return HttpResponseRedirect(request.session['login_from'])
                Non_login_path = request.session.get('Non_login_path')
                print(Non_login_path, 'Non_login_path')
                if Non_login_path:
                    # 记住来源的url，如果没有则设置为首页('/')
                    return redirect(Non_login_path)
                # print(request.POST.get('next', '/'),'postnext')
                # if request.GET.get('next'):
                #     # 记住来源的url，如果没有则设置为首页('/')
                #     print(request.GET.get('next'), request.META.get('HTTP_REFERER'), 'tttt')
                #     return redirect(request.GET.get('next'))
                else:
                    # return redirect('/index/')
                    return redirect(request.META.get('HTTP_REFERER'))
            else:
                message = "密码不正确！"
        else:
            message = "用户不存在！"
        return render(request, 'login.html', locals())


    return render(request, 'login.html', locals())

@csrf_exempt
def signinLNV(request):
    # print("signin")
    message = ""
    inputRoles = Role.objects.filter(name__contains="Users").filter(name__contains="LNV").order_by("name")
    # print(inputRoles)
    if request.method == "POST":
        # message = "请检查填写的内容！"
        account = request.POST.get('inputAccount')
        password = request.POST.get('inputPassword1')
        CNname = request.POST.get('inputCNname')
        username = request.POST.get('inputUsrname')
        Seat = request.POST.get('inputSeat')
        email = request.POST.get('inputEmail')
        role = request.POST.get('inputRole')
        roles = request.POST.getlist('inputRole')
        # print(role, roles)
        if UserInfo.objects.filter(account=account).first():
            message = "工號已注冊！"
        else:
            for i in roles:
                if Role.objects.filter(name=i).first():
                    message = "注冊成功！"
                else:
                    message = "角色内容不對，請聯係管理員！"
                    return render(request, 'SigninLNV.html', locals())
            createdic = {"account": account, "password": password, "CNname": CNname,
                         "username": username, "Seat": Seat, "email": email,
                         "department": 1, "is_active": True, "is_staff": False, "is_SVPuser": False,
                         }
            # Role.objects.filter(name=role).first(),
            print(createdic)
            UserInfo.objects.create(**createdic)
            for i in roles:
                UserInfo.objects.filter(account=account).first().role.add(Role.objects.filter(name=i).first(), )
            return render(request, 'login.html', locals())
    return render(request, 'SigninLNV.html', locals())

@csrf_exempt
def signinABO(request):
    # print("signin")
    message = ""
    inputRoles = Role.objects.filter(name__contains="Users").filter(name__contains="ABO").order_by("name")
    # print(inputRoles)
    if request.method == "POST":
        # message = "请检查填写的内容！"
        account = request.POST.get('inputAccount')
        password = request.POST.get('inputPassword1')
        CNname = request.POST.get('inputCNname')
        username = request.POST.get('inputUsrname')
        Seat = request.POST.get('inputSeat')
        email = request.POST.get('inputEmail')
        role = request.POST.get('inputRole')
        roles = request.POST.getlist('inputRole')
        # print(role, roles)
        if UserInfo.objects.filter(account=account).first():
            message = "工號已注冊！"
        else:
            for i in roles:
                if Role.objects.filter(name=i).first():
                    message = "注冊成功！"
                else:
                    message = "角色内容不對，請聯係管理員！"
                    return render(request, 'SigninABO.html', locals())
            createdic = {"account": account, "password": password, "CNname": CNname,
                         "username": username, "Seat": Seat, "email": email,
                         "department": 1, "is_active": True, "is_staff": False, "is_SVPuser": False,
                         }
            # Role.objects.filter(name=role).first(),
            print(createdic)
            UserInfo.objects.create(**createdic)
            for i in roles:
                UserInfo.objects.filter(account=account).first().role.add(Role.objects.filter(name=i).first(), )
            return render(request, 'login.html', locals())
    return render(request, 'SigninABO.html', locals())

@csrf_exempt
def signinA31(request):
    # print("signin")
    message = ""
    inputRoles = Role.objects.filter(name__contains="Users").filter(name__contains="A31").order_by("name")
    # print(inputRoles)
    if request.method == "POST":
        # message = "请检查填写的内容！"
        account = request.POST.get('inputAccount')
        password = request.POST.get('inputPassword1')
        CNname = request.POST.get('inputCNname')
        username = request.POST.get('inputUsrname')
        Seat = request.POST.get('inputSeat')
        email = request.POST.get('inputEmail')
        role = request.POST.get('inputRole')
        roles = request.POST.getlist('inputRole')
        # print(role, roles)
        if UserInfo.objects.filter(account=account).first():
            message = "工號已注冊！"
        else:
            for i in roles:
                if Role.objects.filter(name=i).first():
                    message = "注冊成功！"
                else:
                    message = "角色内容不對，請聯係管理員！"
                    return render(request, 'SigninA31.html', locals())
            createdic = {"account": account, "password": password, "CNname": CNname,
                         "username": username, "Seat": Seat, "email": email,
                         "department": 1, "is_active": True, "is_staff": False, "is_SVPuser": False,
                         }
            # Role.objects.filter(name=role).first(),
            print(createdic)
            UserInfo.objects.create(**createdic)
            for i in roles:
                UserInfo.objects.filter(account=account).first().role.add(Role.objects.filter(name=i).first(), )
            return render(request, 'login.html', locals())
    return render(request, 'SigninA31.html', locals())

@csrf_exempt
def signinCQT88(request):
    # print("signin")
    message = ""
    inputRoles = Role.objects.filter(name__contains="Users").filter(name__contains="CQT88").order_by("name")
    print(inputRoles)
    if request.method == "POST":
        # message = "请检查填写的内容！"
        account = request.POST.get('inputAccount')
        password = request.POST.get('inputPassword1')
        CNname = request.POST.get('inputCNname')
        username = request.POST.get('inputUsrname')
        Seat = request.POST.get('inputSeat')
        email = request.POST.get('inputEmail')
        role = request.POST.get('inputRole')
        roles = request.POST.getlist('inputRole')
        # print(role, roles)
        if UserInfo.objects.filter(account=account).first():
            message = "工號已注冊！"
        else:
            for i in roles:
                if Role.objects.filter(name=i).first():
                    message = "注冊成功！"
                else:
                    message = "角色内容不對，請聯係管理員！"
                    return render(request, 'signinCQT88.html', locals())
            createdic = {"account": account, "password": password, "CNname": CNname,
                         "username": username, "Seat": Seat, "email": email,
                         "department": 1, "is_active": True, "is_staff": False, "is_SVPuser": False,
                         }
            # Role.objects.filter(name=role).first(),
            print(createdic)
            UserInfo.objects.create(**createdic)
            for i in roles:
                UserInfo.objects.filter(account=account).first().role.add(Role.objects.filter(name=i).first(), )
            return render(request, 'login.html', locals())
    return render(request, 'signinCQT88.html', locals())

@csrf_exempt
def index(request):
    if not request.session.get('is_login_DMS', None):
        return redirect('/login/')
    Syswangzhinamedic = {
        "AdapterPowerCord_LNV": "/AdapterPowerCode/BorrowedAdapter/",
        "Device_C38LNV": "/DeviceLNV/BorrowedDeviceLNV/",
        "Device_A39OBI": "/DeviceA39/BorrowedDeviceA39/",
        "Device_ABO": "/DeviceABO/BorrowedDeviceABO/",
        "Device_CQT88": "/DeviceCQT88/BorrowedDeviceCQT88/",
        "ComputerMS_LNV": "/ComputerMS/BorrowedComputer/",
        "ChairCabinetMS_LNV": "/ChairCabinetMS/BorrowedChairCabinet/",
                         }
    tableData = [
        # {"systName": "AdapterAndPowercode-LNV", "wangzhi": "https://www.baidu.com/", "region": "KS-Plant5", "adminCN": "王君",
        #  "pic": "", "EnglishName": "Jun_Wang", "groupNumber": "C111B1J", "phoneNumber": "21831"},
        # {"systName": "Device-LNV", "wangzhi": "https://www.tmall.com/", "region": "KS-Plant5", "adminCN": "曹泽", "pic": "",
        #  "EnglishName": "Edwin_Cao", "groupNumber": "C1010S3", "phoneNumber": "21831"},
        # {"systName": "Device-ABO", "wangzhi": "https://www.taobao.com/", "region": "CQ", "adminCN": "孙俊清", "pic": "",
        #  "EnglishName": "Erin_Sun", "groupNumber": "20652552", "phoneNumber": "21831"},
    ]

    Gcontent = [
        '1. 請使用Chrome瀏覽器',
        '2. 若不能正常登陆设备管理系统，请及时联系Auto-Team（21831）',
        '3. 系统登陆默认密码是12345678，请大家登录后，尽快修改密码', '4. 系统后续更新维护事项，将以E-mail和系统公告的形式通知大家',
                ]
    for i in Role.objects.all():
        if len(i.name.split("_")) > 2:
            if i.name.split("_")[2] == "Admin":
                # print(i)
                # per_admin = UserInfo.objects.filter(role=i.id).first()
                # per_admin = UserInfo.objects.filter(role=i.id).latest()
                per_admin = UserInfo.objects.filter(role=i.id).last()
                # print(per_admin)
                if per_admin:
                    peradmininfo = {
                        "systName": i.name.split("_")[0] + "_" + i.name.split("_")[1], "wangzhi": "", "region": per_admin.Seat,
                        "adminCN": per_admin.CNname,
                        # "pic": per_admin.Photo.all().first().img.name,
                        "EnglishName": per_admin.username, "groupNumber": per_admin.account,
                        "phoneNumber": per_admin.Tel
                    }
                    if per_admin.Photo.all().first():
                        # print(per_admin.Photo.all().first().img)
                        peradmininfo['pic'] = '/media/' + per_admin.Photo.all().first().img.name
                    tableData.append(peradmininfo)
    if tableData:
        for j in tableData:
            if j['systName'] in Syswangzhinamedic.keys():
                j['wangzhi'] = Syswangzhinamedic[j['systName']]

    # print(request.method, request.POST)
    if request.method == "POST":
        data = {
            "tableData": tableData,
            "Gcontent": Gcontent,
        }
        # print(data)
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'index.html', locals())

@csrf_exempt
def logout(request):
    # print('t')
    # print (request.session.get('is_login_DMS', None))
    if not request.session.get('is_login_DMS', None):
        # 如果本来就未登录，也就没有登出一说
        # print('logout')
        return redirect("/login/")
    #flush()方法是比较安全的一种做法，而且一次性将session中的所有内容全部清空，确保不留后患。但也有不好的地方，那就是如果你在session中夹带了一点‘私货’，会被一并删除，这一点一定要注意
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login_DMS']
    # del request.session['user_id_DSM']
    # del request.session['user_name_DMS']
    return redirect("/login/")

@csrf_exempt
def Change_Password(request):
    if not request.session.get('is_login_DMS', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    # print (request.method)
    if request.method == "POST":
        OldPassword=request.POST.get('OldPassword')
        Password = request.POST.get('Password')
        Passwordc = request.POST.get('Confirm')
        user=request.session.get('user_name_DMS')
        userpass=UserInfo.objects.get(username=user).password
        # print(OldPassword,userpass)
        if OldPassword==userpass:
            if Password==Passwordc:
                # print(request.session.get('user_name_DMS', None))
                updatep = UserInfo.objects.filter(username=request.session.get('user_name_DMS', None))
                # print (updatep)
                # for e in updatep:
                #    print (e.password)
                updatep.update(password=Password)
                request.session.flush()
                return redirect("/login/")
            else:
                message="Password is not same"
                return render(request, 'changepassword.html', locals())
        else:
            message = "Incorrect Password"
            return render(request, 'changepassword.html', locals())
    return render(request, 'changepassword.html', locals())

@csrf_exempt
def UserInfoedit(request):
    if not request.session.get('is_login_DMS', None):
        return redirect('/login/')
    # tableData=[{"systName":"AdapterAndPowercode-LNV","wangzhi":"https://www.baidu.com/","region":"昆山","adminCN":"王君","pic":"","EnglishName":"Jun_Wang","groupNumber":"C111B1J","phoneNumber":"21831"},
    #            {"systName": "Device-LNV","wangzhi":"https://www.tmall.com/", "region": "昆山", "adminCN": "曹泽","pic":"","EnglishName":"Edwin_Cao","groupNumber":"C1010s3","phoneNumber":"21831"},
    #            {"systName": "Device-ABO","wangzhi":"https://www.taobao.com/", "region": "重慶", "adminCN": "孙俊清","pic":"","EnglishName":"Erin_Sun","groupNumber":"20652552","phoneNumber":"21831"},]
    #
    # Gcontent = ['1.若不能正常登陆设备管理系统，请及时联系Jun_Wang（21831）', '2.由于IIS server权限限定,设备管理员不可随意在别人的工作机导出Excel文档',
    #             '3.系统登陆默认密码是123456，请大家登录后，尽快修改密码，密码需为六位纯数字', '4.系统后续更新维护事项，将以E-mail和系统公告的形式通知大家'
    #           , '5.系统后续更新维护事项，将以E-mail和系统公告的形式通知大家', '6.系统后续更新维护事项，将以E-mail和系统公告的形式通知大家', '7.系统后续更新维护事项，将以E-mail和系统公告的形式通知大家'
    #             ]
    weizhi = "用户信息维护"
    select = [
              #   [{"value": "王君"}, {"value": "曹泽"}, {"value": "孙俊清"}, ],
              # [{"value": "C111B1J"}, {"value": "C1010s3"}, {"value": "20652552"}, {"value": "20564439"},
              #  {"value": "20518869"}, {"value": "30157828"}, ]
              ]
    content = [
        # {"id": "1", "account": "C111B1J", "CNname": "王君", "username": "", "password": "", "Email": "rtgff",
        #         "Tel": "73325"},
        #        {"id": "2", "account": "C1010s3", "CNname": "曹泽", "username": "Edwin_Cao", "password": "sdf",
        #         "Email": "fewgrbff", "Tel": "783"},
        #        {"id": "3", "account": "20652552", "CNname": "孙俊清", "username": "Erin_Sun", "password": "sadgfvbgvd",
        #         "Email": "abfvv", "Tel": "785452"},
        #        {"id": "4", "account": "20564439", "CNname": "孙俊清", "username": "Erin_Sun", "password": "asdsxdf",
        #         "Email": "ebfvf", "Tel": "683"},
        #        {"id": "5", "account": "20518869", "CNname": "孙俊清", "username": "Erin_Sun", "password": "asdsfbd",
        #         "Email": "egrtrb", "Tel": "8636"},
        #        {"id": "6", "account": "30157828", "CNname": "孙俊清", "username": "Erin_Sun", "password": "wdsfv",
        #         "Email": "rbtrgbrg", "Tel": "68785758"},
        #        {"id": "7", "account": "10256489", "CNname": "孙俊清", "username": "Erin_Sun", "password": "wdsfdv",
        #         "Email": "rbg", "Tel": "6585"},
    ]
    selectCNname = []
    for i in UserInfo.objects.all().values("CNname").order_by("CNname"):
        selectCNname.append({"value": i["CNname"]})
    select.append(selectCNname)
    selectAccount = []
    for i in UserInfo.objects.all().values("account").order_by("account"):
        selectAccount.append({"value": i["account"]})
    select.append(selectAccount)
    if request.method == "POST":
        if request.POST.get("isGetData") == "first":
            Pers_list = ImportPersonalInfo()
            if Pers_list:
                pass
            for i in UserInfo.objects.all():
                content.append({
                    "id": i.id, "account": i.account, "CNname": i.CNname, "username": i.username, "password": i.password, "Email": i.email,
                            "Tel": i.Tel,
                },)
        if request.POST.get("isGetData") == "SEARCH":
            checkUser_dic = {}
            if request.POST.get("account"):
                checkUser_dic['account'] = request.POST.get("account")
            if request.POST.get("CNname"):
                checkUser_dic['CNname'] = request.POST.get("CNname")
            for i in UserInfo.objects.filter(**checkUser_dic):
                content.append({
                    "id": i.id, "account": i.account, "CNname": i.CNname, "username": i.username, "password": i.password, "Email": i.email,
                            "Tel": i.Tel,
                },)
        if request.POST.get("isGetData") == "update":
            Photolist = request.FILES.getlist("fileList", "")
            id = request.POST.get("id")
            account = request.POST.get("account")
            CNname = request.POST.get("CNname")
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("Email")
            Tel = request.POST.get("Tel")
            updatedic = {
                "account": account, "CNname": CNname, "username": username, "password": password, "email": email, "Tel": Tel,
            }
            UserInfo.objects.filter(id=id).update(**updatedic)
            if Photolist:
                for m in UserInfo.objects.filter(
                        id=id).first().Photo.all():  # 每次接受图片前清除原来的图片，而不是叠加
                    # print(m.id)
                    Imgs.objects.filter(
                        id=m.id).delete()  # 无需先将子表里面相关联的数据都删除（或者断开关联），才能删除母表的图片（并且物理路径下的文件也被删除了），应该是model里面加了mymodel_delete的原因
                for f in Photolist:  # 数据上允许传多张照片，实际生产环境中头像只会传一张
                    # print(f)
                    empt = Imgs()
                    # 增加其他字段应分别对应填写
                    empt.single = f
                    empt.img = f
                    empt.save()
                    UserInfo.objects.filter(id=id).first().Photo.add(empt)
            checkUser_dic = {}
            if request.POST.get("searchaccount"):
                checkUser_dic['account'] = request.POST.get("searchaccount")
            if request.POST.get("searchCNname"):
                checkUser_dic['CNname'] = request.POST.get("searchCNname")
            for i in UserInfo.objects.filter(**checkUser_dic):
                content.append({
                    "id": i.id, "account": i.account, "CNname": i.CNname, "username": i.username, "password": i.password, "Email": i.email,
                            "Tel": i.Tel,
                },)
        data = {
            "select": select,
            "content": content,
            # "tableData":tableData,
            # "Gcontent": Gcontent,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'UserInfoedit.html', locals())

@csrf_exempt
def Change_Skin(request):
    if not request.session.get('is_login_DMS', None):
        return redirect('/login/')
    # print(request.method)
    Skin = request.COOKIES.get('Skin_raw')
    # print(Skin)
    if not Skin:
        Skin = "/static/src/blue.jpg"
    # print(Skin)
    weizhi = "Change Skin"
    Render = render(request, 'ChangeSkin.html', locals())
    Redirect=redirect('/Change_Skin/')
    if request.method == "POST":

        if 'blue' in request.POST:
            Skinv = request.POST.get('Skin')
            Redirect.set_cookie('Skin_raw', "/static/src/blue.jpg", 3600 * 24 * 30 * 12)
        if 'kiwi' in request.POST:
            Skinv = request.POST.get('Skin')
            Redirect.set_cookie('Skin_raw', "/static/src/kiwi.jpg", 3600 * 24 * 30 * 12)
        if 'sunny' in request.POST:
            Skinv = request.POST.get('Skin')
            Redirect.set_cookie('Skin_raw', "/static/src/sunny.jpg",3600*24*30*12)
        if 'yellow' in request.POST:
            Skinv = request.POST.get('Skin')
            Redirect.set_cookie('Skin_raw', "/static/src/yellow.jpg",3600*24*30*12)
        if 'chrome' in request.POST:
            Skinv = request.POST.get('Skin')
            Redirect.set_cookie('Skin_raw', "/static/src/chrome.jpg",3600*24*30*12)
        if 'ocean' in request.POST:
            Skinv = request.POST.get('Skin')
            Redirect.set_cookie('Skin_raw', "/static/src/ocean.jpg",3600*24*30*12)
        return Redirect
            # return redirect('/index/')
    # return redirect('/index/')
    # print(Skin)
    return Render

@csrf_exempt
def Summary(request):
    if not request.session.get('is_login_DMS', None):
        return redirect('/login/')
    # print(request.method)
    selectItem = [
        # {"value": "1234567", "number": "姚麗麗"}, {"value": "2234567", "number": "張亞萍"},
    ]
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        selectItem.append({"value": i["account"], "number": i["CNname"]})

    mock_data1 = [
        # {"id": "1", "Customer": "C38",
        #  "NID": "1514", "DevID": "All Function", "IntfCtgry": "USB_A",
        #  "DevCtgry": "keyboard", "Devproperties": "USB1.0", "Devsize": "--",
        #  "DevVendor": "Lenovo", "DevModel": "SK-8815(L)", "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #  "BrwStatus": ""
        #  },
    ]

    mock_data2 = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "MaterialPN": "ELZP3010009", "MachineStatus": "使用中", },
    ]

    mock_data3 = [
        # {"id": "1", "GYNumber": "DQA-C-002", "Position": "V2FA-29",
        #  "UseStatus": "閑置中", "CollectDate": "2019-2-11"},
    ]

    mock_data4 = [
        # {"id": "1", "GYNumber": "DQA-Y-002", "Position": "V2FA-29",
        #  "UseStatus": "閑置中", "CollectDate": "2019-2-11"},
    ]

    if request.method == "POST":
        # tasks.GetTumdata()
        if request.POST.get('isGetData') == "first":
            pass
        if request.POST.get('isGetData') == "SEARCH":
            BorrowerNum = request.POST.get('BorrowerNum')
            Borrower = request.POST.get('Borrower')

            check_dic1 = {'Usrname': Borrower,
                                'BR_per_code': BorrowerNum, 'BrwStatus__in': ['已借出', '固定設備', '預定確認中', '歸還確認中', '續借確認中']}
            # print(check_dic1)
            mock_datalist1 = DeviceLNV.objects.filter(**check_dic1)
            for i in mock_datalist1:
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

                mock_data1.append(
                    {"id": i.id, "Customer": i.Customer,
                     # "Plant": i.Plant,
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

            check_dic2_1 = {'Usrname': Borrower,
                          'BR_per_code': BorrowerNum,
                          'BrwStatus__in': ['使用中', '閑置中', '申請確認中', '轉帳確認中', '接收確認中']
                            }
            mock_datalist2_1 = ComputerLNV.objects.filter(**check_dic2_1)
            for i in mock_datalist2_1:
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

                mock_data2.append(
                    {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                     "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                     "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                     "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                     "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                     "MachineStatus": i.BrwStatus,
                     "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                )
            check_dic2_2 = {
                            'Receive_per_code': BorrowerNum,
                            'BrwStatus__in': ['轉帳確認中', '接收確認中']}
            mock_datalist2_2 = ComputerLNV.objects.filter(**check_dic2_2)
            for i in mock_datalist2_2:
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

                mock_data2.append(
                    {"id": i.id, "CollectDate": Btime_str, "UnifiedNumber": i.NID,
                     "Number": i.BR_per_code, "Name": i.Usrname, "MaterialPN": i.MaterialPN,
                     "CPU": i.CPU, "RAM": i.RAM, "HDD": i.HDD, "Wireless": i.Wireless, "LCD": i.LCD, "OCR": i.OCR,
                     "Battery": i.Battery, "Adaptor": i.Adaptor, "Region": i.Area, "Factory": i.Plant,
                     "OutPlant": i.Carryif, "ComputerUse": i.Purpose, "Category": i.Category,
                     "MachineStatus": i.BrwStatus,
                     "IdleState": i.IdleStatus, "Years": Years, "FormNumber": i.EFormNo}
                )

            check_dic3_1 = {'OAP': Borrower,
                          'OAPcode': BorrowerNum,
                          'BrwStatus__in': ['使用中', '閑置中', '維修中', '申請確認中', '轉帳確認中', '申請核准中', '接收確認中'],
                          "Category": "櫃子"}
            # print(check_dic1)
            mock_datalist3_1 = ChairCabinetLNV.objects.filter(**check_dic3_1)
            for i in mock_datalist3_1:

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

                mock_data3.append(
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
            check_dic3_2 = {
                            'Receive_per_code': BorrowerNum,
                            'BrwStatus__in': ['轉帳確認中', '接收確認中'],
                            "Category": "櫃子"}
            # print(check_dic1)
            mock_datalist3_2 = ChairCabinetLNV.objects.filter(**check_dic3_2)
            for i in mock_datalist3_2:

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

                mock_data3.append(
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

            check_dic4_1 = {'OAP': Borrower,
                            'OAPcode': BorrowerNum,
                            'BrwStatus__in': ['使用中', '閑置中', '維修中', '申請確認中', '轉帳確認中', '申請核准中', '接收確認中'],
                            "Category": "椅子"}
            # print(check_dic1)
            mock_datalist4_1 = ChairCabinetLNV.objects.filter(**check_dic4_1)
            for i in mock_datalist4_1:

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

                mock_data4.append(
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
            check_dic4_2 = {
                'Receive_per_code': BorrowerNum,
                'BrwStatus__in': ['轉帳確認中', '接收確認中'],
                "Category": "椅子"}
            # print(check_dic1)
            mock_datalist4_2 = ChairCabinetLNV.objects.filter(**check_dic4_2)
            for i in mock_datalist4_2:

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

                mock_data4.append(
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
            "select": selectItem,
            "content1": mock_data1,
            "content2": mock_data2,
            "content3": mock_data3,
            "content4": mock_data4,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'Summary.html', locals())

@csrf_exempt
def Summary_ABO(request):
    if not request.session.get('is_login_DMS', None):
        return redirect('/login/')
    # print(request.method)
    selectItem = [
        # {"value": "1234567", "number": "姚麗麗"}, {"value": "2234567", "number": "張亞萍"},
    ]
    for i in UserInfo.objects.all().values("CNname", "account").distinct().order_by("account"):
        selectItem.append({"value": i["account"], "number": i["CNname"]})

    mock_data1 = [
        # {"id": "1", "Customer": "C38",
        #  "NID": "1514", "DevID": "All Function", "IntfCtgry": "USB_A",
        #  "DevCtgry": "keyboard", "Devproperties": "USB1.0", "Devsize": "--",
        #  "DevVendor": "Lenovo", "DevModel": "SK-8815(L)", "DevName": "Lenovo Enhanced Performance USB Keyboard",
        #  "BrwStatus": ""
        #  },
    ]

    mock_data2 = [
        # {"id": "1", "CollectDate": "2019-2-11", "UnifiedNumber": "GI027569",
        #  "MaterialPN": "ELZP3010009", "MachineStatus": "使用中", },
    ]

    mock_data3 = [
        # {"id": "1", "GYNumber": "DQA-C-002", "Position": "V2FA-29",
        #  "UseStatus": "閑置中", "CollectDate": "2019-2-11"},
    ]

    mock_data4 = [
        # {"id": "1", "GYNumber": "DQA-Y-002", "Position": "V2FA-29",
        #  "UseStatus": "閑置中", "CollectDate": "2019-2-11"},
    ]

    if request.method == "POST":
        if request.POST.get('isGetData') == "first":
            pass
        if request.POST.get('isGetData') == "SEARCH":
            BorrowerNum = request.POST.get('BorrowerNum')
            Borrower = request.POST.get('Borrower')

            check_dic1 = {'Usrname': Borrower,
                                'BR_per_code': BorrowerNum, 'BrwStatus__in': ['已借出', '固定設備', '預定確認中', '歸還確認中', '續借確認中']}
            # print(check_dic1)
            mock_datalist1 = DeviceABO.objects.filter(**check_dic1)
            for i in mock_datalist1:
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

                mock_data1.append(
                    {"id": i.id, "Customer": i.Customer,
                     # "Plant": i.Plant,
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
            "content1": mock_data1,
            "content2": mock_data2,
            "content3": mock_data3,
            "content4": mock_data4,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'Summary_ABO.html', locals())


from django.http import JsonResponse
from app01 import tasks
@csrf_exempt
def ctest(request,*args,**kwargs):
    res=tasks.print_test.delay()
    #任务逻辑
    return JsonResponse({'status':'successful','task_id':res.task_id})