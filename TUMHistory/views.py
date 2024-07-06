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
from app01 import tasks
from .models import *
from django.db.models.functions import Trunc
# Create your views here.
@csrf_exempt
def SummaryTUM(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "TUMHistory/Unit"
    C38Table = [
        # {"Item": "領用", "Customer": "預算", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "預算", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領退差異（領用-退還）", "Customer": "差異", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
    ]
    T88Table = [
        # {"Item": "領用", "Customer": "預算", "Jan": "188", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "預算", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領退差異（領用-退還）", "Customer": "差異", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
    ]
    sectionCustomer = [
        "C38(NB)", "C38(AIO)", "C85", "T88(AIO)"
                       ]
    sectionCategory = [
        "領用", "退還"
    ]
    errMsgNumber = ""
    canEdit = 0
    canEdit_TUM = 0
    roles = []
    onlineuser = request.session.get('account_DMS')
    # print(UserInfo.objects.get(account=onlineuser))
    for i in UserInfo.objects.get(account=onlineuser).role.all():
        roles.append(i.name)
    for i in roles:
        if i == 'Sys_Admin':
            # editPpriority = 4
            canEdit = 1
        elif i == "AdapterPowerCord_LNV_Admin":
            canEdit_TUM = 1
    if request.method == "POST":
        if request.POST:
            try:
                if request.POST.get('isGetData') == 'first':
                    Year_now = str(datetime.datetime.now().year)
                    YearNow = str(datetime.datetime.now().year)
                    if (int(YearNow) % 4) == 0:
                        if (int(YearNow) % 100) == 0:
                            if (int(YearNow) % 400) == 0:
                                # print("{0} 是闰年".format(YearNow))  # 整百年能被400整除的是闰年
                                mounthlist = [("Jan", "-1-31"), ("Feb", "-2-29"), ("Mar", "-3-31"), ("Apr", "-4-30"),
                                              ("May", "-5-31"), ("Jun", "-6-30"),
                                              ("Jul", "-7-31"), ("Aug", "-8-31"), ("Sep", "-9-30"), ("Oct", "-10-31"),
                                              ("Nov", "-11-30"), ("Dec", "-12-31"), ]
                            else:
                                # print("{0} 不是闰年".format(YearNow))
                                mounthlist = [("Jan", "-1-31"), ("Feb", "-2-28"), ("Mar", "-3-31"), ("Apr", "-4-30"),
                                              ("May", "-5-31"), ("Jun", "-6-30"),
                                              ("Jul", "-7-31"), ("Aug", "-8-31"), ("Sep", "-9-30"), ("Oct", "-10-31"),
                                              ("Nov", "-11-30"), ("Dec", "-12-31"), ]
                        else:
                            # print("{0} 是闰年".format(YearNow))  # 非整百年能被4整除的为闰年
                            mounthlist = [("Jan", "-1-31"), ("Feb", "-2-29"), ("Mar", "-3-31"), ("Apr", "-4-30"),
                                          ("May", "-5-31"), ("Jun", "-6-30"),
                                          ("Jul", "-7-31"), ("Aug", "-8-31"), ("Sep", "-9-30"), ("Oct", "-10-31"),
                                          ("Nov", "-11-30"), ("Dec", "-12-31"), ]
                    else:
                        # print("{0} 不是闰年".format(YearNow))
                        mounthlist = [("Jan", "-1-31"), ("Feb", "-2-28"), ("Mar", "-3-31"), ("Apr", "-4-30"),
                                      ("May", "-5-31"),
                                      ("Jun", "-6-30"),
                                      ("Jul", "-7-31"), ("Aug", "-8-31"), ("Sep", "-9-30"), ("Oct", "-10-31"),
                                      ("Nov", "-11-30"), ("Dec", "-12-31"), ]
                    mounthnow = datetime.datetime.now().month
                    # C38Table 领用
                    sectionCustomer_C38 = [
                        "C38(NB)", "C38(AIO)", "C85"
                    ]
                    Jan_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Jan'))['Jan__sum']
                    Feb_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Feb'))['Feb__sum']
                    Mar_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Mar'))['Mar__sum']
                    Apr_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Apr'))['Apr__sum']
                    May_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('May'))['May__sum']
                    Jun_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Jun'))['Jun__sum']
                    Jul_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Jul'))['Jul__sum']
                    Aug_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Aug'))['Aug__sum']
                    Sep_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Sep'))['Sep__sum']
                    Oct_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Oct'))['Oct__sum']
                    Nov_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Nov'))['Nov__sum']
                    Dec_Unitbudget_Num = Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="領用").aggregate(Sum('Dec'))['Dec__sum']
                    C38_yusuan_dic = {"Item": "領用", "Customer": "預算", "Jan": Jan_Unitbudget_Num, "Feb": Feb_Unitbudget_Num, "Mar": Mar_Unitbudget_Num,
                                     "Apr": Apr_Unitbudget_Num, "May": May_Unitbudget_Num, "Jun": Jun_Unitbudget_Num, "Jul": Jul_Unitbudget_Num,
                                     "Aug": Aug_Unitbudget_Num, "Sep": Sep_Unitbudget_Num, "Oct": Oct_Unitbudget_Num, "Nov": Nov_Unitbudget_Num, "Dec": Dec_Unitbudget_Num,
                     }
                    C38_shiji_dic = {"Item": "領用", "Customer": "實際"}
                    C38_chayi_dic = {"Item": "領用", "Customer": "差異（實際-預算）"}
                    C38_yusuan_dic_summary_mounth = 0
                    C38_yusuan_dic_summary = 0
                    C38_shiji_dic_summary_mounth = 0
                    mounthnum = 1
                    for i in mounthlist:
                        if i[0] in C38_yusuan_dic.keys() and C38_yusuan_dic[i[0]] != "" and C38_yusuan_dic[i[0]] != None:
                            C38_yusuan_dic_summary += C38_yusuan_dic[i[0]]
                            if mounthnum > mounthnow:
                                pass
                            else:
                                DateNow_begin = datetime.datetime.strptime(YearNow + "-" + i[1].split("-")[1] + "-1",
                                                                           '%Y-%m-%d')
                                # print(DateNow_begin)
                                DateNow = datetime.datetime.strptime(YearNow + i[1], '%Y-%m-%d')
                                Test_Endperiod = [DateNow_begin, DateNow]
                                shiji_inDQA = UnitInDQA_Tum.objects.filter(CustomerCode__in=sectionCustomer_C38,
                                                   InData__range=Test_Endperiod).aggregate(Sum("QTY"))['QTY__sum'] if UnitInDQA_Tum.objects.filter(CustomerCode__in=sectionCustomer_C38,
                                                   InData__range=Test_Endperiod) else 0
                                shiji_return = DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_C38,
                                                   InData__range=Test_Endperiod).aggregate(Sum("QTY"))['QTY__sum'] if DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_C38,
                                                   InData__range=Test_Endperiod) else 0
                                C38_shiji_dic[i[0]] = shiji_inDQA + shiji_return
                                C38_chayi_dic[i[0]] = C38_shiji_dic[i[0]] - C38_yusuan_dic[i[0]]
                                C38_shiji_dic_summary_mounth += C38_shiji_dic[i[0]]
                                C38_yusuan_dic_summary_mounth += C38_yusuan_dic[i[0]]
                        mounthnum += 1
                    # print(C38_shiji_dic)
                    C38_yusuan_dic['Summary_Month'] = C38_yusuan_dic_summary_mounth
                    C38_yusuan_dic['Summary'] = C38_yusuan_dic_summary
                    C38_shiji_dic['Summary_Month'] = C38_shiji_dic_summary_mounth
                    C38_shiji_dic['Summary'] = C38_shiji_dic_summary_mounth
                    C38_chayi_dic['Summary_Month'] = C38_shiji_dic_summary_mounth - C38_yusuan_dic_summary_mounth
                    C38_chayi_dic['Summary'] = C38_shiji_dic_summary_mounth - C38_yusuan_dic_summary
                    C38Table.append(C38_yusuan_dic)
                    C38Table.append(C38_shiji_dic)
                    C38Table.append(C38_chayi_dic)
                    # C38Table 退還
                    tuihuan_Jan_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Jan'))['Jan__sum']
                    tuihuan_Feb_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Feb'))['Feb__sum']
                    tuihuan_Mar_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Mar'))['Mar__sum']
                    tuihuan_Apr_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Apr'))['Apr__sum']
                    tuihuan_May_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('May'))['May__sum']
                    tuihuan_Jun_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Jun'))['Jun__sum']
                    tuihuan_Jul_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Jul'))['Jul__sum']
                    tuihuan_Aug_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Aug'))['Aug__sum']
                    tuihuan_Sep_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Sep'))['Sep__sum']
                    tuihuan_Oct_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Oct'))['Oct__sum']
                    tuihuan_Nov_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Nov'))['Nov__sum']
                    tuihuan_Dec_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_C38, Year=Year_now, Category="退還").aggregate(
                        Sum('Dec'))['Dec__sum']
                    tuihuan_C38_yusuan_dic = {"Item": "退還", "Customer": "預算", "Jan": tuihuan_Jan_Unitbudget_Num, "Feb": tuihuan_Feb_Unitbudget_Num,
                                      "Mar": tuihuan_Mar_Unitbudget_Num,
                                      "Apr": tuihuan_Apr_Unitbudget_Num, "May": tuihuan_May_Unitbudget_Num, "Jun": tuihuan_Jun_Unitbudget_Num,
                                      "Jul": tuihuan_Jul_Unitbudget_Num,
                                      "Aug": tuihuan_Aug_Unitbudget_Num, "Sep": tuihuan_Sep_Unitbudget_Num, "Oct": tuihuan_Oct_Unitbudget_Num,
                                      "Nov": tuihuan_Nov_Unitbudget_Num, "Dec": tuihuan_Dec_Unitbudget_Num,
                                      }
                    tuihuan_C38_shiji_dic = {"Item": "退還", "Customer": "實際"}
                    tuihuan_C38_chayi_dic = {"Item": "退還", "Customer": "差異（實際-預算）"}
                    lingtui_C38_chayi_dic = {"Item": "領退差異（領用-退還）", "Customer": "差異"}
                    tuihuan_C38_yusuan_dic_summary_mounth = 0
                    tuihuan_C38_yusuan_dic_summary = 0
                    tuihuan_C38_shiji_dic_summary_mounth = 0
                    mounthnum = 1
                    for i in mounthlist:
                        if i[0] in tuihuan_C38_yusuan_dic.keys() and tuihuan_C38_yusuan_dic[i[0]] != "" and tuihuan_C38_yusuan_dic[i[0]] != None:
                            tuihuan_C38_yusuan_dic_summary += tuihuan_C38_yusuan_dic[i[0]]
                            if mounthnum > mounthnow:
                                pass
                            else:
                                DateNow_begin = datetime.datetime.strptime(YearNow + "-" + i[1].split("-")[1] + "-1",
                                                                           '%Y-%m-%d')
                                # print(DateNow_begin)
                                DateNow = datetime.datetime.strptime(YearNow + i[1], '%Y-%m-%d')
                                Test_Endperiod = [DateNow_begin, DateNow]
                                tuihuan_C38_shiji_dic[i[0]] = DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_C38,
                                                            ReturnData__range=Test_Endperiod).aggregate(
                                    Sum("QTY"))['QTY__sum'] if DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_C38,
                                                                  ReturnData__range=Test_Endperiod) else 0
                                # print(i[0], tuihuan_C38_shiji_dic[i[0]])
                                tuihuan_C38_chayi_dic[i[0]] = tuihuan_C38_shiji_dic[i[0]] - tuihuan_C38_yusuan_dic[i[0]]
                                lingtui_C38_chayi_dic[i[0]] = C38_chayi_dic[i[0]] - tuihuan_C38_chayi_dic[i[0]]
                                tuihuan_C38_shiji_dic_summary_mounth += tuihuan_C38_shiji_dic[i[0]]
                                tuihuan_C38_yusuan_dic_summary_mounth += tuihuan_C38_yusuan_dic[i[0]]
                        mounthnum += 1
                    # print(C38_shiji_dic)
                    tuihuan_C38_yusuan_dic['Summary_Month'] = tuihuan_C38_yusuan_dic_summary_mounth
                    tuihuan_C38_yusuan_dic['Summary'] = tuihuan_C38_yusuan_dic_summary
                    tuihuan_C38_shiji_dic['Summary_Month'] = tuihuan_C38_shiji_dic_summary_mounth
                    tuihuan_C38_shiji_dic['Summary'] = tuihuan_C38_shiji_dic_summary_mounth
                    tuihuan_C38_chayi_dic['Summary_Month'] = tuihuan_C38_shiji_dic_summary_mounth - tuihuan_C38_yusuan_dic_summary_mounth
                    tuihuan_C38_chayi_dic['Summary'] = tuihuan_C38_shiji_dic_summary_mounth - tuihuan_C38_yusuan_dic_summary
                    lingtui_C38_chayi_dic[
                        'Summary_Month'] = C38_chayi_dic['Summary_Month'] - tuihuan_C38_chayi_dic['Summary_Month']
                    lingtui_C38_chayi_dic['Summary'] = C38_chayi_dic['Summary'] - tuihuan_C38_chayi_dic['Summary']
                    C38Table.append(tuihuan_C38_yusuan_dic)
                    C38Table.append(tuihuan_C38_shiji_dic)
                    C38Table.append(tuihuan_C38_chayi_dic)
                    C38Table.append(lingtui_C38_chayi_dic)

                    #T88Table 领用
                    sectionCustomer_T88 = [
                        "T88(AIO)"
                    ]
                    Year_now = str(datetime.datetime.now().year)
                    Jan_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Jan'))['Jan__sum']
                    Feb_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Feb'))['Feb__sum']
                    Mar_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Mar'))['Mar__sum']
                    Apr_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Apr'))['Apr__sum']
                    May_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('May'))['May__sum']
                    Jun_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Jun'))['Jun__sum']
                    Jul_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Jul'))['Jul__sum']
                    Aug_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Aug'))['Aug__sum']
                    Sep_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Sep'))['Sep__sum']
                    Oct_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Oct'))['Oct__sum']
                    Nov_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Nov'))['Nov__sum']
                    Dec_Unitbudget_Num = \
                    Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="領用").aggregate(
                        Sum('Dec'))['Dec__sum']
                    T88_yusuan_dic = {"Item": "領用", "Customer": "預算", "Jan": Jan_Unitbudget_Num, "Feb": Feb_Unitbudget_Num,
                                      "Mar": Mar_Unitbudget_Num,
                                      "Apr": Apr_Unitbudget_Num, "May": May_Unitbudget_Num, "Jun": Jun_Unitbudget_Num,
                                      "Jul": Jul_Unitbudget_Num,
                                      "Aug": Aug_Unitbudget_Num, "Sep": Sep_Unitbudget_Num, "Oct": Oct_Unitbudget_Num,
                                      "Nov": Nov_Unitbudget_Num, "Dec": Dec_Unitbudget_Num,
                                      }

                    T88_shiji_dic = {"Item": "領用", "Customer": "實際"}
                    T88_chayi_dic = {"Item": "領用", "Customer": "差異（實際-預算）"}
                    YearNow = str(datetime.datetime.now().year)

                    T88_yusuan_dic_summary_mounth = 0
                    T88_yusuan_dic_summary = 0
                    T88_shiji_dic_summary_mounth = 0
                    mounthnum = 1
                    for i in mounthlist:
                        if i[0] in T88_yusuan_dic.keys() and T88_yusuan_dic[i[0]] != "" and T88_yusuan_dic[i[0]] != None:
                            print(T88_yusuan_dic[i[0]])
                            T88_yusuan_dic_summary += T88_yusuan_dic[i[0]]
                            if mounthnum > mounthnow:
                                pass
                            else:
                                DateNow_begin = datetime.datetime.strptime(YearNow + "-" + i[1].split("-")[1] + "-1",
                                                                           '%Y-%m-%d')
                                # print(DateNow_begin)
                                DateNow = datetime.datetime.strptime(YearNow + i[1], '%Y-%m-%d')
                                Test_Endperiod = [DateNow_begin, DateNow]
                                shiji_inDQA = UnitInDQA_Tum.objects.filter(CustomerCode__in=sectionCustomer_T88,
                                                                                   InData__range=Test_Endperiod).aggregate(
                                    Sum("QTY"))['QTY__sum'] if UnitInDQA_Tum.objects.filter(CustomerCode__in=sectionCustomer_T88,
                                                                                   InData__range=Test_Endperiod) else 0
                                shiji_return = DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_T88,
                                                                                   InData__range=Test_Endperiod).aggregate(
                                    Sum("QTY"))['QTY__sum'] if DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_T88,
                                                                                   InData__range=Test_Endperiod) else 0
                                T88_shiji_dic[i[0]] = shiji_inDQA + shiji_return
                                T88_chayi_dic[i[0]] = T88_shiji_dic[i[0]] - T88_yusuan_dic[i[0]]
                                T88_shiji_dic_summary_mounth += T88_shiji_dic[i[0]]
                                T88_yusuan_dic_summary_mounth += T88_yusuan_dic[i[0]]
                        mounthnum += 1
                    # print(T88_shiji_dic)
                    T88_yusuan_dic['Summary_Month'] = T88_yusuan_dic_summary_mounth
                    T88_yusuan_dic['Summary'] = T88_yusuan_dic_summary
                    T88_shiji_dic['Summary_Month'] = T88_shiji_dic_summary_mounth
                    T88_shiji_dic['Summary'] = T88_shiji_dic_summary_mounth
                    T88_chayi_dic['Summary_Month'] = T88_shiji_dic_summary_mounth - T88_yusuan_dic_summary_mounth
                    T88_chayi_dic['Summary'] = T88_shiji_dic_summary_mounth - T88_yusuan_dic_summary
                    T88Table.append(T88_yusuan_dic)
                    T88Table.append(T88_shiji_dic)
                    T88Table.append(T88_chayi_dic)
                    # T88Table 退还
                    tuihuan_Jan_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Jan'))['Jan__sum']
                    tuihuan_Feb_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Feb'))['Feb__sum']
                    tuihuan_Mar_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Mar'))['Mar__sum']
                    tuihuan_Apr_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Apr'))['Apr__sum']
                    tuihuan_May_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('May'))['May__sum']
                    tuihuan_Jun_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Jun'))['Jun__sum']
                    tuihuan_Jul_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Jul'))['Jul__sum']
                    tuihuan_Aug_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Aug'))['Aug__sum']
                    tuihuan_Sep_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Sep'))['Sep__sum']
                    tuihuan_Oct_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Oct'))['Oct__sum']
                    tuihuan_Nov_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Nov'))['Nov__sum']
                    tuihuan_Dec_Unitbudget_Num = \
                        Unitbudget.objects.filter(Customer__in=sectionCustomer_T88, Year=Year_now, Category="退還").aggregate(
                            Sum('Dec'))['Dec__sum']
                    tuihuan_T88_yusuan_dic = {"Item": "退還", "Customer": "預算", "Jan": tuihuan_Jan_Unitbudget_Num,
                                              "Feb": tuihuan_Feb_Unitbudget_Num,
                                              "Mar": tuihuan_Mar_Unitbudget_Num,
                                              "Apr": tuihuan_Apr_Unitbudget_Num, "May": tuihuan_May_Unitbudget_Num,
                                              "Jun": tuihuan_Jun_Unitbudget_Num,
                                              "Jul": tuihuan_Jul_Unitbudget_Num,
                                              "Aug": tuihuan_Aug_Unitbudget_Num, "Sep": tuihuan_Sep_Unitbudget_Num,
                                              "Oct": tuihuan_Oct_Unitbudget_Num,
                                              "Nov": tuihuan_Nov_Unitbudget_Num, "Dec": tuihuan_Dec_Unitbudget_Num,
                                              }
                    tuihuan_T88_shiji_dic = {"Item": "退還", "Customer": "實際"}
                    tuihuan_T88_chayi_dic = {"Item": "退還", "Customer": "差異（實際-預算）"}
                    lingtui_T88_chayi_dic = {"Item": "領退差異（領用-退還）", "Customer": "差異"}
                    tuihuan_T88_yusuan_dic_summary_mounth = 0
                    tuihuan_T88_yusuan_dic_summary = 0
                    tuihuan_T88_shiji_dic_summary_mounth = 0
                    mounthnum = 1
                    for i in mounthlist:
                        if i[0] in tuihuan_T88_yusuan_dic.keys() and tuihuan_T88_yusuan_dic[i[0]] != "" and tuihuan_T88_yusuan_dic[i[0]] != None:
                            tuihuan_T88_yusuan_dic_summary += tuihuan_T88_yusuan_dic[i[0]]
                            if mounthnum > mounthnow:
                                pass
                            else:
                                DateNow_begin = datetime.datetime.strptime(YearNow + "-" + i[1].split("-")[1] + "-1",
                                                                           '%Y-%m-%d')
                                # print(DateNow_begin)
                                DateNow = datetime.datetime.strptime(YearNow + i[1], '%Y-%m-%d')
                                Test_Endperiod = [DateNow_begin, DateNow]
                                tuihuan_T88_shiji_dic[i[0]] = \
                                DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_T88,
                                                                  ReturnData__range=Test_Endperiod).aggregate(
                                    Sum("QTY"))['QTY__sum'] if DQAUnit_TUMHistory.objects.filter(CustomerCode__in=sectionCustomer_T88,
                                                                  ReturnData__range=Test_Endperiod) else 0
                                tuihuan_T88_chayi_dic[i[0]] = tuihuan_T88_shiji_dic[i[0]] - tuihuan_T88_yusuan_dic[i[0]]
                                lingtui_T88_chayi_dic[i[0]] = T88_chayi_dic[i[0]] - tuihuan_T88_chayi_dic[i[0]]
                                tuihuan_T88_shiji_dic_summary_mounth += tuihuan_T88_shiji_dic[i[0]]
                                tuihuan_T88_yusuan_dic_summary_mounth += tuihuan_T88_yusuan_dic[i[0]]
                        mounthnum += 1
                    # print(T88_shiji_dic)
                    tuihuan_T88_yusuan_dic['Summary_Month'] = tuihuan_T88_yusuan_dic_summary_mounth
                    tuihuan_T88_yusuan_dic['Summary'] = tuihuan_T88_yusuan_dic_summary
                    tuihuan_T88_shiji_dic['Summary_Month'] = tuihuan_T88_shiji_dic_summary_mounth
                    tuihuan_T88_shiji_dic['Summary'] = tuihuan_T88_shiji_dic_summary_mounth
                    tuihuan_T88_chayi_dic[
                        'Summary_Month'] = tuihuan_T88_shiji_dic_summary_mounth - tuihuan_T88_yusuan_dic_summary_mounth
                    tuihuan_T88_chayi_dic['Summary'] = tuihuan_T88_shiji_dic_summary_mounth - tuihuan_T88_yusuan_dic_summary
                    lingtui_T88_chayi_dic[
                        'Summary_Month'] = T88_chayi_dic['Summary_Month'] - tuihuan_T88_chayi_dic['Summary_Month']
                    lingtui_T88_chayi_dic['Summary'] = T88_chayi_dic['Summary'] - tuihuan_T88_chayi_dic['Summary']
                    T88Table.append(tuihuan_T88_yusuan_dic)
                    T88Table.append(tuihuan_T88_shiji_dic)
                    T88Table.append(tuihuan_T88_chayi_dic)
                    T88Table.append(lingtui_T88_chayi_dic)
            except Exception as e:
                print('first',str(e))
            try:
                if request.POST.get('action') == 'addSubmit':
                    Input_dic = {}
                    Check_dic = {}
                    if request.POST.get('Customer'):
                        Input_dic['Customer'] = request.POST.get('Customer')
                        Check_dic['Customer'] = request.POST.get('Customer')
                    if request.POST.get('Year'):
                        Input_dic['Year'] = request.POST.get('Year')
                        Check_dic['Year'] = request.POST.get('Year')
                    if request.POST.get('Category'):
                        Input_dic['Category'] = request.POST.get('Category')
                        Check_dic['Category'] = request.POST.get('Category')
                    if request.POST.get('Jan'):
                        Input_dic['Jan'] = request.POST.get('Jan')
                    if request.POST.get('Feb'):
                        Input_dic['Feb'] = request.POST.get('Feb')
                    if request.POST.get('Mar'):
                        Input_dic['Mar'] = request.POST.get('Mar')
                    if request.POST.get('Apr'):
                        Input_dic['Apr'] = request.POST.get('Apr')
                    if request.POST.get('May'):
                        Input_dic['May'] = request.POST.get('May')
                    if request.POST.get('Jun'):
                        Input_dic['Jun'] = request.POST.get('Jun')
                    if request.POST.get('Jul'):
                        Input_dic['Jul'] = request.POST.get('Jul')
                    if request.POST.get('Aug'):
                        Input_dic['Aug'] = request.POST.get('Aug')
                    if request.POST.get('Sep'):
                        Input_dic['Sep'] = request.POST.get('Sep')
                    if request.POST.get('Oct'):
                        Input_dic['Oct'] = request.POST.get('Oct')
                    if request.POST.get('Nov'):
                        Input_dic['Nov'] = request.POST.get('Nov')
                    if request.POST.get('Dec'):
                        Input_dic['Dec'] = request.POST.get('Dec')
                    if Unitbudget.objects.filter(**Check_dic):
                        errMsgNumber = '该客户别：%s，该年份：%s的%s，数据已经存在。' % (Check_dic['Customer'], Check_dic['Year'], Check_dic['Category'])
                    else:
                        Unitbudget.objects.create(**Input_dic)
            except Exception as e:
                print('addSubmit',str(e))
            try:
                if request.POST.get('isGetData') == 'synchronous':
                    tasks.GetTumdata()
            except Exception as e:
                print('isGetData',str(e))

            data = {
                "C38Table": C38Table,
                "T88Table": T88Table,
                "sectionCustomer": sectionCustomer,
                "sectionCategory": sectionCategory,
                "errMsgNumber": errMsgNumber,
                "canEdit": canEdit,
                "canEdit_TUM": canEdit_TUM,
            }
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'TUMHistory/TUMHistory.html', locals())

@csrf_exempt
def SummaryMateria(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "TUMHistory/Materia"
    C38Table = [
        # {"Item": "領用", "Customer": "預算", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "預算", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領退差異（領用-退還）", "Customer": "差異", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
    ]
    T88Table = [
        # {"Item": "領用", "Customer": "預算", "Jan": "188", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領用", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "預算", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "實際", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "退還", "Customer": "差異（實際-預算）", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
        # {"Item": "領退差異（領用-退還）", "Customer": "差異", "Jan": "168", "Feb": "178", "Mar": "233", "Apr": "233", "May": "233",
        #  "Jun": "233", "Jul": "233", "Aug": "233", "Sep": "233", "Oct": "233", "Nov": "233", "Dec": "233",
        #  "Summary_Month": "233", "Summary": "233"},
    ]
    sectionCustomer = [
        "C38(NB)", "C38(AIO)", "C85", "T88(AIO)"
                       ]
    sectionCategory = [
        "領用", "退還"
    ]
    errMsgNumber = ""
    canEdit = 1
    canEdit = 0
    roles = []
    onlineuser = request.session.get('account_DMS')
    # print(UserInfo.objects.get(account=onlineuser))
    for i in UserInfo.objects.get(account=onlineuser).role.all():
        roles.append(i.name)
    for i in roles:
        if i == 'Sys_Admin':
            # editPpriority = 4
            canEdit = 1
    queryset_data_OTST = MateriaInDQA_Tum.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))#__icontains不接受 array 就像查询集中的那样address__icontains= ["word1", "word2", "word3"]
    queryset_data_RT = DQAMateria_TUMHistory.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
    all_queryset = queryset_data_OTST.union(queryset_data_RT)#用一次后会改变all_queryset本身，下次要出府使用需要重新定义
    selectProposer = [
        # {"value": "20795434", "number": "張宵凌"}, {"value": "20720831", "number": "劉婭茹"},
    ]
    for i in all_queryset.values("CurrentKeeper", "CurrentKeeper_CN").distinct().order_by("CurrentKeeper"):
        selectProposer.append({"value": i["CurrentKeeper"], "number": i["CurrentKeeper_CN"]})

    queryset_data_OTST = MateriaInDQA_Tum.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))
    queryset_data_RT = DQAMateria_TUMHistory.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
    all_queryset = queryset_data_OTST.union(queryset_data_RT)
    sectionProject = [
        # "GLS4I", "FLMA0", "GLS4A"
    ]
    for i in all_queryset.values("ProjectCode").distinct().order_by("ProjectCode"):
        sectionProject.append(i["ProjectCode"])

    queryset_data_OTST = MateriaInDQA_Tum.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))
    queryset_data_RT = DQAMateria_TUMHistory.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
    all_queryset = queryset_data_OTST.union(queryset_data_RT)
    sectionCustomer = [
        # "C38(AIO)", "A39", "C38(NB)"
                       ]
    for i in all_queryset.values("CustomerCode").distinct().order_by("CustomerCode"):
        sectionCustomer.append(i["CustomerCode"])

    queryset_data_OTST = MateriaInDQA_Tum.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))
    queryset_data_RT = DQAMateria_TUMHistory.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
    all_queryset = queryset_data_OTST.union(queryset_data_RT)
    sectionPhase = [
        # "B(DVT)", "C", "FFRT"
    ]
    for i in all_queryset.values("PhaseName").distinct().order_by("PhaseName"):
        sectionPhase.append(i["PhaseName"])

    queryset_data_OTST = MateriaInDQA_Tum.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))
    queryset_data_RT = DQAMateria_TUMHistory.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
    all_queryset = queryset_data_OTST.union(queryset_data_RT)
    sectionPN = [
        # "GA00000MP20", "DDC00002700", "DD10000WW00"
    ]
    for i in all_queryset.values("PN").distinct().order_by("PN"):
        sectionPN.append(i["PN"])

    queryset_data_OTST = MateriaInDQA_Tum.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))
    queryset_data_RT = DQAMateria_TUMHistory.objects.exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
    all_queryset = queryset_data_OTST.union(queryset_data_RT)
    sectionStatus = [
        # "測試中", "已退庫"
                     ]
    for i in all_queryset.values("Status").distinct().order_by("Status"):
        sectionStatus.append(i["Status"])

    # 表格數據
    mock_data = [
        # {"id": 1, "SiteName": "CN55", "FunctionName": "QAD", "PN": "GA00000MP20",
        #  "CurrentKeeper": "C1209AW", "CurrentKeeper_CN": "鄒麗錦", "ApplyReasonCategory": "",
        #  "ApplyReason": "For EOY10 SDV phase test", "InData": "2023-08-01",
        #  "ReturnOffline": "", "ReturnData": "2017-01-17 09:50:24.443", "Status": "測試中",
        #  "DeptNo": "KM0MAQACD0", "ItemNo": "", "CostCenter": "KM0MAQACD0", "ProjectCode": "EOY10",
        #  "Description": "PWR CORD 0014X1MX0016 3P US LT 10D C38A", "QTY": "", "PhaseName": "B(DVT)",
        #  "EOPDate": "2021/03/31",
        #  },
        # {"id": 2, "SiteName": "CN55", "FunctionName": "QAD", "PN": "GA00000MP20",
        #  "CurrentKeeper": "C1209AW", "CurrentKeeper_CN": "鄒麗錦", "ApplyReasonCategory": "",
        #  "ApplyReason": "For EOY10 SDV phase test", "InData": "2023-08-01",
        #  "ReturnOffline": "", "ReturnData": "2017-01-17 09:50:24.443", "Status": "測試中",
        #  "DeptNo": "KM0MAQACD0", "ItemNo": "", "CostCenter": "KM0MAQACD0", "ProjectCode": "EOY10",
        #  "Description": "PWR CORD 0014X1MX0016 3P US LT 10D C38A", "QTY": "", "PhaseName": "B(DVT)",
        #  "EOPDate": "2021/03/31",
        #  },
        # {"id": 3, "SiteName": "CN55", "FunctionName": "QAD", "PN": "GA00000MP20",
        #  "CurrentKeeper": "C1209AW", "CurrentKeeper_CN": "鄒麗錦", "ApplyReasonCategory": "",
        #  "ApplyReason": "For EOY10 SDV phase test", "InData": "2023-08-01",
        #  "ReturnOffline": "", "ReturnData": "2017-01-17 09:50:24.443", "Status": "測試中",
        #  "DeptNo": "KM0MAQACD0", "ItemNo": "", "CostCenter": "KM0MAQACD0", "ProjectCode": "EOY10",
        #  "Description": "PWR CORD 0014X1MX0016 3P US LT 10D C38A", "QTY": "", "PhaseName": "B(DVT)",
        #  "EOPDate": "2021/03/31",
        #  },
    ]

    if request.method == "POST":
        if request.POST.get('isGetData') == 'first':
            pass
        if request.POST.get('isGetData') == 'SEARCH':
            Proposer = request.POST.get('Proposer')
            Project = request.POST.get('Project')
            Customer = request.POST.get('Customer')
            PN = request.POST.get('PN')
            Phase = request.POST.get('Phase')
            Status = request.POST.get('Status')
            check_dic = {}
            if Customer:
                check_dic["CustomerCode"] = Customer
            if Project:
                check_dic["ProjectCode"] = Project
            if Phase:
                check_dic["PhaseName"] = Phase
            if PN:
                check_dic["PN"] = PN
            if Proposer:
                check_dic["CurrentKeeper"] = Proposer
            if Status:
                check_dic["Status"] = Status

            print(check_dic)
            queryset_data_OTST = MateriaInDQA_Tum.objects.filter(**check_dic).exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000"))
            queryset_data_RT = DQAMateria_TUMHistory.objects.filter(**check_dic).exclude(Q(PN__contains="PK1000") | Q(PN__contains="GA0000")).defer('ReturnID')
            all_queryset = queryset_data_OTST.union(queryset_data_RT)
            for i in all_queryset:
                mock_data.append(
                    {
                         "SiteName": i.SiteName, "FunctionName": i.FunctionName, "CustomerCode": i.CustomerCode, "PN": i.PN,
                         "CurrentKeeper": i.CurrentKeeper, "CurrentKeeper_CN": i.CurrentKeeper_CN, "ApplyReasonCategory": i.ApplyReasonCategory,
                         "ApplyReason": i.ApplyReason, "InData": str(i.InData),
                         "ReturnOffline": str(i.ReturnOffline), "ReturnData": str(i.ReturnData), "Status": i.Status,
                         "DeptNo": i.DeptNo, "ItemNo": i.ItemNo, "CostCenter": i.CostCenter, "ProjectCode": i.ProjectCode,
                         "Description": i.Description, "QTY": i.QTY, "PhaseName": i.PhaseName,
                         "EOPDate": str(i.EOPDate),
                    }
                )

        data = {
            "content": mock_data,
            "sectionProject": sectionProject,
            "selectProposer": selectProposer,
            "sectionCustomer": sectionCustomer,
            "sectionPhase": sectionPhase,
            "sectionPN": sectionPN,
            "sectionStatus": sectionStatus,
        }
        # print(data)
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'TUMHistory/MateriaHistory.html', locals())