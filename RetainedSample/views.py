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
from .models import RetainedSample, PersonalRetainedSample, RetainedSampleRecord


@csrf_exempt
def RetainedSample_summary(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "留樣系統/管理"
    CustomerOptions = []

    # print(roles)
    errMsg = ''
    cabinets_datas = [
        # {"id": 1, "name": "柜体1", "rows": 5, "cols": 6, "gridData": [
        #                                                                 [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""}],
        #                                                                 [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 ]
        #  },
        # {"id": 2, "name": "柜体2", "rows": 5, "cols": 6, "gridData": [
        #     [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        # ]
        #  },
    ]
    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            pass


        else:
            try:
                request.body

            except:
                pass
            else:
                if 'addCabinet' in str(request.body):
                    pass


        data = {
            "cabinets": cabinets_datas,
            # "isAdmin": isAdmin,
            # "currentUser": currentUser,
            "CustomerOptions": CustomerOptions,
            "errMsg": errMsg,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'RetainedSample/RetainedSample.html', locals())

@csrf_exempt
def RetainedSample_MyBorrow(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "留樣系統/管理"
    CustomerOptions = []

    # print(roles)
    errMsg = ''
    cabinets_datas = [
        # {"id": 1, "name": "柜体1", "rows": 5, "cols": 6, "gridData": [
        #                                                                 [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""}],
        #                                                                 [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 ]
        #  },
        # {"id": 2, "name": "柜体2", "rows": 5, "cols": 6, "gridData": [
        #     [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        # ]
        #  },
    ]
    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            pass


        else:
            try:
                request.body

            except:
                pass
            else:
                if 'addCabinet' in str(request.body):
                    pass


        data = {
            "cabinets": cabinets_datas,
            # "isAdmin": isAdmin,
            # "currentUser": currentUser,
            "CustomerOptions": CustomerOptions,
            "errMsg": errMsg,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'RetainedSample/RetainedSample.html', locals())

@csrf_exempt
def RetainedSample_MyApproval(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "留樣系統/管理"
    CustomerOptions = []

    # print(roles)
    errMsg = ''
    cabinets_datas = [
        # {"id": 1, "name": "柜体1", "rows": 5, "cols": 6, "gridData": [
        #                                                                 [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""}],
        #                                                                 [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 ]
        #  },
        # {"id": 2, "name": "柜体2", "rows": 5, "cols": 6, "gridData": [
        #     [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        # ]
        #  },
    ]
    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            pass


        else:
            try:
                request.body

            except:
                pass
            else:
                if 'addCabinet' in str(request.body):
                    pass


        data = {
            "cabinets": cabinets_datas,
            # "isAdmin": isAdmin,
            # "currentUser": currentUser,
            "CustomerOptions": CustomerOptions,
            "errMsg": errMsg,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'RetainedSample/RetainedSample.html', locals())

@csrf_exempt
def RetainedSample_BRRecord(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "留樣系統/管理"
    CustomerOptions = []

    # print(roles)
    errMsg = ''
    cabinets_datas = [
        # {"id": 1, "name": "柜体1", "rows": 5, "cols": 6, "gridData": [
        #                                                                 [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""}],
        #                                                                 [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 ]
        #  },
        # {"id": 2, "name": "柜体2", "rows": 5, "cols": 6, "gridData": [
        #     [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        # ]
        #  },
    ]
    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            pass


        else:
            try:
                request.body

            except:
                pass
            else:
                if 'addCabinet' in str(request.body):
                    pass


        data = {
            "cabinets": cabinets_datas,
            # "isAdmin": isAdmin,
            # "currentUser": currentUser,
            "CustomerOptions": CustomerOptions,
            "errMsg": errMsg,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'RetainedSample/RetainedSample.html', locals())

@csrf_exempt
def RetainedSample_ScrapRecord(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "留樣系統/管理"
    CustomerOptions = []

    # print(roles)
    errMsg = ''
    cabinets_datas = [
        # {"id": 1, "name": "柜体1", "rows": 5, "cols": 6, "gridData": [
        #                                                                 [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""},
        #                                                                  {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "", "notes": ""}],
        #                                                                 [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""},
        #                                                                  {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #                                                                   "notes": ""}],
        #                                                                 ]
        #  },
        # {"id": 2, "name": "柜体2", "rows": 5, "cols": 6, "gridData": [
        #     [{"position": "A1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "A6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "B1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "B6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "C1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "C6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "D1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "D6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        #     [{"position": "E1", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E2", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E3", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E4", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E5", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""},
        #      {"position": "E6", "user": "", "status": "0", "statusText": "空闲", "borrowDate": "", "reserveDate": "",
        #       "notes": ""}],
        # ]
        #  },
    ]
    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            pass


        else:
            try:
                request.body

            except:
                pass
            else:
                if 'addCabinet' in str(request.body):
                    pass


        data = {
            "cabinets": cabinets_datas,
            # "isAdmin": isAdmin,
            # "currentUser": currentUser,
            "CustomerOptions": CustomerOptions,
            "errMsg": errMsg,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'RetainedSample/RetainedSample.html', locals())

