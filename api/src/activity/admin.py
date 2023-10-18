from django.contrib import admin

# Register your models here.

from .models import TimeZone, BusinessHour, Activity, Report

admin.site.register(TimeZone)
admin.site.register(BusinessHour)
admin.site.register(Activity)
admin.site.register(Report)
