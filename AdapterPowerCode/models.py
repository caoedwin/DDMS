from django.db import models

# Create your models here.
class PICS(models.Model):
    # id = models.AutoField(max_length=10, primary_key=True, verbose_name='id')
    pic = models.ImageField(upload_to='Adapter/PIC/',verbose_name='图片地址')
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

class AdapterPowerCodeBR(models.Model):
    BR_Status_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('已借出', '已借出'),
        ('可借用', '可借用'),
        # ('固定設備', '固定設備'),
        ('預定確認', '預定確認'),
        ('歸還確認', '歸還確認'),
        ('續借確認', '續借確認'),
        ('Close', 'Close'),
    )
    Pinming_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('PowerCode', 'PowerCode'),
        ('Adapter', 'Adapter'),
    )
    Leibie_choice = (
        # ('Select Customer', 'Select Customer'),
        # ('', ''),
        ('一類', '一類'),
        ('二類', '二類'),
    )
    Changjia = models.CharField(max_length=108, verbose_name='廠家')
    MaterialPN = models.CharField(max_length=108, verbose_name='MaterialPN')
    Description = models.CharField(max_length=1000, verbose_name='Description')
    Power = models.CharField(max_length=64, verbose_name='功率')
    Number = models.CharField(max_length=64, unique=True, verbose_name='編號')
    Model = models.CharField(max_length=256, null=True, blank=True, verbose_name='Model')
    Pinming = models.CharField(max_length=64, choices=Pinming_choice,  null=True, blank=True, verbose_name='品名')
    Leibie = models.CharField(max_length=64, choices=Leibie_choice,  null=True, blank=True, verbose_name='類別')
    Location = models.CharField(max_length=64, verbose_name='Location')
    Customer = models.CharField(max_length=64, verbose_name='客戶別')
    OAP = models.CharField(max_length=16, null=True, blank=True, verbose_name='掛賬人')
    OAPcode = models.CharField(max_length=16, null=True, blank=True, verbose_name='掛賬人工號')

    Project_Code = models.CharField(max_length=16, verbose_name='ProjectCode')
    Phase = models.CharField(max_length=16, verbose_name='Phase')
    Device_Status = models.CharField(max_length=64, null=True, blank=True, verbose_name='設備狀態')
    BR_Status = models.CharField(max_length=64, choices=BR_Status_choice, null=True, blank=True, verbose_name='借還狀態')
    BR_per = models.CharField(max_length=64, null=True, blank=True, verbose_name='借還人員')
    BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='借還人員工號')
    Predict_return = models.DateField(max_length=64, null=True, blank=True, verbose_name='預計歸還日期')
    Borrow_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='借用日期')
    Return_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='歸還日期')
    Last_BR_per = models.CharField(max_length=64, null=True, blank=True, verbose_name='最近一次借還人員')
    Last_BR_per_code = models.CharField(max_length=64, null=True, blank=True, verbose_name='最近一次借還人員工號')
    Last_Predict_return = models.DateField(max_length=64, null=True, blank=True, verbose_name='最近一次預計歸還日期')
    Last_Borrow_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='最近一次借用日期')
    Last_Return_date = models.DateField(max_length=64, null=True, blank=True, verbose_name='最近一次歸還日期')
    Photo = models.ManyToManyField(PICS, related_name='pics', blank=True, verbose_name='图片表')