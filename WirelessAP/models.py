from django.db import models

# Create your models here.
class WirelessAP(models.Model):

    Room = models.CharField(max_length=30, verbose_name='Room No.')
    Owner_Num = models.CharField(max_length=30, verbose_name='AP Owner工號')
    Owner_EN = models.CharField(max_length=30, verbose_name='AP Owner')
    Category = models.CharField(max_length=64, verbose_name='Category')
    Net_Area = models.CharField(max_length=512, verbose_name='外網網點')
    AP_Model = models.CharField(max_length=256, verbose_name='AP廠商型號')
    AP_SSID = models.CharField(max_length=128,  verbose_name='AP SSID')
    Channel_24G = models.CharField(max_length=28,  null=True, blank=True, verbose_name='2.4GHz Channel')
    Channel_5G = models.CharField(max_length=28,  null=True, blank=True, verbose_name='5GHz Channel')
    Channel_6G = models.CharField(max_length=28,  null=True, blank=True, verbose_name='6GHz Channel')
    AP_Psw = models.CharField(max_length=128, verbose_name='AP Password')
    AP_IP = models.CharField(max_length=128, verbose_name='IP')

    Brw_Owner_Num = models.CharField(max_length=26, null=True, blank=True, verbose_name='借用人工號')
    Brw_Owner_CN = models.CharField(max_length=26, null=True, blank=True, verbose_name='借用人')
    Start_Time = models.DateTimeField(max_length=64, null=True, blank=True, verbose_name='借用時間(Start)')
    End_Time = models.DateTimeField(max_length=64, null=True, blank=True, verbose_name='借用時間(End)')
    Project = models.CharField(max_length=50, null=True, blank=True, verbose_name='Project(Compal name)')
    Case = models.CharField(max_length=256, null=True, blank=True, verbose_name='Test Case')
    Comments = models.CharField(max_length=1024, null=True, blank=True, verbose_name='Comments')
    class Meta:
        verbose_name = 'WirelessAP'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{Room}>>{AP_SSID}>>{AP_IP}'.format(Room=self.Room, AP_SSID=self.AP_SSID, AP_IP=self.AP_IP)