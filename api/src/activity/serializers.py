from rest_framework import serializers


class TimeZoneSerializer(serializers.Serializer):
    store_id = serializers.CharField(max_length=255, required=False)
    timezone_str = serializers.CharField(max_length=255, required=False)
