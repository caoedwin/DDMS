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
from .models import Cabinet, CabinetGrid, GridRecord

@csrf_exempt
def CabinetManage_edit(request):
    if not request.session.get('is_login_DMS', None):
        # print(request.session.get('is_login', None))
        return redirect('/login/')
    weizhi = "智能柜体/管理"
    CustomerOptions = []
    for i in CabinetGrid._meta.get_field('Customer').choices:
        CustomerOptions.append(i[0])
    isAdmin = False
    roles = []
    onlineuser = request.session.get('account_DMS')
    currentUser = {"name": onlineuser, "phone": ''}
    # print(onlineuser)
    if UserInfo.objects.filter(account=onlineuser).first():
        for i in UserInfo.objects.filter(account=onlineuser).first().role.all():
            roles.append(i.name)
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
    for i in roles:
        if i == 'Sys_Admin' or i == 'CabinetManageAdmin':
            isAdmin = True

    # print(request.method)
    if request.method == "POST":
        if 'first' in str(request.body):
            pass
        if 'DeleteCabinet' in str(request.body):
            cabinet_id = request.POST.get('cabinetId')
            cabinet = Cabinet.objects.get(id=cabinet_id)
            # 检查是否存在非空闲状态的柜格
            non_free_grids = CabinetGrid.objects.filter(
                cabinet=cabinet
            ).exclude(status=0)  # 排除空闲状态(status=0)

            if non_free_grids.exists():
                occupied_positions = list(non_free_grids.values_list('position', flat=True))
                errMsg = "柜体中存在非空闲柜格，无法删除"
            else:
                # 直接删除柜体即可（级联删除会自动处理关联的柜格和记录）
                # 设置了 on_delete=models.CASCADE。这意味着当删除一个 CabinetGrid 实例时，所有关联的 GridRecord 记录也会被自动删除。因此，在删除 CabinetGrid 时，不需要显式地先删除 GridRecord。
                cabinet.delete()


        else:
            try:
                request.body

            except:
                pass
            else:
                if 'addCabinet' in str(request.body):
                    responseData = json.loads(request.body)
                    CabinetsInfo = responseData["newCabinet"]
                    Cabinet_create_dic = {
                        "name": CabinetsInfo["name"],
                        "location": CabinetsInfo["location"],
                        "description": CabinetsInfo["description"],
                        "rows": CabinetsInfo["rows"],
                        "cols": CabinetsInfo["cols"],
                    }
                    try:
                        with transaction.atomic():
                            Cabinet_obj = Cabinet.objects.create(**Cabinet_create_dic)
                            CabinetGrids_list = []
                            for row in CabinetsInfo["gridData"]:
                                for col in row:
                                    data = {
                                        "cabinet_id": Cabinet_obj.id,
                                        "row": col['rowIndex'],
                                        "col": col['colIndex'],
                                        "position": col['position'],
                                        "status": col['status'],
                                        "Customer": col['Customer'],
                                        "ProCode": col['ProCode'],
                                        "CampalCode": col['CampalCode'],
                                        "Brow_at": col['borrowDate'] if col['borrowDate'] and col['borrowDate'] != 'null' else None,
                                        "BrowReson": col['BrowReson'],
                                        "Take_at": col['takeoutDate'] if col['takeoutDate'] and col['takeoutDate'] != 'null' else None,
                                        "TakeReson": col['TakeReson'],
                                        "Back_at": col['reserveDate'] if col['reserveDate'] and col['reserveDate'] != 'null' else None,
                                        "user": col['user'],
                                        "phone": col['phone'],
                                        "notes": col['notes'],
                                        "creator": onlineuser,
                                    }
                                    CabinetGrids_list.append(CabinetGrid(**data))
                            # print(CabinetGrids_list)
                            CabinetGrid.objects.bulk_create(CabinetGrids_list)
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                #管理员编辑单元格
                if 'isSaveCell' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                                    #柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                                    # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                                    # "row": responseData['rowIndex'],
                                    # "col": responseData['colIndex'],
                                    "position": responseData['position'],
                                    #借用信息
                                    "status": responseData['status'],
                                    "Customer": responseData['Customer'],
                                    "ProCode": responseData['ProCode'],
                                    "CampalCode": responseData['CampalCode'],
                                    "Brow_at": responseData['borrowDate'] if responseData['borrowDate'] and responseData['borrowDate'] != 'null' else None,
                                    "BrowReson": responseData['BrowReson'],
                                    "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData['takeoutDate'] != 'null' else None,
                                    "TakeReson": responseData['TakeReson'],
                                    "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData['reserveDate'] != 'null' else None,
                                    "user": responseData['user'],
                                    "phone": responseData['phone'],
                                    "notes": responseData['notes'],
                                    # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                                }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            #历史记录
                            createGridRecord_dic = {
                                "grid_id": ID,
                                "action": 'update',
                                "old_status": responseData['old_status'],
                                "new_status": responseData['status'],

                                "Customer": responseData['Customer'],
                                "ProCode": responseData['ProCode'],
                                "CampalCode": responseData['CampalCode'],
                                "Brow_at": responseData['borrowDate'] if responseData['borrowDate'] and responseData[
                                    'borrowDate'] != 'null' else None,
                                "BrowReson": responseData['BrowReson'],
                                "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                                    'takeoutDate'] != 'null' else None,
                                "TakeReson": responseData['TakeReson'],
                                "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData[
                                    'reserveDate'] != 'null' else None,
                                "user": responseData['user'],
                                "phone": responseData['phone'],
                                "notes": responseData['notes'],
                            }
                            # print(createGridRecord_dic)
                            GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                #用户点击预约
                if 'UserBorrow' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                                    #柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                                    # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                                    # "row": responseData['rowIndex'],
                                    # "col": responseData['colIndex'],
                                    "position": responseData['position'],
                                    #借用信息
                                    "status": responseData['status'],
                                    "Customer": responseData['Customer'],
                                    "ProCode": responseData['ProCode'],
                                    "CampalCode": responseData['CampalCode'],
                                    "Brow_at": responseData['borrowDate'] if responseData['borrowDate'] and responseData['borrowDate'] != 'null' else None,
                                    "BrowReson": responseData['BrowReson'],
                                    "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData['takeoutDate'] != 'null' else None,
                                    "TakeReson": responseData['TakeReson'],
                                    "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData['reserveDate'] != 'null' else None,
                                    "user": onlineuser,
                                    "phone": responseData['phone'],
                                    "notes": responseData['notes'],
                                    # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                                }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            # #历史记录
                            # createGridRecord_dic = {
                            #     "grid_id": ID,
                            #     "action": 'update',
                            #     "old_status": responseData['old_status'],
                            #     "new_status": responseData['status'],
                            #
                            #     "Customer": responseData['Customer'],
                            #     "ProCode": responseData['ProCode'],
                            #     "CampalCode": responseData['CampalCode'],
                            #     "Brow_at": responseData['borrowDate'] if responseData['borrowDate'] and responseData[
                            #         'borrowDate'] != 'null' else None,
                            #     "BrowReson": responseData['BrowReson'],
                            #     "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                            #         'takeoutDate'] != 'null' else None,
                            #     "TakeReson": responseData['TakeReson'],
                            #     "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData[
                            #         'reserveDate'] != 'null' else None,
                            #     "user": responseData['user'],
                            #     "phone": responseData['phone'],
                            #     "notes": responseData['notes'],
                            # }
                            # # print(createGridRecord_dic)
                            # GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                # 用户点击预约
                if 'cancelReserve' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                        # 柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                        # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                        # "row": responseData['rowIndex'],
                        # "col": responseData['colIndex'],
                        # "position": responseData['position'],
                        # 借用信息
                        "status": responseData['status'],
                        "Customer": '',
                        "ProCode": '',
                        "CampalCode": '',
                        "Brow_at": None,
                        "BrowReson": '',
                        # "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                        #     'takeoutDate'] != 'null' else None,
                        # "TakeReson": responseData['TakeReson'],
                        # "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData[
                        #     'reserveDate'] != 'null' else None,
                        "user": '',
                        "phone": '',
                        # "notes": responseData['notes'],
                        # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                    }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            # #历史记录
                            # createGridRecord_dic = {
                            #     "grid_id": ID,
                            #     "action": 'update',
                            #     "old_status": responseData['old_status'],
                            #     "new_status": responseData['status'],
                            #
                            #     "Customer": responseData['Customer'],
                            #     "ProCode": responseData['ProCode'],
                            #     "CampalCode": responseData['CampalCode'],
                            #     "Brow_at": responseData['borrowDate'] if responseData['borrowDate'] and responseData[
                            #         'borrowDate'] != 'null' else None,
                            #     "BrowReson": responseData['BrowReson'],
                            #     "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                            #         'takeoutDate'] != 'null' else None,
                            #     "TakeReson": responseData['TakeReson'],
                            #     "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData[
                            #         'reserveDate'] != 'null' else None,
                            #     "user": responseData['user'],
                            #     "phone": responseData['phone'],
                            #     "notes": responseData['notes'],
                            # }
                            # # print(createGridRecord_dic)
                            # GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                # 管理员确认借出
                if 'confirmBorrow' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                        # 柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                        # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                        # "row": responseData['rowIndex'],
                        # "col": responseData['colIndex'],
                        # "position": responseData['position'],
                        # 借用信息
                        "status": responseData['status'],
                        # "Customer": responseData['Customer'],
                        # "ProCode": responseData['ProCode'],
                        # "CampalCode": responseData['CampalCode'],
                        "Brow_at": datetime.datetime.now().strftime(
                                                              "%Y-%m-%d %H:%M:%S"),
                        # "BrowReson": responseData['BrowReson'],
                        # "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                        #     'takeoutDate'] != 'null' else None,
                        # "TakeReson": responseData['TakeReson'],
                        # "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData[
                        #     'reserveDate'] != 'null' else None,
                        # "user": responseData['user'],
                        # "phone": responseData['phone'],
                        # "notes": responseData['notes'],
                        # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                    }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            # 历史记录
                            createGridRecord_dic = {
                                "grid_id": ID,
                                "action": 'update',
                                "old_status": responseData['old_status'],
                                "new_status": responseData['status'],

                                "Customer": responseData['Customer'],
                                "ProCode": responseData['ProCode'],
                                "CampalCode": responseData['CampalCode'],
                                "Brow_at": datetime.datetime.now().strftime(
                                                              "%Y-%m-%d %H:%M:%S"),
                                "BrowReson": responseData['BrowReson'],
                                "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and
                                                                          responseData[
                                                                              'takeoutDate'] != 'null' else None,
                                "TakeReson": responseData['TakeReson'],
                                "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and
                                                                          responseData[
                                                                              'reserveDate'] != 'null' else None,
                                "user": responseData['user'],
                                "phone": responseData['phone'],
                                "notes": responseData['notes'],
                            }
                            # print(createGridRecord_dic)
                            GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                # 用户取出保留
                if 'confirmTakeOut' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                        # 柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                        # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                        # "row": responseData['rowIndex'],
                        # "col": responseData['colIndex'],
                        # "position": responseData['position'],
                        # 借用信息
                        "status": responseData['status'],
                        # "Customer": responseData['Customer'],
                        # "ProCode": responseData['ProCode'],
                        # "CampalCode": responseData['CampalCode'],
                        # "Brow_at": datetime.datetime.now().strftime(
                        #     "%Y-%m-%d %H:%M:%S"),
                        # "BrowReson": responseData['BrowReson'],
                        "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                            'takeoutDate'] != 'null' else None,#这个地方时前端获取当前日期
                        "TakeReson": responseData['TakeReson'],
                        "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and responseData[
                            'reserveDate'] != 'null' else None,
                        # "user": responseData['user'],
                        # "phone": responseData['phone'],
                        # "notes": responseData['notes'],
                        # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                    }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            # 历史记录
                            createGridRecord_dic = {
                                "grid_id": ID,
                                "action": 'update',
                                "old_status": responseData['old_status'],
                                "new_status": responseData['status'],

                                "Customer": responseData['Customer'],
                                "ProCode": responseData['ProCode'],
                                "CampalCode": responseData['CampalCode'],
                                "Brow_at": datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"),
                                "BrowReson": responseData['BrowReson'],
                                "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and
                                                                          responseData[
                                                                              'takeoutDate'] != 'null' else None,
                                "TakeReson": responseData['TakeReson'],
                                "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and
                                                                          responseData[
                                                                              'reserveDate'] != 'null' else None,
                                "user": responseData['user'],
                                "phone": responseData['phone'],
                                "notes": responseData['notes'],
                            }
                            # print(createGridRecord_dic)
                            GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                # 用户取消保留，机器放回
                if 'cancelTakenReserve' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                        # 柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                        # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                        # "row": responseData['rowIndex'],
                        # "col": responseData['colIndex'],
                        # "position": responseData['position'],
                        # 借用信息
                        "status": responseData['status'],
                        # "Customer": responseData['Customer'],
                        # "ProCode": responseData['ProCode'],
                        # "CampalCode": responseData['CampalCode'],
                        # "Brow_at": datetime.datetime.now().strftime(
                        #     "%Y-%m-%d %H:%M:%S"),
                        # "BrowReson": responseData['BrowReson'],
                        # "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and responseData[
                        #     'takeoutDate'] != 'null' else None,  # 这个地方时前端获取当前日期
                        # "TakeReson": responseData['TakeReson'],
                        "Back_at": None,
                        # "user": responseData['user'],
                        # "phone": responseData['phone'],
                        # "notes": responseData['notes'],
                        # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                    }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            # 历史记录
                            createGridRecord_dic = {
                                "grid_id": ID,
                                "action": 'update',
                                "old_status": responseData['old_status'],
                                "new_status": responseData['status'],

                                "Customer": responseData['Customer'],
                                "ProCode": responseData['ProCode'],
                                "CampalCode": responseData['CampalCode'],
                                "Brow_at": datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"),
                                "BrowReson": responseData['BrowReson'],
                                "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and
                                                                          responseData[
                                                                              'takeoutDate'] != 'null' else None,
                                "TakeReson": responseData['TakeReson'],
                                "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and
                                                                          responseData[
                                                                              'reserveDate'] != 'null' else None,
                                "user": responseData['user'],
                                "phone": responseData['phone'],
                                "notes": responseData['notes'],
                            }
                            # print(createGridRecord_dic)
                            GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)
                # 用户归还存储格
                if 'returnCell' in str(request.body):
                    responseData = json.loads(request.body)
                    ID = responseData['Gridid']
                    # print(id)
                    updateCabinetGrid_dic = {
                        # 柜体信息，除了position（其实就是格子名称），创建后就不允许改动
                        # "cabinet_id": responseData['cabinetId'],#创建后就不允许改动
                        # "row": responseData['rowIndex'],
                        # "col": responseData['colIndex'],
                        # "position": responseData['position'],
                        # 借用信息
                        "status": responseData['status'],
                        "Customer": '',
                        "ProCode": '',
                        "CampalCode": '',
                        "Brow_at": None,
                        "BrowReson": '',
                        "Take_at": None,  # 这个地方时前端获取当前日期
                        "TakeReson": '',
                        "Back_at": None,
                        "user": '',
                        "phone": '',
                        "notes": '',
                        # "creator": onlineuser,#只有创建时需要填写，后面就不让改动
                    }
                    try:
                        with transaction.atomic():
                            CabinetGrid.objects.filter(id=ID).update(**updateCabinetGrid_dic)
                            # 历史记录
                            createGridRecord_dic = {
                                "grid_id": ID,
                                "action": 'update',
                                "old_status": responseData['old_status'],
                                "new_status": responseData['status'],

                                "Customer": responseData['Customer'],
                                "ProCode": responseData['ProCode'],
                                "CampalCode": responseData['CampalCode'],
                                "Brow_at": datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"),
                                "BrowReson": responseData['BrowReson'],
                                "Take_at": responseData['takeoutDate'] if responseData['takeoutDate'] and
                                                                          responseData[
                                                                              'takeoutDate'] != 'null' else None,
                                "TakeReson": responseData['TakeReson'],
                                "Back_at": responseData['reserveDate'] if responseData['reserveDate'] and
                                                                          responseData[
                                                                              'reserveDate'] != 'null' else None,
                                "user": responseData['user'],
                                "phone": responseData['phone'],
                                "notes": responseData['notes'],
                            }
                            # print(createGridRecord_dic)
                            GridRecordresult = GridRecord.objects.create(**createGridRecord_dic)
                            # print(GridRecordresult, 'GridRecordresult')
                    except Exception as e:
                        print(str(e))
                        errMsg = str(e)


        #mock_data
        for i in Cabinet.objects.all():
            cabinets_dic = {
                "id": i.id, "name": i.name, "rows": i.rows, "cols": i.cols,
            }
            gridData_list = []
            for j in CabinetGrid.objects.filter(cabinet=i).values('row').distinct().order_by():#多字段干扰​：使用 .values('row') 时，如果查询包含其他字段（如通过 order_by 或模型默认排序），distinct() 可能无效。数据库会对所有字段组合去重，而不仅是 row。
                # print(j['row'])
                rowdata = []
                for k in CabinetGrid.objects.filter(cabinet=i, row=j['row']).values('col'):
                    celldata = CabinetGrid.objects.filter(cabinet=i, row=j['row'], col=k['col']).first()
                    coldic = {
                        'id': celldata.id,
                        "cabinet": i.id, "rowIndex": celldata.row, "colIndex": celldata.col,
                        "status": celldata.status,
                        "statusText": celldata.get_status_display(),
                        "position": celldata.position, "user": celldata.user, "phone": celldata.phone,
                        "Customer": celldata.Customer, "ProCode": celldata.ProCode,  "CampalCode": celldata.CampalCode,
                        "borrowDate": str(celldata.Brow_at) if celldata.Brow_at else '', "BrowReson": celldata.BrowReson,
                        "takeoutDate": str(celldata.Take_at) if celldata.Take_at else '', "TakeReson": celldata.TakeReson,
                         "reserveDate": str(celldata.Back_at) if celldata.Back_at else '',
                               "notes": celldata.notes
                    }
                    rowdata.append(coldic)
                gridData_list.append(rowdata)
            cabinets_dic["gridData"] = gridData_list
            cabinets_datas.append(cabinets_dic)

        data = {
            "cabinets": cabinets_datas,
            "isAdmin": isAdmin,
            "currentUser": currentUser,
            "CustomerOptions": CustomerOptions,
            "errMsg": errMsg,
        }
        print(data["cabinets"])
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render(request, 'CabinetManage/CabinetManage.html', locals())




