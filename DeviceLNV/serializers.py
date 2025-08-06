from rest_framework import serializers
from .models import *

class DeviceLNVerilizer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLNV
        fields = "__all__"