from rest_framework import serializers
from .models import CampaignSetting

class CampaignSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignSetting
        fields = '__all__'
