from django.db import models

class ChairCabinetLNV(models.Model):
    Customer_list = (
        ('', ''),
        ('C38(NB)', 'C38(NB)'),
        ('C38(AIO)', 'C38(AIO)'),
        ('T88(AIO)', 'T88(AIO)'),
        ('A39', 'A39'),
    )
    Plant_list = (
        ('', ''),
        ('KS', 'KS'),
        ('CQ', 'CQ'),
    )
    BR_Status_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        # ('驗收中', '驗收中'),
        ('使用中', '使用中'),
        # ('歸還中', '歸還中'),
        # ('轉帳中', '轉帳中'),

        ('閑置中', '閑置中'),
        ('已損壞', '已損壞'),
        ('維修中', '維修中'),

        ('申請確認中', '申請確認中'),
        ('轉帳確認中', '轉帳確認中'),

        ('申請核准中', '申請核准中'),
        ('接收確認中', '接收確認中'),
        # ('歸還確認中', '歸還確認中'),

        # ('申請核准中', '申請核准中'),
        # ('接收核准中', '接收核准中'),

    )
    Dev_Status_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('Good', 'Good'),
        ('Fixed', 'Fixed'),
        ('Long', 'Long'),
        ('Damaged', 'Damaged'),
        ('Lost', 'Lost'),
    )
    expirdate_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('一年', '一年'),
        ('二年', '二年'),
        ('三年', '三年'),
        ('四年', '四年'),
        ('五年', '五年'),
    )
    LSTA_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('Must', 'Must'),
        ('Optional', 'Optional'),
        ('Similar', 'Similar'),
    )
    Idle_Status_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('待轉賬', '待轉賬'),
        ('待退庫', '待退庫'),
    )

    # Customer = models.CharField(max_length=24, choices=Customer_list, verbose_name='客戶別')
    # Plant = models.CharField(max_length=108, choices=Plant_list, verbose_name='廠區')
    NID = models.CharField(max_length=16, unique=True, verbose_name='統一編號')
    Category = models.CharField(max_length=64, verbose_name='產品類別')
    Area = models.CharField(max_length=64, verbose_name='位置')
    linshi_Area = models.CharField(max_length=64, null=True, blank=True, verbose_name='位置')
    Purpose = models.CharField(max_length=256, null=True, blank=True, verbose_name='臨時用途')
    linshi_Purpose = models.CharField(max_length=256, null=True, blank=True, verbose_name='臨時用途')

    # DevStatus = models.CharField(max_length=64, choices=Dev_Status_choice, null=True, blank=True, verbose_name='設備狀態')
    BrwStatus = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='使用狀態')
    linshi_BrwStatus = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='臨時使用狀態')
    OAP = models.CharField(max_length=64, null=True, blank=True, verbose_name='保管人')
    OAPcode = models.CharField(max_length=64, null=True, blank=True, verbose_name='保管人工號')
    Usrname = models.CharField(max_length=64, null=True, blank=True, verbose_name='使用人')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='使用人工號')
    Btime = models.DateField(max_length=64, null=True, blank=True, verbose_name='領用日期')
    Rtime = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')


    Last_OAP = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一任保管人姓名')
    Last_OAPcode = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一任保管人工號')
    Last_Borrow_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='上一次領用日期')
    Last_Return_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='上一次歸還日期')
    Last_BR_per = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一任使用人')
    Last_BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一任使用人工號')
    Last_BrwStatus = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='上一任使用狀態')

    Transefer_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='轉賬人員工號')
    Receive_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='接收人員工號')
    Sign_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='簽核人員工號')

    class Meta:
        verbose_name = 'ChairCabinetLNV'  # 不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{NID}>{Usrname}>{Category}>{Area}'.format(NID=self.NID, Usrname=self.Usrname, Category=self.Category, Area=self.Area)

class ChairCabinetLNVHis(models.Model):
    Result_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    )
    NID = models.CharField(max_length=16, verbose_name='統一編號')
    Category = models.CharField(max_length=64, verbose_name='產品類別')
    Area = models.CharField(max_length=64, verbose_name='位置')
    Purpose = models.CharField(max_length=256, null=True, blank=True, verbose_name='用途')
    OAP = models.CharField(max_length=64, null=True, blank=True, verbose_name='保管人')
    OAPcode = models.CharField(max_length=64, null=True, blank=True, verbose_name='保管人工號')
    BrwStatus = models.CharField(max_length=64,  null=True, blank=True, verbose_name='使用狀態')
    Btime = models.DateField(max_length=64, null=True, blank=True, verbose_name='領用日期')
    Rtime = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')
    Changetime = models.DateField(max_length=64, null=True, blank=True, verbose_name='变更使用人日期')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='使用人工號')
    Usrname = models.CharField(max_length=64, null=True, blank=True, verbose_name='使用人')
    Transefer_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='轉賬人員工號')
    Receive_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='接收人員工號')
    Comments = models.CharField(max_length=2000, null=True, blank=True, verbose_name='Comments')
    class Meta:
        verbose_name = '柜椅借还记录'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{NID}>{OAP}>{OAPcode}'.format(NID=self.NID, OAP=self.OAP, OAPcode=self.OAPcode)