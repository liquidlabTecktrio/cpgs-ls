from rest_framework import serializers

from cpgsapp.models import NetworkSettings

class NetworkSettingsSerializer(serializers.ModelSerializer):
     class Meta:
        model = NetworkSettings
        fields = "__all__"