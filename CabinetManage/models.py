from django.db import models
from django.utils import timezone
from app01.models import UserInfo

User = UserInfo()


class Cabinet(models.Model):
    """柜体模型"""
    name = models.CharField(max_length=100, verbose_name="柜体名称")
    location = models.CharField(max_length=200, blank=True, verbose_name="位置")
    description = models.CharField(max_length=2000, blank=True, verbose_name="描述")
    rows = models.PositiveIntegerField(default=5, verbose_name="行数")
    cols = models.PositiveIntegerField(default=6, verbose_name="列数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "柜体"
        verbose_name_plural = "柜体"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CabinetGrid(models.Model):
    """柜格模型"""
    STATUS_CHOICES = (
        ('空闲', '空闲'),
        ('使用中', '使用中'),
        ('预定中', '预定中'),
        ('拿取保留中', '拿取保留中'),
    )
    Customer_CHOICES = (
        ('C38(NB)', 'C38(NB)'),
        ('C38(AIO)', 'C38(AIO)'),
        ('T88', 'T88'),
        ('T89', 'T89'),
    )

    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name='grids', verbose_name="所属柜体")
    row = models.PositiveIntegerField(verbose_name="行")
    col = models.PositiveIntegerField(verbose_name="列")
    position = models.CharField(max_length=10, verbose_name="位置编号", help_text="例如：A1, B2等")
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, verbose_name="状态")
    Customer = models.CharField(choices=Customer_CHOICES, max_length=20, verbose_name="客戶別")
    ProCode = models.CharField(max_length=100, blank=True, verbose_name="客戶ProCode")
    CampalCode = models.CharField(max_length=100, blank=True, verbose_name="CampalCode")
    Brow_at = models.DateTimeField(verbose_name="留樣日期")
    BrowReson = models.CharField(max_length=2000, blank=True, verbose_name="留樣原因")
    Take_at = models.DateTimeField(verbose_name="拿取日期")
    TakeReson = models.CharField(max_length=2000, blank=True, verbose_name="拿取原因")
    Back_at = models.DateTimeField(verbose_name="放回日期")
    user = models.CharField(max_length=20, blank=True, verbose_name="借用人（工号）")
    phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    notes = models.CharField(max_length=2000, blank=True, verbose_name="備注")
    creator = models.CharField(max_length=20, blank=True, verbose_name="创建人工号")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "柜格"
        verbose_name_plural = "柜格"
        unique_together = ('cabinet', 'position')  # 同一个柜体内位置编号唯一
        ordering = ['cabinet', 'row', 'col']

    def __str__(self):
        return f"{self.cabinet.name} - {self.position}"


class GridRecord(models.Model):
    """柜格记录模型，记录状态变化"""
    ACTION_CHOICES = (
        ('create', '创建'),
        ('update', '更新'),
        ('reserve', '预定'),
        ('use', '使用'),
        ('release', '释放'),
        ('keep', '拿取保留中'),
    )

    grid = models.ForeignKey(CabinetGrid, on_delete=models.CASCADE, related_name='records', verbose_name="柜格")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作")
    old_status = models.CharField(choices=CabinetGrid.STATUS_CHOICES, max_length=20, verbose_name="原状态")
    new_status = models.CharField(choices=CabinetGrid.STATUS_CHOICES, max_length=20, verbose_name="新状态")
    Customer = models.CharField(max_length=100, blank=True, verbose_name="客戶別")
    ProCode = models.CharField(max_length=100, blank=True, verbose_name="客戶ProCode")
    CampalCode = models.CharField(max_length=100, blank=True, verbose_name="CampalCode")
    Brow_at = models.DateTimeField(verbose_name="留樣日期")
    BrowReson = models.CharField(max_length=2000, blank=True, verbose_name="留樣原因")
    Take_at = models.DateTimeField(verbose_name="拿取日期")
    TakeReson = models.CharField(max_length=2000, blank=True, verbose_name="拿取原因")
    Back_at = models.DateTimeField(verbose_name="放回日期")
    user = models.CharField(max_length=20, blank=True, verbose_name="借用人（工号）")
    phone = models.CharField(max_length=20, blank=True, verbose_name="联系电话")
    notes = models.CharField(max_length=2000, blank=True, verbose_name="備注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        verbose_name = "柜格记录"
        verbose_name_plural = "柜格记录"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.grid} - {self.get_action_display()} ({self.get_old_status_display()} → {self.get_new_status_display()})"