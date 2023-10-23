from .util.handler import trigger_report_generation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .util.functions import get_report_id
from django.http import HttpResponse
from rest_framework import status
from django.urls import reverse
from .models import Report
from typing import Dict
import os

# Create your views here.


@api_view()
def trigger_report(request: Request) -> Response:
    print("REQUEST", request)

    report_id = get_report_id()
    trigger_report_generation(report_id, batch_size=10)
    return Response(report_id)


@api_view()
def get_report(request: Request, report_id: str) -> Response:
    report: Report | None
    file_path: str
    response: Dict[str, str]
    base_url: str

    report = Report.objects.filter(report_id=report_id).first()

    print("REQUEST", request)

    if report is None:
        return Response(
            {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
        )

    response = {
        "status": report.status,
    }

    file_path = f"report/{report_id}.csv"

    if report.status == Report.STATUS_COMPLETE:
        if os.path.exists(file_path):
            base_url = request.scheme + "://" + request.META["HTTP_HOST"]
            response[
                "report"
            ] = f'{base_url}{reverse("get_report_file", args=(report_id,))}'
        else:
            return Response(
                {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
            )

    return Response(response)


@api_view()
def get_report_file(request: Request, report_id: str) -> Response | HttpResponse:
    file_path: str
    response: HttpResponse

    file_path = f"report/{report_id}.csv"

    print("REQUEST", request)

    if os.path.exists(file_path):
        with open(file_path, "r") as fr:
            response = HttpResponse(content=fr.read(), content_type="text/csv")
            return response
    else:
        return Response(
            {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
        )
