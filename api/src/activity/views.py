from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TimeZone
from .serializers import TimeZoneSerializer
from util.functions import stores, get_store_timezone

# Create your views here.


@api_view()
def trigger_report(request):
    tz = TimeZone.objects.values("timezone_str")
    tzs = TimeZoneSerializer(tz, many=True)
    return Response(tzs.data)


@api_view()
def get_report(request):
    tz = TimeZone.objects.values("timezone_str")
    tzs = TimeZoneSerializer(tz, many=True)
    return Response(tzs.data)
