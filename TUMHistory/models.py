from django.db import models

# Create your models here.
class Unitbudget(models.Model):
    Customer_list = (
        ('', ''),
        ('C38(NB)', 'C38(NB)'),
        ('C38(AIO)', 'C38(AIO)'),
        ('C85', 'C85'),
        ('T88(AIO)', 'T88(AIO)'),
        ('A39', 'A39'),
    )
    Category_list = (
        ('', ''),
        ('領用', '領用'),
        ('退還', '退還'),
    )
    Customer = models.CharField(max_length=30, choices=Customer_list, verbose_name='Customer')
    Year = models.CharField(max_length=30, verbose_name='年份')
    Category = models.CharField(max_length=30, choices=Category_list, default='', verbose_name='Category')
    Jan = models.IntegerField("Jan", null=True, blank=True)
    Feb = models.IntegerField("Feb", null=True, blank=True)
    Mar = models.IntegerField("Mar", null=True, blank=True)
    Apr = models.IntegerField("Apr", null=True, blank=True)
    May = models.IntegerField("May", null=True, blank=True)
    Jun = models.IntegerField("Jun", null=True, blank=True)
    Jul = models.IntegerField("Jul", null=True, blank=True)
    Aug = models.IntegerField("Aug", null=True, blank=True)
    Sep = models.IntegerField("Sep", null=True, blank=True)
    Oct = models.IntegerField("Oct", null=True, blank=True)
    Nov = models.IntegerField("Nov", null=True, blank=True)
    Dec = models.IntegerField("Dec", null=True, blank=True)


class UnitInDQA_Tum(models.Model):
    ItemID = models.CharField(max_length=30, verbose_name='ItemID')
    SiteName = models.CharField(max_length=30, verbose_name='SiteName')
    FunctionName = models.CharField(max_length=30, verbose_name='FunctionName')
    CustomerCode = models.CharField(max_length=30, verbose_name='CustomerCode')
    SN = models.CharField(max_length=60, verbose_name='SN')
    PN = models.CharField(max_length=60, verbose_name='PN')
    CurrentKeeper = models.CharField(max_length=60, verbose_name='CurrentKeeper')
    CurrentKeeper_CN = models.CharField(max_length=60, verbose_name='當前掛賬人')
    ApplyReasonCategory = models.CharField(max_length=60, null=True, blank=True, verbose_name='ApplyReasonCategory')
    ApplyReason = models.CharField(max_length=1024, null=True, blank=True, verbose_name='領用原因')
    InData = models.DateField(max_length=60, null=True, blank=True, verbose_name='入賬日期')
    ReturnOffline = models.DateField(max_length=60, null=True, blank=True, verbose_name='歸還期限')
    ReturnData = models.DateTimeField(max_length=60, null=True, blank=True, verbose_name='退庫日期')
    Status = models.CharField(max_length=60, null=True, blank=True, verbose_name='當前狀態')
    DeptNo = models.CharField(max_length=60, null=True, blank=True, verbose_name='DeptNo')
    TUMsystemCode = models.CharField(max_length=60, null=True, blank=True, verbose_name='系統編碼')
    CostCenter = models.CharField(max_length=60, null=True, blank=True, verbose_name='CostCenter')
    ProjectCode = models.CharField(max_length=60, null=True, blank=True, verbose_name='ProjectCode')
    Description = models.CharField(max_length=512, null=True, blank=True, verbose_name='Description')
    QTY = models.IntegerField(null=True, blank=True, verbose_name='QTY')
    Phase = models.CharField(max_length=20, null=True, blank=True, verbose_name='機種階段')
    EOPDate = models.DateField(max_length=20, null=True, blank=True, verbose_name='EOP日期')
    class Meta:
        verbose_name = 'UnitInDQA_Tum'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{ItemID}>>{SN}>>{PN}'.format(ItemID=self.ItemID, SN=self.SN, PN=self.PN)

class DQAUnit_TUMHistory(models.Model):
    ItemID = models.CharField(max_length=30, verbose_name='ItemID')
    SiteName = models.CharField(max_length=30, verbose_name='SiteName')
    FunctionName = models.CharField(max_length=30, verbose_name='FunctionName')
    CustomerCode = models.CharField(max_length=30, verbose_name='CustomerCode')
    SN = models.CharField(max_length=60, verbose_name='SN')
    PN = models.CharField(max_length=60, verbose_name='PN')
    CurrentKeeper = models.CharField(max_length=60, verbose_name='CurrentKeeper')
    CurrentKeeper_CN = models.CharField(max_length=60, verbose_name='當前掛賬人')
    ApplyReasonCategory = models.CharField(max_length=60, null=True, blank=True, verbose_name='ApplyReasonCategory')
    ApplyReason = models.CharField(max_length=1024, null=True, blank=True, verbose_name='領用原因')
    InData = models.DateField(max_length=60, null=True, blank=True, verbose_name='入賬日期')
    ReturnOffline = models.DateField(max_length=60, null=True, blank=True, verbose_name='歸還期限')
    ReturnData = models.DateTimeField(max_length=60, null=True, blank=True, verbose_name='退庫日期')
    Status = models.CharField(max_length=60, null=True, blank=True, verbose_name='當前狀態')
    DeptNo = models.CharField(max_length=60, null=True, blank=True, verbose_name='DeptNo')
    TUMsystemCode = models.CharField(max_length=60, null=True, blank=True, verbose_name='系統編碼')
    CostCenter = models.CharField(max_length=60, null=True, blank=True, verbose_name='CostCenter')
    ProjectCode = models.CharField(max_length=60, null=True, blank=True, verbose_name='ProjectCode')
    Description = models.CharField(max_length=512, null=True, blank=True, verbose_name='Description')
    QTY = models.IntegerField(null=True, blank=True, verbose_name='QTY')
    Phase = models.CharField(max_length=20, null=True, blank=True, verbose_name='機種階段')
    EOPDate = models.DateField(max_length=20, null=True, blank=True, verbose_name='EOP日期')
    class Meta:
        verbose_name = 'DQAUnit_TUMHistory'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
        # indexes = [models.Index(fields=["address", "english_name"])]  # 普通索引
        # 联合约束   其中goods和user不能重复
        # unique_together = ["ItemID", "SN", "PN"]
        # 联合索引
        # index_together = ["ItemID", "SN", "PN"]
        # unique_together = ["goods", "user"]  表示联合约束，其中"goods"和"user"表示不能重复，不能一样。
        # index_together = ["user", "goods"] 表示联合索引，其中"goods"和"user"联合同步查询，提高效率。
        # indexes = [
        #     models.Index(fields=["ItemID", "SN", "PN"], name='index_ItemID_SNPN')
        # ]
    def __str__(self):
        return '{ItemID}>>{SN}>>{PN}'.format(ItemID=self.ItemID, SN=self.SN, PN=self.PN)


class MateriaInDQA_Tum(models.Model):
    SiteName = models.CharField(max_length=30, verbose_name='SiteName')
    FunctionName = models.CharField(max_length=30, verbose_name='FunctionName')
    CustomerCode = models.CharField(max_length=30, verbose_name='CustomerCode')
    PN = models.CharField(max_length=60, verbose_name='PN')
    CurrentKeeper = models.CharField(max_length=60, verbose_name='CurrentKeeper')
    CurrentKeeper_CN = models.CharField(max_length=60, verbose_name='當前掛賬人')
    ApplyReasonCategory = models.CharField(max_length=60, null=True, blank=True, verbose_name='ApplyReasonCategory')
    ApplyReason = models.CharField(max_length=1024, null=True, blank=True, verbose_name='領用原因')
    InData = models.DateField(max_length=60, null=True, blank=True, verbose_name='入賬日期')
    ReturnOffline = models.DateField(max_length=60, null=True, blank=True, verbose_name='歸還期限')
    ReturnData = models.DateTimeField(max_length=60, null=True, blank=True, verbose_name='退庫日期')
    Status = models.CharField(max_length=60, null=True, blank=True, verbose_name='當前狀態')
    DeptNo = models.CharField(max_length=60, null=True, blank=True, verbose_name='DeptNo')
    ItemNo = models.CharField(max_length=60, null=True, blank=True, verbose_name='ItemNo')
    CostCenter = models.CharField(max_length=60, null=True, blank=True, verbose_name='CostCenter')
    ProjectCode = models.CharField(max_length=60, null=True, blank=True, verbose_name='ProjectCode')
    Description = models.CharField(max_length=512, null=True, blank=True, verbose_name='Description')
    QTY = models.IntegerField(null=True, blank=True, verbose_name='QTY')
    PhaseName = models.CharField(max_length=20, null=True, blank=True, verbose_name='PhaseName')
    EOPDate = models.DateField(max_length=20, null=True, blank=True, verbose_name='EOP日期')
    class Meta:
        verbose_name = 'MateriaInDQA_Tum'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{CurrentKeeper}>>{PN}'.format(CurrentKeeper=self.CurrentKeeper, PN=self.PN)

class DQAMateria_TUMHistory(models.Model):
    ReturnID = models.CharField(max_length=30, verbose_name='ReturnID')
    SiteName = models.CharField(max_length=30, verbose_name='SiteName')
    FunctionName = models.CharField(max_length=30, verbose_name='FunctionName')
    CustomerCode = models.CharField(max_length=30, verbose_name='CustomerCode')
    PN = models.CharField(max_length=60, verbose_name='PN')
    CurrentKeeper = models.CharField(max_length=60, verbose_name='CurrentKeeper')
    CurrentKeeper_CN = models.CharField(max_length=60, verbose_name='當前掛賬人')
    ApplyReasonCategory = models.CharField(max_length=60, null=True, blank=True, verbose_name='ApplyReasonCategory')
    ApplyReason = models.CharField(max_length=1024, null=True, blank=True, verbose_name='領用原因')
    InData = models.DateField(max_length=60, null=True, blank=True, verbose_name='入賬日期')
    ReturnOffline = models.DateField(max_length=60, null=True, blank=True, verbose_name='歸還期限')
    ReturnData = models.DateTimeField(max_length=60, null=True, blank=True, verbose_name='退庫日期')
    Status = models.CharField(max_length=60, null=True, blank=True, verbose_name='當前狀態')
    DeptNo = models.CharField(max_length=60, null=True, blank=True, verbose_name='DeptNo')
    ItemNo = models.CharField(max_length=60, null=True, blank=True, verbose_name='ItemNo')
    CostCenter = models.CharField(max_length=60, null=True, blank=True, verbose_name='CostCenter')
    ProjectCode = models.CharField(max_length=60, null=True, blank=True, verbose_name='ProjectCode')
    Description = models.CharField(max_length=512, null=True, blank=True, verbose_name='Description')
    QTY = models.IntegerField(null=True, blank=True, verbose_name='QTY')
    PhaseName = models.CharField(max_length=20, null=True, blank=True, verbose_name='PhaseName')
    EOPDate = models.DateField(max_length=20, null=True, blank=True, verbose_name='EOP日期')
    class Meta:
        verbose_name = 'DQAMateria_TUMHistory'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{CurrentKeeper}>>{ReturnID}>>{PN}'.format(CurrentKeeper=self.CurrentKeeper, ReturnID=self.ReturnID, PN=self.PN)