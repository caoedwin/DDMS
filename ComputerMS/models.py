from django.db import models

class ComputerLNV(models.Model):
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
        # ('申請中', '申請中'),
        # ('歸還中', '歸還中'),
        # ('轉帳中', '轉帳中'),

        ('閑置中', '閑置中'),# 此闲置中是指的EFORM里面主管挂账的闲置中，而不是可借用状态，如果要加可借用的动作，可以再加个可借用状态
        ('已報廢', '已報廢'),
        # ('長期借用', '長期借用'),
        ('申請確認中', '申請確認中'),
        ('歸還確認中', '歸還確認中'),# 相当于改成报废确认中
        ('轉帳確認中', '轉帳確認中'),
        ('接收確認中', '接收確認中'),
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
    MaterialPN = models.CharField(max_length=128, null=True, blank=True, verbose_name='MaterialPN')
    CPU = models.CharField(max_length=64, verbose_name='CPU')
    RAM = models.CharField(max_length=512, verbose_name='RAM')
    HDD = models.CharField(max_length=256, verbose_name='HDD')
    Wireless = models.CharField(max_length=8,  verbose_name='Wireless')
    LCD = models.CharField(max_length=128, verbose_name='LCD')
    OCR = models.CharField(max_length=128, verbose_name='OCR')
    Battery = models.CharField(max_length=8, verbose_name='Battery')
    Adaptor = models.CharField(max_length=8, verbose_name='Adaptor')
    Area = models.CharField(max_length=8, verbose_name='地區')
    Carryif = models.CharField(max_length=64, verbose_name='攜出廠外')
    Plant = models.CharField(max_length=8, verbose_name='廠區')
    Purpose = models.CharField(max_length=256, verbose_name='電腦用途')
    Category = models.CharField(max_length=64, verbose_name='產品類別')



    # DevStatus = models.CharField(max_length=64, choices=Dev_Status_choice, null=True, blank=True, verbose_name='設備狀態')
    BrwStatus = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='工作機狀態')
    linshi_BrwStatus = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='临时工作機狀態')
    IdleStatus = models.CharField(max_length=64, choices=Idle_Status_choice, null=True, blank=True, verbose_name='閒置狀態')
    EFormNo = models.CharField(max_length=64, verbose_name='E-Form單號')
    Usrname = models.CharField(max_length=64, null=True, blank=True, verbose_name='姓名')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='工號')
    Btime = models.DateField(max_length=64, null=True, blank=True, verbose_name='領用日期')
    Rtime = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')

    Last_BR_per = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一任使用人姓名')
    Last_BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='上一任使用人工號')
    Last_Borrow_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='上一次領用日期')
    Last_Return_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='上一次歸還日期')

    Transefer_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='轉賬人員工號')
    Receive_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='接收人員工號')
    Sign_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='簽核人員工號')
    class Meta:
        verbose_name = 'ComputerLNV'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{NID}>{Usrname}'.format(NID=self.NID, Usrname=self.Usrname)

class ComputerLNVHis(models.Model):
    Result_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    )
    NID = models.CharField(max_length=16, verbose_name='統一編號')
    EFormNo = models.CharField(max_length=64, verbose_name='E-Form單號')
    Area = models.CharField(max_length=8, null=True, blank=True, verbose_name='地區')
    Carryif = models.CharField(max_length=64, verbose_name='攜出廠外')
    Plant = models.CharField(max_length=8, null=True, blank=True, verbose_name='廠區')
    Purpose = models.CharField(max_length=256, null=True, blank=True, verbose_name='電腦用途')
    Usrname = models.CharField(max_length=64, null=True, blank=True, verbose_name='姓名')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='工號')
    Btime = models.DateField(max_length=64, null=True, blank=True, verbose_name='領用日期')
    Rtime = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')
    Transefer_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='轉賬人員工號')
    Receive_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='接收人員工號')
    Comments = models.CharField(max_length=2000, null=True, blank=True, verbose_name='Comments')
    class Meta:
        verbose_name = 'NB借还记录'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{NID}>>{BR_per_code}'.format(NID=self.NID, BR_per_code=self.BR_per_code)
