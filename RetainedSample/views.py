from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime, os, json
from django.db.models import Max, Min, Sum, Count, Q
from django.http import JsonResponse
from app01.models import UserInfo
from .models import RetainedSample, PersonalRetainedSample, RetainedSampleRecord


@csrf_exempt
def RetainedSample_summary(request):
    if not request.session.get('is_login_DMS', None):
        return redirect('/login/')

    weizhi = "留樣系統/管理"
    onlineuser = request.session.get('account_DMS')
    isAdmin = False

    # 检查用户是否为管理员
    try:
        user_info = UserInfo.objects.get(account=onlineuser)
        roles = []
        if user_info:
            for i in user_info.role.all():
                roles.append(i.name)
        for i in roles:
            if 'Sys_Admin' in i or 'C38_RetainedSam_admin' in i:
                isAdmin = True
    except Exception as e:
        print(f"获取用户权限失败: {str(e)}")

    # 如果是页面加载请求（非AJAX且无tab参数）
    has_tab_param = 'tab' in request.GET
    if request.method == 'GET' and not has_tab_param:
        return render(request, 'RetainedSample/RetainedSample.html', locals())
    if request.method == 'GET':
        tab = request.GET.get('tab', 'summary')
        print('tab')

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

            # 获取所有用户信息
            users = UserInfo.objects.filter(is_active=True).all()
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

            # 获取当前用户信息
            try:
                user_info = UserInfo.objects.get(account=onlineuser)
                current_user_info = {
                    'value': user_info.account,
                    'display_name': f"{user_info.CNname} ({user_info.account})" if user_info.CNname else user_info.username,
                    'account': user_info.account,
                    'name': user_info.CNname or user_info.username
                }
            except:
                current_user_info = {
                    'value': onlineuser,
                    'display_name': onlineuser,
                    'account': onlineuser,
                    'name': onlineuser
                }

            # 获取留样位置选项
            retain_positions = RetainedSample.objects.values_list('RetainPosition', flat=True).distinct()

            updateData = {
                'success': True,
                'samples': list(queryset.values()),
                'filter_options': {
                    'projects': list(projects),
                    'samples': list(samples),
                    'manufacturers': list(manufacturers),
                    'users': user_options,
                    'retain_positions': list(retain_positions)
                },
                'current_user': current_user_info,
                'is_admin': isAdmin
            }
            # print(updateData)
            return JsonResponse(updateData)

        elif tab == "myBorrow":
            # 获取当前用户的借用记录
            try:
                user_info = UserInfo.objects.get(account=onlineuser)
                personal_samples = PersonalRetainedSample.objects.filter(
                    Borrower=user_info.account
                ).order_by('-created_at')

                borrow_data = []
                for ps in personal_samples:
                    borrow_data.append({
                        'id': ps.id,
                        'SampleName': ps.Sample.SampleName if ps.Sample else '',
                        'Project': ps.Sample.Project if ps.Sample else '',
                        'BorrowQuantity': ps.BorrowQuantity,
                        'RemainedQuantity': ps.RemainedQuantity,
                        'BorrowedReson': ps.BorrowedReson,
                        'Status': ps.Status,
                        'created_at': ps.created_at.strftime('%Y-%m-%d %H:%M:%S') if ps.created_at else ''
                    })

                updateData = {
                    'success': True,
                    'my_borrows': borrow_data,
                    'is_admin': isAdmin
                }
            except Exception as e:
                print(f"获取我的借用失败: {str(e)}")
                updateData = {
                    'success': False,
                    'message': '获取数据失败',
                    'is_admin': isAdmin
                }
            return JsonResponse(updateData)

        elif tab == "myApproval":
            if not isAdmin:
                return JsonResponse({'success': False, 'message': '无权限访问'})

            # 获取待审批的借用记录和归还记录
            approval_list = []

            # 借用申请（状态为"借用確認中"）
            borrow_approvals = PersonalRetainedSample.objects.filter(
                Status='借用確認中'
            ).order_by('created_at')

            for ps in borrow_approvals:
                approval_list.append({
                    'id': ps.id,
                    'RecordType': '借用申請',
                    'SampleName': ps.Sample.SampleName if ps.Sample else '',
                    'Project': ps.Sample.Project if ps.Sample else '',
                    'Borrower': ps.Borrower,
                    'Quantity': ps.BorrowQuantity,
                    'Reason': ps.BorrowedReson,
                    'Status': '待审批',
                    'created_at': ps.created_at.strftime('%Y-%m-%d %H:%M:%S') if ps.created_at else ''
                })

            # 归还申请（状态为"歸還確認中"）
            return_approvals = PersonalRetainedSample.objects.filter(
                Status='歸還確認中'
            ).order_by('created_at')

            for ps in return_approvals:
                approval_list.append({
                    'id': ps.id,
                    'RecordType': '歸還申請',
                    'SampleName': ps.Sample.SampleName if ps.Sample else '',
                    'Project': ps.Sample.Project if ps.Sample else '',
                    'Borrower': ps.Borrower,
                    'Quantity': ps.ReturnRequestedQuantity,
                    'Reason': ps.ReturnReason,
                    'Status': '待确认',
                    'created_at': ps.ReturnRequestedAt.strftime('%Y-%m-%d %H:%M:%S') if ps.ReturnRequestedAt else ''
                })

            updateData = {
                'success': True,
                'approval_list': approval_list,
                'is_admin': isAdmin
            }
            return JsonResponse(updateData)

        elif tab == "records":
            # 获取所有借用记录（不包括未审批的）
            records = PersonalRetainedSample.objects.exclude(
                Status='借用確認中'
            ).order_by('-created_at')

            # 应用搜索条件
            project = request.GET.get('project', '')
            sample = request.GET.get('sample', '')
            manufacturer = request.GET.get('manufacturer', '')
            borrower = request.GET.get('borrower', '')

            if project or sample or manufacturer:
                # 先过滤样品
                sample_qs = RetainedSample.objects.all()
                if project:
                    sample_qs = sample_qs.filter(Project__icontains=project)
                if sample:
                    sample_qs = sample_qs.filter(SampleName__icontains=sample)
                if manufacturer:
                    sample_qs = sample_qs.filter(Manufacturer__icontains=manufacturer)

                sample_ids = sample_qs.values_list('id', flat=True)
                records = records.filter(Sample_id__in=sample_ids)

            if borrower:
                records = records.filter(Borrower__icontains=borrower)

            # 提取过滤选项
            projects = RetainedSample.objects.values_list('Project', flat=True).distinct()
            samples = RetainedSample.objects.values_list('SampleName', flat=True).distinct()
            manufacturers = RetainedSample.objects.values_list('Manufacturer', flat=True).distinct()
            borrowers = PersonalRetainedSample.objects.values_list('Borrower', flat=True).distinct()

            records_data = []
            for ps in records:
                records_data.append({
                    'SampleName': ps.Sample.SampleName if ps.Sample else '',
                    'Project': ps.Sample.Project if ps.Sample else '',
                    'Manufacturer': ps.Sample.Manufacturer if ps.Sample else '',
                    'Borrower': ps.Borrower,
                    'BorrowQuantity': ps.BorrowQuantity,
                    'BorrowedReson': ps.BorrowedReson,
                    'BorrowedStatus': '已借用' if ps.Status == '已借用' else ps.Status,
                    'ReturnedStatus': '已歸還' if ps.Status == '已歸還' else '未歸還',
                    'created_at': ps.created_at.strftime('%Y-%m-%d %H:%M:%S') if ps.created_at else ''
                })

            updateData = {
                'success': True,
                'borrow_records': records_data,
                'filter_options': {
                    'projects': list(projects),
                    'samples': list(samples),
                    'manufacturers': list(manufacturers),
                    'borrowers': list(borrowers)
                },
                'is_admin': isAdmin
            }
            return JsonResponse(updateData)

        elif tab == "scrapRecords":
            if not isAdmin:
                return JsonResponse({'success': False, 'message': '无权限访问'})

            # 获取报废记录
            scrap_records = RetainedSampleRecord.objects.filter(
                RecordType='報廢'
            ).order_by('-created_at')

            # 应用搜索条件
            project = request.GET.get('project', '')
            sample = request.GET.get('sample', '')
            manufacturer = request.GET.get('manufacturer', '')

            if project or sample or manufacturer:
                # 先过滤样品
                sample_qs = RetainedSample.objects.all()
                if project:
                    sample_qs = sample_qs.filter(Project__icontains=project)
                if sample:
                    sample_qs = sample_qs.filter(SampleName__icontains=sample)
                if manufacturer:
                    sample_qs = sample_qs.filter(Manufacturer__icontains=manufacturer)

                sample_ids = sample_qs.values_list('id', flat=True)
                scrap_records = scrap_records.filter(Sample_id__in=sample_ids)

            # 提取过滤选项
            projects = RetainedSample.objects.values_list('Project', flat=True).distinct()
            samples = RetainedSample.objects.values_list('SampleName', flat=True).distinct()
            manufacturers = RetainedSample.objects.values_list('Manufacturer', flat=True).distinct()

            scrap_data = []
            for sr in scrap_records:
                scrap_data.append({
                    'SampleName': sr.Sample.SampleName if sr.Sample else '',
                    'Project': sr.Sample.Project if sr.Sample else '',
                    'Manufacturer': sr.Sample.Manufacturer if sr.Sample else '',
                    'ScrappedBy': sr.Borrowed,
                    'ScrapQuantity': sr.BorrowQuantity,
                    'ScrapReason': sr.BorrowedReson,
                    'created_at': sr.created_at.strftime('%Y-%m-%d %H:%M:%S') if sr.created_at else ''
                })

            updateData = {
                'success': True,
                'scrap_records': scrap_data,
                'filter_options': {
                    'projects': list(projects),
                    'samples': list(samples),
                    'manufacturers': list(manufacturers)
                },
                'is_admin': isAdmin
            }
            return JsonResponse(updateData)

    elif request.method == "POST":
        try:
            post_data = json.loads(request.body)

            # 处理借用申请
            # 处理借用申请
            if post_data.get('borrowData') == 'borrowData':
                sample_id = post_data.get('sample_id')
                borrow_quantity = int(post_data.get('borrow_quantity', 0))
                borrow_reason = post_data.get('borrow_reason', '')

                if not sample_id or borrow_quantity <= 0:
                    return JsonResponse({'success': False, 'message': '参数错误'})

                try:
                    with transaction.atomic():
                        # 获取样品并锁定
                        sample = RetainedSample.objects.select_for_update().get(id=sample_id)

                        # 检查剩余数量是否足够（需要同时考虑已借出和签核中的数量）
                        available_quantity = sample.RemainedQuantity - sample.UnderApprovalQuantity
                        if available_quantity < borrow_quantity:
                            return JsonResponse({'success': False, 'message': '库存不足'})

                        # 正确更新样品数据
                        # 签核中数量增加
                        sample.UnderApprovalQuantity += borrow_quantity
                        # 剩余数量减少
                        sample.RemainedQuantity -= borrow_quantity
                        sample.save()

                        # 获取当前用户信息
                        try:
                            user_info = UserInfo.objects.get(account=onlineuser)
                            borrower_name = user_info.CNname or user_info.username
                            borrower_account = user_info.account
                        except:
                            borrower_name = onlineuser
                            borrower_account = onlineuser

                        # 创建个人借用记录
                        personal_sample = PersonalRetainedSample.objects.create(
                            Sample_id=sample_id,
                            Borrower=borrower_account,
                            Status='借用確認中',
                            BorrowQuantity=borrow_quantity,
                            BorrowedReson=borrow_reason,
                            RemainedQuantity=borrow_quantity  # 初始剩余借用数量等于借用数量
                        )

                        # 创建借用记录
                        RetainedSampleRecord.objects.create(
                            Sample_id=sample_id,
                            RecordType='借用申請',
                            Borrowed=borrower_account,
                            BorrowQuantity=borrow_quantity,
                            BorrowedReson=borrow_reason,
                            BorrowedStatus='待审批',
                            ReturnedStatus='未歸還'
                        )

                        return JsonResponse({'success': True, 'message': '借用申请提交成功'})

                except RetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '样品不存在'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'借用失败: {str(e)}'})

            # 处理同意借用
            elif post_data.get('scrapData') == 'scrapData' and post_data.get('record_id'):
                if not isAdmin:
                    return JsonResponse({'success': False, 'message': '无权限操作'})

                record_id = post_data.get('record_id')

                try:
                    with transaction.atomic():
                        # 获取借用记录
                        personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                            id=record_id,
                            Status='借用確認中'
                        )

                        # 获取样品
                        sample = personal_sample.Sample

                        # 更新样品数据
                        sample.BorrowedQuantity += personal_sample.BorrowQuantity
                        sample.UnderApprovalQuantity -= personal_sample.BorrowQuantity
                        sample.save()

                        # 更新借用记录状态
                        personal_sample.Status = '已借用'
                        personal_sample.ApprovedAt = datetime.datetime.now()
                        personal_sample.ApprovedBy = onlineuser
                        personal_sample.save()

                        # 获取操作人信息
                        try:
                            operator_info = UserInfo.objects.get(account=onlineuser)
                            operator_name = operator_info.CNname or operator_info.username
                        except:
                            operator_name = onlineuser

                        # 创建审批记录
                        RetainedSampleRecord.objects.create(
                            Sample=sample,
                            RecordType='借用審批',
                            Borrowed=personal_sample.Borrower,
                            BorrowQuantity=personal_sample.BorrowQuantity,
                            BorrowedReson=personal_sample.BorrowedReson,
                            BorrowedStatus='已批准',
                            ReturnedStatus='未歸還'
                        )

                        return JsonResponse({'success': True, 'message': '同意借用成功'})

                except PersonalRetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '借用记录不存在或状态不正确'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'审批失败: {str(e)}'})

            # 处理拒绝借用
            elif post_data.get('reject') == 'reject' and post_data.get('record_id'):
                if not isAdmin:
                    return JsonResponse({'success': False, 'message': '无权限操作'})

                record_id = post_data.get('record_id')

                try:
                    with transaction.atomic():
                        # 获取借用记录
                        personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                            id=record_id,
                            Status='借用確認中'
                        )

                        # 获取样品
                        sample = personal_sample.Sample

                        # 更新样品数据（退回数量）
                        sample.UnderApprovalQuantity -= personal_sample.BorrowQuantity
                        sample.RemainedQuantity += personal_sample.BorrowQuantity
                        sample.save()

                        # 更新借用记录状态
                        personal_sample.Status = '已拒絕'
                        personal_sample.RejectedAt = datetime.datetime.now()
                        personal_sample.RejectedBy = onlineuser
                        personal_sample.save()

                        # 获取操作人信息
                        try:
                            operator_info = UserInfo.objects.get(account=onlineuser)
                            operator_name = operator_info.CNname or operator_info.username
                        except:
                            operator_name = onlineuser

                        # 创建拒绝记录
                        RetainedSampleRecord.objects.create(
                            Sample=sample,
                            RecordType='借用審批',
                            Borrowed=personal_sample.Borrower,
                            BorrowQuantity=personal_sample.BorrowQuantity,
                            BorrowedReson=personal_sample.BorrowedReson,
                            BorrowedStatus='已拒绝',
                            ReturnedStatus='未歸還'
                        )

                        return JsonResponse({'success': True, 'message': '拒绝借用成功'})

                except PersonalRetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '借用记录不存在或状态不正确'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'拒绝失败: {str(e)}'})

            # 处理报废
            elif post_data.get('scrapData') == 'scrapData' and post_data.get('scrap_quantity'):
                if not isAdmin:
                    return JsonResponse({'success': False, 'message': '无权限操作'})

                sample_id = post_data.get('sample_id')
                scrap_quantity = int(post_data.get('scrap_quantity', 0))
                scrap_reason = post_data.get('scrap_reason', '')

                if not sample_id or scrap_quantity <= 0:
                    return JsonResponse({'success': False, 'message': '参数错误'})

                try:
                    with transaction.atomic():
                        # 获取样品
                        sample = RetainedSample.objects.select_for_update().get(id=sample_id)

                        # 检查剩余数量是否足够
                        if sample.RemainedQuantity < scrap_quantity:
                            return JsonResponse({'success': False, 'message': '报废数量超过剩余数量'})

                        # 更新样品数据
                        sample.RemainedQuantity -= scrap_quantity
                        sample.save()

                        # 获取操作人信息
                        try:
                            user_info = UserInfo.objects.get(account=onlineuser)
                            operator_name = user_info.CNname or user_info.username
                        except:
                            operator_name = onlineuser

                        # 创建报废记录
                        RetainedSampleRecord.objects.create(
                            Sample=sample,
                            RecordType='報廢',
                            Borrowed=onlineuser,
                            BorrowQuantity=scrap_quantity,
                            BorrowedReson=scrap_reason,
                            BorrowedStatus='已完成',
                            ReturnedStatus='未歸還'
                        )

                        return JsonResponse({'success': True, 'message': '报废成功'})

                except RetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '样品不存在'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'报废失败: {str(e)}'})

            # 处理新增记录
            elif post_data.get('Key_Post') == 'adddata':
                new_sample = RetainedSample.objects.create(
                    Project=post_data.get('Project', ''),
                    Owner=post_data.get('Owner', ''),
                    SampleName=post_data.get('SampleName', ''),
                    Manufacturer=post_data.get('Manufacturer', ''),
                    SampleBatch=post_data.get('SampleBatch', ''),
                    SampleQuantity=post_data.get('SampleQuantity', 0),
                    Retainer=post_data.get('Retainer', ''),
                    RetainStart=post_data.get('RetainStart', ''),
                    RetainPeriod=post_data.get('RetainPeriod', 0),
                    RetainPosition=post_data.get('RetainPosition', ''),
                    BorrowedQuantity=0,
                    RemainedQuantity=post_data.get('SampleQuantity', 0),
                    UnderApprovalQuantity=0
                )
                return JsonResponse({'success': True, 'message': '添加成功'})

            # 处理编辑记录
            elif post_data.get('Key_Post') == 'editdata':
                sample_id = post_data.get('id')
                if not sample_id:
                    return JsonResponse({'success': False, 'message': 'ID不能为空'})

                try:
                    sample = RetainedSample.objects.get(id=sample_id)
                    # 更新字段（專案名稱不可修改）
                    sample.Owner = post_data.get('Owner', sample.Owner)
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

                    sample.Retainer = post_data.get('Retainer', sample.Retainer)
                    sample.RetainStart = post_data.get('RetainStart', sample.RetainStart)
                    sample.RetainPeriod = post_data.get('RetainPeriod', sample.RetainPeriod)
                    sample.RetainPosition = post_data.get('RetainPosition', sample.RetainPosition)

                    sample.save()
                    return JsonResponse({'success': True, 'message': '更新成功'})

                except RetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '记录不存在'})

            # 处理删除记录
            elif post_data.get('Key_Post') == 'deletedata':
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

    return render(request, 'RetainedSample/RetainedSample.html', locals())


@csrf_exempt
def handle_approval(request):
    """处理审批操作（借用和归还的审批）"""
    if not request.session.get('is_login_DMS', None):
        return JsonResponse({'success': False, 'message': '请先登录'})

    onlineuser = request.session.get('account_DMS')

    # 检查是否为管理员
    isAdmin = False
    try:
        user_info = UserInfo.objects.get(account=onlineuser)
        roles = []
        for role in user_info.role.all():
            roles.append(role.name)
        for role_name in roles:
            if 'Sys_Admin' in role_name or 'C38_RetainedSam_admin' in role_name:
                isAdmin = True
                break
    except:
        pass

    if not isAdmin:
        return JsonResponse({'success': False, 'message': '无权限操作'})

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})

    try:
        post_data = json.loads(request.body)
        action_type = post_data.get('action_type', '')
        record_id = post_data.get('record_id')
        record_type = post_data.get('record_type', '')

        if not record_id:
            return JsonResponse({'success': False, 'message': '记录ID不能为空'})

        if action_type == 'confirm_approval':
            # 同意审批
            # 处理同意借用（在handle_approval函数中）
            if record_type == '借用申請':
                try:
                    with transaction.atomic():
                        # 获取借用记录
                        personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                            id=record_id,
                            Status='借用確認中'
                        )

                        # 获取样品
                        sample = personal_sample.Sample

                        # 更新样品数据
                        sample.BorrowedQuantity += personal_sample.BorrowQuantity
                        sample.UnderApprovalQuantity -= personal_sample.BorrowQuantity
                        # RemainedQuantity已经在借用申请时减少了，这里不需要再修改
                        sample.save()

                        # 更新借用记录状态
                        personal_sample.Status = '已借用'
                        personal_sample.ApprovedAt = datetime.datetime.now()
                        personal_sample.ApprovedBy = onlineuser
                        personal_sample.save()

                        # 创建审批记录...
                        return JsonResponse({'success': True, 'message': '同意借用成功'})

                except PersonalRetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '借用记录不存在或状态不正确'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'审批失败: {str(e)}'})

            elif record_type == '歸還申請':
                # 同意归还申请
                try:
                    with transaction.atomic():
                        # 获取借用记录
                        personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                            id=record_id,
                            Status='歸還確認中'
                        )

                        # 获取样品
                        sample = personal_sample.Sample

                        # 更新借用记录
                        return_quantity = personal_sample.ReturnRequestedQuantity
                        personal_sample.RemainedQuantity -= return_quantity

                        # 如果全部归还，则状态改为已归还
                        if personal_sample.RemainedQuantity <= 0:
                            personal_sample.Status = '已歸還'
                            personal_sample.ReturnedAt = datetime.datetime.now()
                            personal_sample.ReturnedQuantity = personal_sample.BorrowQuantity
                        else:
                            personal_sample.Status = '已借用'
                            personal_sample.ReturnedQuantity = personal_sample.BorrowQuantity - personal_sample.RemainedQuantity

                        personal_sample.save()

                        # 更新样品数据
                        sample.BorrowedQuantity -= return_quantity
                        sample.RemainedQuantity += return_quantity
                        sample.save()

                        # 获取操作人信息
                        try:
                            operator_info = UserInfo.objects.get(account=onlineuser)
                            operator_name = operator_info.CNname or operator_info.username
                        except:
                            operator_name = onlineuser

                        # 创建归还确认记录
                        RetainedSampleRecord.objects.create(
                            Sample=sample,
                            RecordType='歸還確認',
                            Borrowed=personal_sample.Borrower,
                            BorrowQuantity=return_quantity,
                            BorrowedReson=personal_sample.ReturnReason,
                            BorrowedStatus='已批准',
                            ReturnedStatus='已歸還' if personal_sample.RemainedQuantity <= 0 else '部分歸還'
                        )

                        return JsonResponse({'success': True, 'message': '同意歸還成功'})

                except PersonalRetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '歸還記錄不存在或狀態不正確'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'审批失败: {str(e)}'})
            else:
                return JsonResponse({'success': False, 'message': '未知的审批类型'})

        elif action_type == 'reject_approval':
            # 拒绝审批
            reject_reason = post_data.get('reject_reason', '')

            if record_type == '借用申請':
                # 拒绝借用申请
                try:
                    with transaction.atomic():
                        # 获取借用记录
                        personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                            id=record_id,
                            Status='借用確認中'
                        )

                        # 获取样品
                        sample = personal_sample.Sample

                        # 更新样品数据（退回数量）
                        sample.UnderApprovalQuantity -= personal_sample.BorrowQuantity
                        sample.RemainedQuantity += personal_sample.BorrowQuantity
                        sample.save()

                        # 更新借用记录状态
                        personal_sample.Status = '已拒絕'
                        personal_sample.RejectedAt = datetime.datetime.now()
                        personal_sample.RejectedBy = onlineuser
                        personal_sample.save()

                        # 获取操作人信息
                        try:
                            operator_info = UserInfo.objects.get(account=onlineuser)
                            operator_name = operator_info.CNname or operator_info.username
                        except:
                            operator_name = onlineuser

                        # 创建拒绝记录
                        RetainedSampleRecord.objects.create(
                            Sample=sample,
                            RecordType='借用審批',
                            Borrowed=personal_sample.Borrower,
                            BorrowQuantity=personal_sample.BorrowQuantity,
                            BorrowedReson=f'拒絕: {reject_reason}',
                            BorrowedStatus='已拒绝',
                            ReturnedStatus='未歸還'
                        )

                        return JsonResponse({'success': True, 'message': '拒絕借用成功'})

                except PersonalRetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '借用记录不存在或状态不正确'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'拒绝失败: {str(e)}'})

            elif record_type == '歸還申請':
                # 拒绝归还申请
                try:
                    with transaction.atomic():
                        # 获取借用记录
                        personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                            id=record_id,
                            Status='歸還確認中'
                        )

                        # 获取样品
                        sample = personal_sample.Sample

                        # 更新借用记录状态
                        personal_sample.Status = '已借用'
                        personal_sample.save()

                        # 获取操作人信息
                        try:
                            operator_info = UserInfo.objects.get(account=onlineuser)
                            operator_name = operator_info.CNname or operator_info.username
                        except:
                            operator_name = onlineuser

                        # 创建拒绝归还记录
                        RetainedSampleRecord.objects.create(
                            Sample=sample,
                            RecordType='歸還審批',
                            Borrowed=personal_sample.Borrower,
                            BorrowQuantity=0,
                            BorrowedReson=f'拒絕歸還: {reject_reason}',
                            BorrowedStatus='已拒绝',
                            ReturnedStatus='未歸還'
                        )

                        return JsonResponse({'success': True, 'message': '已拒絕歸還申請'})

                except PersonalRetainedSample.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '借用记录不存在或状态不正确'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'拒绝失败: {str(e)}'})
            else:
                return JsonResponse({'success': False, 'message': '未知的审批类型'})

        else:
            return JsonResponse({'success': False, 'message': '未知操作类型'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误'})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
def handle_return(request):
    """处理归还申请"""
    if not request.session.get('is_login_DMS', None):
        return JsonResponse({'success': False, 'message': '请先登录'})

    onlineuser = request.session.get('account_DMS')

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})

    try:
        post_data = json.loads(request.body)
        action_type = post_data.get('action_type', '')

        if action_type == 'request_return':
            # 用户申请归还
            record_id = post_data.get('record_id')
            return_quantity = int(post_data.get('return_quantity', 0))
            return_reason = post_data.get('return_reason', '')

            if not record_id or return_quantity <= 0:
                return JsonResponse({'success': False, 'message': '参数错误'})

            try:
                with transaction.atomic():
                    # 获取借用记录
                    personal_sample = PersonalRetainedSample.objects.select_for_update().get(
                        id=record_id,
                        Borrower=onlineuser,
                        Status='已借用'
                    )

                    # 检查归还数量是否有效
                    if return_quantity > personal_sample.RemainedQuantity:
                        return JsonResponse({'success': False, 'message': '归还数量超过剩余借用数量'})

                    # 获取样品信息
                    sample = personal_sample.Sample

                    # 更新借用记录
                    personal_sample.Status = '歸還確認中'
                    personal_sample.ReturnRequestedAt = datetime.datetime.now()
                    personal_sample.ReturnRequestedQuantity = return_quantity
                    personal_sample.ReturnReason = return_reason
                    personal_sample.save()

                    # 获取操作人信息
                    try:
                        user_info = UserInfo.objects.get(account=onlineuser)
                        operator_name = user_info.CNname or user_info.username
                    except:
                        operator_name = onlineuser

                    # 创建归还申请记录
                    RetainedSampleRecord.objects.create(
                        Sample=sample,
                        RecordType='歸還申請',
                        Borrowed=onlineuser,
                        BorrowQuantity=return_quantity,
                        BorrowedReson=return_reason,
                        BorrowedStatus='待确认',
                        ReturnedStatus='未歸還'
                    )

                    return JsonResponse({'success': True, 'message': '归还申请提交成功'})

            except PersonalRetainedSample.DoesNotExist:
                return JsonResponse({'success': False, 'message': '借用记录不存在或状态不正确'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'归还申请失败: {str(e)}'})

        else:
            return JsonResponse({'success': False, 'message': '未知操作类型'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误'})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': str(e)})