from rest_framework import serializers
from .models import *

class DeviceAPDQATPEerilizer(serializers.ModelSerializer):
    class Meta:
        model = DeviceAPDQATPE
        fields = "__all__"