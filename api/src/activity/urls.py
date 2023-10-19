from django.urls import path
from . import views

urlpatterns = [
    path("trigger_report/", views.trigger_report),
    path("get_report/", views.get_report),
]
