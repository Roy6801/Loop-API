from .util.handler import trigger_report_generation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .util.functions import get_report_id
from django.http import HttpResponse
from rest_framework import status
from django.urls import reverse
from .models import Report
import os

# Create your views here.


@api_view()
def trigger_report(request):
    report_id = get_report_id()
    trigger_report_generation(report_id, batch_size=10)
    return Response(report_id)


@api_view()
def get_report(request, report_id):
    report = Report.objects.filter(report_id=report_id).first()
    if report is None:
        return Response(
            {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
        )

    response_data = {
        "status": report.status,
    }

    file_path = f"report/{report_id}.csv"

    if report.status == Report.STATUS_COMPLETE:
        if os.path.exists(file_path):
            base_url = request.scheme + "://" + request.META["HTTP_HOST"]
            response_data[
                "report"
            ] = f'{base_url}{reverse("get_report_file", args=(report_id,))}'
        else:
            Response({"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data)


@api_view()
def get_report_file(request, report_id):
    file_path = f"report/{report_id}.csv"

    if os.path.exists(file_path):
        with open(file_path, "r") as fr:
            response = HttpResponse(content=fr.read(), content_type="text/csv")
    else:
        Response({"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND)

    return response
