from django.db import models

class TestDeviceLNV(models.Model):
    Category = models.CharField(max_length=50, verbose_name='Category')
    Class = models.CharField(max_length=256, null=True, blank=True, verbose_name='Class')
    Type = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Type')
    Covered_range_for_case = models.CharField(max_length=5000, null=True, blank=True, verbose_name='Covered range for case')
    Require_State = models.CharField(max_length=256, null=True, blank=True, verbose_name='Require State')
    Comments = models.CharField(max_length=5000, null=True, blank=True, verbose_name='Comments')
    Remark = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Remark')
    ODM_status = models.CharField(max_length=64, null=True, blank=True, verbose_name='ODM status')
    Purchase_Plan = models.CharField(max_length=128, null=True, blank=True, verbose_name='Purchase Plan')
    Device_Price = models.FloatField(max_length=64, null=True, blank=True, verbose_name='Device Price')
    Device1 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #1')
    Device2 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #2')
    Device3 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #3')
    Device4 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #4')
    Device5 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #5')
    Device6 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #6')
    Device7 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #7')
    Device8 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #8')
    Device9 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #9')
    Device10 = models.CharField(max_length=64, null=True, blank=True, verbose_name='Device #10')
    class Meta:
        verbose_name = 'TestDeviceLNV'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return '{Category}>>{Class}'.format(Category=self.Category, Class=self.Class)