from django.db import models

class PICS(models.Model):
    # id = models.AutoField(max_length=10, primary_key=True, verbose_name='id')
    pic = models.ImageField(upload_to='DeviceLNV/PIC/',verbose_name='图片地址')
    single = models.CharField(max_length=200,null=True, blank=True,verbose_name='图片名称')
    def __unicode__(self):  # __str__ on Python 3
        return (self.id,self.pic)

    # def __str__(self):
    #     return str(self.single)
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
@receiver(pre_delete, sender=PICS)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.pic.delete(False)

# Create your models here.
class DeclarationNofile(models.Model):
    # id = models.AutoField(max_length=10, primary_key=True, verbose_name='id')
    files = models.ImageField(upload_to='DeviceLNV/DeclarationNo/',verbose_name='文件内容')
    single = models.CharField(max_length=200,null=True, blank=True,verbose_name='文件名称')
    def __unicode__(self):  # __str__ on Python 3
        return (self.id,self.files)

    # def __str__(self):
    #     return str(self.single)
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
@receiver(pre_delete, sender=DeclarationNofile)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.files.delete(False)

class DeviceLNV(models.Model):
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
        ('驗收中', '驗收中'),
        ('已借出', '已借出'),
        ('可借用', '可借用'),
        ('固定設備', '固定設備'),
        # ('長期借用', '長期借用'),
        ('預定確認中', '預定確認中'),
        ('歸還確認中', '歸還確認中'),
        ('續借確認中', '續借確認中'),
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
    Customer = models.CharField(max_length=24, choices=Customer_list, verbose_name='客戶別')
    Plant = models.CharField(max_length=108, choices=Plant_list, verbose_name='廠區')
    NID = models.CharField(max_length=16, unique=True, verbose_name='設備序號')
    DevID = models.CharField(max_length=128, null=True, blank=True, verbose_name='設備用途')
    Photo = models.ManyToManyField(PICS, related_name='pics', blank=True, verbose_name='图片表')
    IntfCtgry = models.CharField(max_length=64, verbose_name='介面種類')
    DevCtgry = models.CharField(max_length=512, verbose_name='設備種類')
    Devproperties = models.CharField(max_length=256, verbose_name='設備屬性')
    DevVendor = models.CharField(max_length=128,  verbose_name='設備廠家')
    Devsize = models.CharField(max_length=128,  null=True, blank=True, verbose_name='設備容量')
    DevModel = models.CharField(max_length=128, verbose_name='設備型號')
    DevName = models.CharField(max_length=1024, verbose_name='設備名稱')

    HWVer = models.CharField(max_length=1000, null=True, blank=True, verbose_name='HW Ver.')
    FWVer = models.CharField(max_length=1000, null=True, blank=True, verbose_name='FW Ver.')
    DevDescription = models.CharField(max_length=1024, null=True, blank=True, verbose_name='設備描述')
    PckgIncludes = models.CharField(max_length=512, null=True, blank=True, verbose_name='附帶品')
    expirdate = models.CharField(max_length=108, choices=expirdate_choice, null=True, blank=True, verbose_name='保固期')
    DevPrice = models.CharField(max_length=16, null=True, blank=True, verbose_name='價值 RMB(單價)')
    Source = models.CharField(max_length=64, null=True, blank=True, verbose_name='設備來源')
    Pchsdate = models.DateField(max_length=64, null=True, blank=True, verbose_name='購買時間')
    PN = models.CharField(max_length=64, null=True, blank=True, verbose_name='料號')
    LSTA = models.CharField(max_length=256, choices=LSTA_choice, null=True, blank=True, verbose_name='LNV SW Test lab device Audit list: Require state(Must, Optional)')
    ApplicationNo = models.CharField(max_length=64, null=True, blank=True, verbose_name='申購單號')
    DeclarationNo = models.CharField(max_length=64, null=True, blank=True, verbose_name='報關單號')
    Declaration = models.ManyToManyField(DeclarationNofile, related_name='filesDe', blank=True, verbose_name='報關單')
    AssetNum = models.CharField(max_length=64, null=True, blank=True, verbose_name='資產編號')

    addnewname = models.CharField(max_length=64, null=True, blank=True, verbose_name='設備添加人員')
    addnewdate = models.DateField(max_length=64, null=True, blank=True, verbose_name='設備添加日期')
    Comment = models.CharField(max_length=1000, null=True, blank=True, verbose_name='備註')
    uscyc = models.CharField(max_length=64, null=True, blank=True, verbose_name='使用次數')
    UsrTimes = models.CharField(max_length=64, null=True, blank=True, verbose_name='借還次數')
    DevStatus = models.CharField(max_length=64, choices=Dev_Status_choice, null=True, blank=True, verbose_name='設備狀態')
    BrwStatus = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='借還狀態')
    Usrname = models.CharField(max_length=64, null=True, blank=True, verbose_name='用戶名稱')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='借還人員工號')
    ProjectCode = models.CharField(max_length=16, null=True, blank=True, verbose_name='機種')
    Phase = models.CharField(max_length=16, null=True, blank=True, verbose_name='Phase')
    useday = models.CharField(max_length=16, null=True, blank=True, verbose_name='使用天數')
    Plandate = models.DateField(max_length=64, null=True, blank=True, verbose_name='預計歸還日期')
    Btime = models.DateField(max_length=64, null=True, blank=True, verbose_name='借用時間')
    Rtime = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')
    EOL = models.DateField(max_length=64, null=True, blank=True, verbose_name='EOL日期')
    Last_BR_per = models.CharField(max_length=64, null=True, blank=True, verbose_name='最近一次借還人員')
    Last_BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='最近一次借還人員工號')
    Last_ProjectCode = models.CharField(max_length=16, null=True, blank=True, verbose_name='最近一次借機種')
    Last_Phase = models.CharField(max_length=16, null=True, blank=True, verbose_name='最近一次借Phase')
    Last_Predict_return = models.DateField(max_length=64, null=True, blank=True, verbose_name='最近一次預計歸還日期')
    Last_Borrow_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='最近一次借用日期')
    Last_Return_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='最近一次歸還日期')
    Last_uscyc = models.CharField(max_length=64, null=True, blank=True, verbose_name='上次借用期間使用次數')
    class Meta:
        verbose_name = 'Device_LNV'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{NID}>>{DevID}'.format(NID=self.NID, DevID=self.DevID)

class DeviceLNVHis(models.Model):
    Result_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    )
    NID = models.CharField(max_length=16, verbose_name='設備序號')
    DevID = models.CharField(max_length=128, null=True, blank=True, verbose_name='設備編號')
    DevModel = models.CharField(max_length=128, verbose_name='設備型號')
    DevName = models.CharField(max_length=1024, verbose_name='設備名稱')
    uscyc = models.CharField(max_length=64, null=True, blank=True, verbose_name='使用次數')
    Btime = models.DateField(max_length=64, null=True, blank=True, verbose_name='借用時間')
    Plandate = models.DateField(max_length=64, null=True, blank=True, verbose_name='預計歸還日期')
    Rtime = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')
    Usrname = models.CharField(max_length=64, null=True, blank=True, verbose_name='用戶名稱')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='借還人員工號')
    ProjectCode = models.CharField(max_length=16, null=True, blank=True, verbose_name='機種')
    Phase = models.CharField(max_length=16, null=True, blank=True, verbose_name='Phase')
    Result = models.CharField(max_length=16, choices=Result_choice,  null=True, blank=True, verbose_name='Result')
    Devstatus = models.CharField(max_length=16, null=True, blank=True, verbose_name='Devstatus')
    Comments = models.CharField(max_length=2000, null=True, blank=True, verbose_name='Comments')
    class Meta:
        verbose_name = '设备借还记录'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{NID}>>{BR_per_code}'.format(NID=self.NID, BR_per_code=self.BR_per_code)
class DeviceIntfCtgryList(models.Model):
    IntfCtgry = models.CharField(max_length=64, verbose_name='介面種類')
    # DevCtgry = models.CharField(max_length=512, verbose_name='設備種類')
    # Devproperties = models.CharField(max_length=256, verbose_name='設備屬性')
    # DevVendor = models.CharField(max_length=128, verbose_name='設備廠家')
    # Devsize = models.CharField(max_length=128, null=True, blank=True, verbose_name='設備容量')
    class Meta:
        verbose_name = '介面種類'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.IntfCtgry

class DeviceDevCtgryList(models.Model):
    DevCtgry = models.CharField(max_length=512, verbose_name='設備種類')
    IntfCtgry_P = models.ForeignKey("DeviceIntfCtgryList", on_delete=True)
    class Meta:
        verbose_name = '設備種類'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示带菜单前缀的权限
        return '{IntfCtgry_P}>>{DevCtgry}'.format(IntfCtgry_P=self.IntfCtgry_P, DevCtgry=self.DevCtgry)

class DeviceDevpropertiesList(models.Model):
    Devproperties = models.CharField(max_length=256, verbose_name='設備屬性')
    DevCtgry_P = models.ForeignKey("DeviceDevCtgryList", on_delete=True)
    class Meta:
        verbose_name = '設備屬性'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示带菜单前缀的权限
        return '{DevCtgry_P}>>{Devproperties}'.format(DevCtgry_P=self.DevCtgry_P, Devproperties=self.Devproperties)

class DeviceDevVendorList(models.Model):
    DevVendor = models.CharField(max_length=128, verbose_name='設備廠家')
    Devproperties_P = models.ForeignKey("DeviceDevpropertiesList", on_delete=True)
    class Meta:
        verbose_name = '設備廠家'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示带菜单前缀的权限
        return '{Devproperties_P}>>{DevVendor}'.format(Devproperties_P=self.Devproperties_P, DevVendor=self.DevVendor)

class DeviceDevsizeList(models.Model):
    Devsize = models.CharField(max_length=128, null=True, blank=True, verbose_name='設備容量')
    DevVendor_P = models.ForeignKey("DeviceDevVendorList", on_delete=True)
    class Meta:
        verbose_name = '設備容量'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示带菜单前缀的权限
        return '{DevVendor_P}>>{Devsize}'.format(DevVendor_P=self.DevVendor_P, Devsize=self.Devsize)