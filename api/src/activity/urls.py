from django.urls import path
from . import views

urlpatterns = [
    path("trigger_report/", views.trigger_report),
    path("get_report/<str:report_id>", views.get_report),
]
