# Generated by Django 2.1.7 on 2023-09-22 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WirelessAP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Room', models.CharField(max_length=30, verbose_name='Room No.')),
                ('Owner_Num', models.CharField(max_length=30, verbose_name='AP Owner工號')),
                ('Owner_EN', models.CharField(max_length=30, verbose_name='AP Owner')),
                ('Category', models.CharField(max_length=64, verbose_name='Category')),
                ('Net_Area', models.CharField(max_length=512, verbose_name='外網網點')),
                ('AP_Model', models.CharField(max_length=256, verbose_name='AP廠商型號')),
                ('AP_SSID', models.CharField(max_length=128, verbose_name='AP SSID')),
                ('Channel_24G', models.CharField(blank=True, max_length=28, null=True, verbose_name='2.4GHz Channel')),
                ('Channel_5G', models.CharField(blank=True, max_length=28, null=True, verbose_name='5GHz Channel')),
                ('Channel_6G', models.CharField(blank=True, max_length=28, null=True, verbose_name='6GHz Channel')),
                ('AP_Psw', models.CharField(max_length=128, verbose_name='AP Password')),
                ('AP_IP', models.CharField(max_length=128, verbose_name='IP')),
                ('Brw_Owner_Num', models.CharField(blank=True, max_length=26, null=True, verbose_name='借用人工號')),
                ('Brw_Owner_CN', models.CharField(blank=True, max_length=26, null=True, verbose_name='借用人')),
                ('Start_Time', models.DateTimeField(blank=True, max_length=64, null=True, verbose_name='借用時間(Start)')),
                ('End_Time', models.DateTimeField(blank=True, max_length=64, null=True, verbose_name='借用時間(End)')),
                ('Project', models.CharField(blank=True, max_length=50, null=True, verbose_name='Project(Compal name)')),
                ('Case', models.CharField(blank=True, max_length=256, null=True, verbose_name='Test Case')),
                ('Comments', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Comments')),
            ],
            options={
                'verbose_name': 'WirelessAP',
                'verbose_name_plural': 'WirelessAP',
            },
        ),
    ]
