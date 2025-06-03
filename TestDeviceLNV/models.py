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
    Act_Status = models.CharField(max_length=64, null=True, blank=True, verbose_name='Act_Status')
    Device_Know_Issue = models.CharField(max_length=5000, null=True, blank=True, verbose_name='Device Know Issue')
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


# 方法 1：使用第三方库 django-jsonfield
# pip install django-jsonfield
# from jsonfield import JSONField  # 注意导入方式
#
# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     attributes = JSONField(default=dict)  # 存储 JSON 数据

# 方法 2：手动使用 TextField + JSON 序列化
# import json
#
# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     attributes = models.TextField(default='{}')  # 存储 JSON 字符串
#
#     def get_attributes(self):
#         """将 TextField 字符串解析为 Python 字典"""
#         return json.loads(self.attributes)
#
#     def set_attributes(self, data):
#         """将字典序列化为字符串存入数据库"""
#         self.attributes = json.dumps(data)

# 方法 3：终极建议：升级 Django 版本
# 如果项目允许，强烈建议升级到 Django ≥ 3.1，直接使用原生 JSONField：

# 新增数据
# python
# # 方法 1（使用 django-jsonfield）
# product = Product.objects.create(
#     name="Laptop",
#     attributes={"color": "silver", "ports": ["USB-C", "HDMI"]}
# )
#
# # 方法 2（手动处理）
# product = Product(name="Laptop")
# product.set_attributes({"color": "silver", "ports": ["USB-C", "HDMI"]})
# product.save()

# 查询数据
# python
# # 方法 1：直接查询键值（需数据库支持，如 MySQL 5.7+）
# # 注意：django-jsonfield 的查询语法可能有限
# products = Product.objects.filter(attributes__color="silver")
#
# # 方法 2：手动过滤（效率较低）
# all_products = Product.objects.all()
# silver_products = [
#     p for p in all_products
#     if p.get_attributes().get('color') == 'silver'
# ]
#
# # 使用原生 SQL 查询（MySQL 5.7+）
# query = """
#     SELECT * FROM app_product
#     WHERE JSON_EXTRACT(attributes, '$.color') = 'silver'
# """
# silver_products = Product.objects.raw(query)

# 修改数据
# python
# product = Product.objects.get(id=1)
#
# # 方法 1：直接修改字典
# attrs = product.attributes
# attrs["price"] = 999
# product.attributes = attrs
# product.save()
#
# # 方法 2：通过辅助方法
# attrs = product.get_attributes()
# attrs["price"] = 999
# product.set_attributes(attrs)
# product.save()
# 删除键值
# python
# product = Product.objects.get(id=1)
# attrs = product.attributes
#
# # 删除键
# if "price" in attrs:
#     del attrs["price"]
# product.attributes = attrs
# product.save()