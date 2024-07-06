# -*- coding: utf-8 -*-
from django.db import models
import django.utils.timezone as timezone
from DjangoUeditor.models import UEditorField #头部增加这行代码导入UEditorField

# Create your models here.
from django.contrib.auth.models import User

#导入Django自带用户模块
class Imgs(models.Model):
    # id = models.AutoField(max_length=10, primary_key=True, verbose_name='id')
    img = models.ImageField(upload_to='img/UserInfo/',verbose_name='图片地址')
    single = models.CharField(max_length=200,null=True, blank=True,verbose_name='图片名称')
    def __unicode__(self):  # __str__ on Python 3
        return (self.id,self.img)

    # def __str__(self):
    #     return str(self.single)
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
@receiver(pre_delete, sender=Imgs)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.img.delete(False)


class UserInfo(models.Model):
    """
    用户：划分角色
    """
    SeatChoice = (
        ('KS-Plant5', 'KS-Plant5'),
        ('KS-Plant3', 'KS-Plant3'),
        ('KS-Plant2', 'KS-Plant2'),
        ('CQ', 'CQ'),
        ('CD', 'CD'),
    )
    DEPARTMENT_CHOICES = {
        (1, '测试部门'),
        (2, '开发部门'),
        (3, 'PM'),
        (4, '其它部门'),
    }
    account = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=64)
    username = models.CharField(max_length=32)
    CNname = models.CharField(max_length=32, default='')
    # Customer = models.CharField(max_length=32, null=True, blank=True, default='')
    Tel = models.CharField(max_length=32 ,null=True, blank=True,default='')
    Seat = models.CharField(max_length=108, choices=SeatChoice, default='KS-Plant5')
    email = models.EmailField()
    department = models.IntegerField(verbose_name='部门', choices=DEPARTMENT_CHOICES, default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_SVPuser = models.BooleanField(default=False)
    role = models.ManyToManyField("Role")
    Photo = models.ManyToManyField(Imgs, related_name='imgs', blank=True, verbose_name='图片表')

    class Meta:
        verbose_name = 'UserInfo'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class Role(models.Model):
    """
    角色：绑定权限
    """
    name = models.CharField(max_length=32, unique=True)
    perms=models.ManyToManyField('Permission')

    class Meta:
        verbose_name = 'Role'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name

class Permission(models.Model):
    """
    权限
    """
    Menu_title=models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=128, unique=True)
    menu = models.ForeignKey("Menu", null=True, blank=True, on_delete=True)
    class Meta:
        verbose_name = 'Permission'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示带菜单前缀的权限
        return '{menu}---{permission}'.format(menu=self.menu, permission=self.Menu_title)

class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(max_length=32, unique=True)
    parent = models.ForeignKey("Menu", null=True, blank=True,on_delete=True)
    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单
    class Meta:
        verbose_name = 'Menu'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


