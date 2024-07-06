from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime,os, json
from django.db.models import Max,Min,Sum,Count,Q
from django.http import JsonResponse
from .models import WirelessAP
from service.init_permission import init_permission
from DMS import settings
from django.core.mail import send_mail, send_mass_mail
from django.core.mail import EmailMultiAlternatives
from app01 import tasks
from app01.models import UserInfo
# Create your views here.
@csrf_exempt
def Borrowed(request):
    if not request.session.get('is_login', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "WirelessAP/Borrowed"


    if request.method == "POST":
        pass
        data = {

        }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'WirelessAP/Borrowed.html', locals())