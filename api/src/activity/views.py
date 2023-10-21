from rest_framework.decorators import api_view
from rest_framework.response import Response
from .util.functions import get_report_id
from .util.handler import trigger_report_generation
from django.http import HttpResponse
from rest_framework import status
from .models import Report

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
    if report.status == Report.STATUS_COMPLETE:
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="report/{report_id}.csv"'

        response_data["report"] = response.content

    return Response(response_data)
