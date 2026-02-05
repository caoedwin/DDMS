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
    onlineuser = request.session.get('account_DMS')
    isAdmin = True
    message = ''
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
    if request.method == 'GET' and 'tab' not in request.GET:
        return render(request, 'RetainedSample/RetainedSample.html', locals())
    # 以下处理数据API请求
    if request.method == 'GET':
        tab = request.GET.get('tab', 'summary')

        # 在RetainedSample_summary视图的summary部分修改
        # 在RetainedSample_summary视图的summary部分修改
        # 在RetainedSample_summary视图的summary部分修改
        if tab == 'summary':
            queryset = RetainedSample.objects.all()

            # 应用搜索条件
            project = request.GET.get('project', '')
            sample = request.GET.get('sample', '')
            manufacturer = request.GET.get('manufacturer', '')

            if project:
                queryset = queryset.filter(Project__icontains=project)
            if sample:
                queryset = queryset.filter(SampleName__icontains=sample)
            if manufacturer:
                queryset = queryset.filter(Manufacturer__icontains=manufacturer)

            # 提取过滤选项
            projects = queryset.values_list('Project', flat=True).distinct()
            samples = queryset.values_list('SampleName', flat=True).distinct()
            manufacturers = queryset.values_list('Manufacturer', flat=True).distinct()

            # 获取所有用户信息（使用您的UserInfo模型）
            from app01.models import UserInfo
            users = UserInfo.objects.filter(is_active=True).all()

            # 构建用户选项：格式为"姓名（工号）"
            user_options = []
            for user in users:
                if user.account and user.CNname:
                    display_name = f"{user.CNname} ({user.account})"
                    user_options.append({
                        'value': user.account,
                        'label': display_name
                    })
                elif user.account:
                    display_name = f"{user.username} ({user.account})"
                    user_options.append({
                        'value': user.account,
                        'label': display_name
                    })
                else:
                    display_name = user.username
                    user_options.append({
                        'value': user.username,
                        'label': display_name
                    })


            # 尝试获取UserInfo中的当前用户详细信息
            try:
                # print(onlineuser)
                # print(UserInfo.objects.get(account=onlineuser))
                user_info = UserInfo.objects.get(account=onlineuser)
                # 当前用户信息
                current_user_info = {
                    'value': user_info.account,  # 工号
                    'display_name': f"{user_info.CNname} ({user_info.account})"  # 显示格式
                }

            except Exception as e:
                print(str(e))

            updateData = {
                'success': True,
                'samples': list(queryset.values()),
                'filter_options': {
                    'projects': list(projects),
                    'samples': list(samples),
                    'manufacturers': list(manufacturers),
                    'users': user_options,
                },
                'current_user': current_user_info,
                'is_admin': isAdmin
            }
            return HttpResponse(json.dumps(updateData), content_type="application/json")
        if tab == "myBorrow":
            updateData = {
                'is_admin': isAdmin,
                'success': True,
                'samples': [],
                'filter_options': {
                    'projects': ["項目1", "項目2",],
                    'samples': ["樣品1", "樣品2",],
                    'manufacturers': ["廠商1", "廠商2",],
                    'borrowers': ["借用人1", "借用人2",]
                }
            }
            # print(updateData)
            return HttpResponse(json.dumps(updateData), content_type="application/json")
        if tab == "myApproval":
            updateData = {
                'is_admin': isAdmin,
                'success': True,
                'samples': [],
                'filter_options': {
                    'projects': ["項目1", "項目2",],
                    'samples': ["樣品1", "樣品2",],
                    'manufacturers': ["廠商1", "廠商2",],
                    'borrowers': ["借用人1", "借用人2",]
                }
            }
            # print(updateData)
            return HttpResponse(json.dumps(updateData), content_type="application/json")
        if tab == "records":
            updateData = {
                'is_admin': isAdmin,
                'success': True,
                'samples': [],
                'filter_options': {
                    'projects': ["項目1", "項目2",],
                    'samples': ["樣品1", "樣品2",],
                    'manufacturers': ["廠商1", "廠商2",],
                    'borrowers': ["借用人1", "借用人2",]
                }
            }
            # print(updateData)
            return HttpResponse(json.dumps(updateData), content_type="application/json")
        if tab == "baofeiRecord":
            updateData = {
                'is_admin': isAdmin,
                'success': True,
                'samples': [],
                'filter_options': {
                    'projects': ["項目1", "項目2",],
                    'samples': ["樣品1", "樣品2",],
                    'manufacturers': ["廠商1", "廠商2",],
                    'borrowers': ["借用人1", "借用人2",]
                }
            }
            # print(updateData)
            return HttpResponse(json.dumps(updateData), content_type="application/json")
    if request.method == "POST":
        if request.POST:
            try:
                post_data = json.loads(request.body)
                key_post = post_data.get('Key_Post', '')

                if key_post == 'adddata':
                    # 添加新记录
                    new_sample = RetainedSample.objects.create(
                        Project=post_data.get('Project', ''),
                        Owner=post_data.get('Owner', ''),  # 保存工号
                        SampleName=post_data.get('SampleName', ''),
                        Manufacturer=post_data.get('Manufacturer', ''),
                        SampleBatch=post_data.get('SampleBatch', ''),
                        SampleQuantity=post_data.get('SampleQuantity', 0),
                        Retainer=post_data.get('Retainer', ''),  # 保存工号
                        RetainStart=post_data.get('RetainStart', ''),
                        RetainPeriod=post_data.get('RetainPeriod', 0),
                        RetainPosition=post_data.get('RetainPosition', ''),
                        BorrowedQuantity=0,
                        RemainedQuantity=post_data.get('SampleQuantity', 0),
                        UnderApprovalQuantity=0
                    )
                    return JsonResponse({'success': True, 'message': '添加成功'})

                elif key_post == 'editdata':
                    # 编辑记录
                    sample_id = post_data.get('id')
                    if not sample_id:
                        return JsonResponse({'success': False, 'message': 'ID不能为空'})

                    try:
                        sample = RetainedSample.objects.get(id=sample_id)
                        # 更新字段（專案名稱不可修改）
                        sample.Owner = post_data.get('Owner', sample.Owner)  # 更新工号
                        sample.SampleName = post_data.get('SampleName', sample.SampleName)
                        sample.Manufacturer = post_data.get('Manufacturer', sample.Manufacturer)
                        sample.SampleBatch = post_data.get('SampleBatch', sample.SampleBatch)

                        # 处理数量变化
                        old_quantity = sample.SampleQuantity
                        new_quantity = post_data.get('SampleQuantity', old_quantity)

                        if new_quantity != old_quantity:
                            quantity_diff = new_quantity - old_quantity
                            sample.SampleQuantity = new_quantity
                            sample.RemainedQuantity = max(0, sample.RemainedQuantity + quantity_diff)

                        sample.Retainer = post_data.get('Retainer', sample.Retainer)  # 更新工号
                        sample.RetainStart = post_data.get('RetainStart', sample.RetainStart)
                        sample.RetainPeriod = post_data.get('RetainPeriod', sample.RetainPeriod)
                        sample.RetainPosition = post_data.get('RetainPosition', sample.RetainPosition)

                        sample.save()
                        return JsonResponse({'success': True, 'message': '更新成功'})

                    except RetainedSample.DoesNotExist:
                        return JsonResponse({'success': False, 'message': '记录不存在'})

                elif key_post == 'deletedata':
                    # 删除记录
                    sample_id = post_data.get('id')
                    if not sample_id:
                        return JsonResponse({'success': False, 'message': 'ID不能为空'})

                    try:
                        sample = RetainedSample.objects.get(id=sample_id)

                        # 检查是否可以删除（例如：有借用记录的不能删除）
                        if sample.BorrowedQuantity > 0 or sample.UnderApprovalQuantity > 0:
                            return JsonResponse({'success': False, 'message': '该样品有借用记录或待审批记录，不能删除'})

                        sample.delete()
                        return JsonResponse({'success': True, 'message': '删除成功'})

                    except RetainedSample.DoesNotExist:
                        return JsonResponse({'success': False, 'message': '记录不存在'})

                else:
                    return JsonResponse({'success': False, 'message': '未知操作类型'})

            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': '请求数据格式错误'})
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                return JsonResponse({'success': False, 'message': str(e)})

            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': '请求数据格式错误'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})


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
            "message": message,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'RetainedSample/RetainedSample.html', locals())
