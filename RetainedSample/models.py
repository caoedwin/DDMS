from django.db import models
from django.utils import timezone
from app01.models import UserInfo

User = UserInfo()

class RetainedSample(models.Model):
    """留样样品"""
    Position_CHOICES = (
        ('Plant5-#23', 'Plant5-#23'),
    )
    Project = models.CharField(max_length=40, verbose_name="專案名稱")
    Owner = models.CharField(max_length=30, verbose_name="專案負責人")#工號
    SampleName = models.CharField(max_length=200, verbose_name="樣品名稱")
    Manufacturer = models.CharField(max_length=200, verbose_name="樣品廠商")
    SampleBatch = models.CharField(max_length=500, verbose_name="樣品批次/版本號")

    SampleQuantity = models.IntegerField(verbose_name="樣品數量")
    Retainer = models.CharField(max_length=30, verbose_name="留樣人")  # 工號
    RetainStart = models.DateField(verbose_name="留樣日期")
    RetainPeriod = models.FloatField(verbose_name="留樣周期(年)")
    RetainPosition = models.CharField(choices=Position_CHOICES, max_length=300, verbose_name="留樣位置")
    BorrowedQuantity = models.IntegerField(verbose_name="已借出數量")
    RemainedQuantity = models.IntegerField(verbose_name="剩餘留樣數量")
    UnderApprovalQuantity = models.IntegerField(verbose_name="簽核中數量")

    ReturnRequestedAt = models.DateTimeField(null=True, blank=True, verbose_name="归还申请时间")
    ReturnRequestedQuantity = models.IntegerField(default=0, verbose_name="申请归还数量")
    ReturnReason = models.CharField(max_length=500, blank=True, verbose_name="归还原因")
    ReturnedAt = models.DateTimeField(null=True, blank=True, verbose_name="实际归还时间")
    ReturnedQuantity = models.IntegerField(default=0, verbose_name="已归还数量")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")


class PersonalRetainedSample(models.Model):
    """個人留样信息"""
    Sample = models.ForeignKey("RetainedSample", default='', on_delete=models.CASCADE, verbose_name="留样样品")
    Borrower = models.CharField(max_length=30, verbose_name="借用人")  # 工號
    Status = models.CharField(max_length=30, verbose_name="借還狀態")  # 借用確認中，已借用，歸還確認中，已歸還

    BorrowQuantity = models.IntegerField(verbose_name="借用數量")
    BorrowedReson = models.CharField(max_length=1000, blank=True, verbose_name="借用用途")

    RemainedQuantity = models.IntegerField(default=0, verbose_name="剩余借用数量")
    ReturnRequestedAt = models.DateTimeField(null=True, blank=True, verbose_name="归还申请时间")
    ReturnRequestedQuantity = models.IntegerField(default=0, verbose_name="申请归还数量")
    ReturnReason = models.CharField(max_length=500, blank=True, verbose_name="归还原因")
    ReturnedAt = models.DateTimeField(null=True, blank=True, verbose_name="实际归还时间")
    ReturnedQuantity = models.IntegerField(default=0, verbose_name="已归还数量")
    ApprovedAt = models.DateTimeField(null=True, blank=True, verbose_name="批准时间")
    ApprovedBy = models.CharField(max_length=100, blank=True, verbose_name="批准人")
    RejectedAt = models.DateTimeField(null=True, blank=True, verbose_name="拒绝时间")
    RejectedBy = models.CharField(max_length=100, blank=True, verbose_name="拒绝人")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

class RetainedSampleRecord(models.Model):
    """個人留样信息"""
    Sample = models.ForeignKey("RetainedSample", default='', on_delete=models.CASCADE, verbose_name="留样样品")
    RecordType = models.CharField(max_length=30, blank=True ,verbose_name="記錄類型")  # 借還，報廢
    Borrowed = models.CharField(max_length=30, verbose_name="借用人")  # 工號
    BorrowQuantity = models.IntegerField(verbose_name="借用數量")
    BorrowedReson = models.CharField(max_length=1000, blank=True, verbose_name="借用用途")
    BorrowedStatus = models.CharField(max_length=30, verbose_name="借用狀態")  # 已借用
    ReturnedStatus = models.CharField(max_length=30, verbose_name="借用狀態")  # 已歸還，未歸還

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")