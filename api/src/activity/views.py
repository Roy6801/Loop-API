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
    """
    View for triggering the generation of a new report.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: Response containing the generated report ID.
    """

    # Generate a new report ID.
    report_id = get_report_id()

    # Trigger the report generation process with a batch size of 10.
    trigger_report_generation(report_id, batch_size=10)

    # Return a response containing the generated report ID.
    return Response(report_id)


@api_view()
def get_report(request: Request, report_id: str) -> Response:
    """
    View for retrieving information about a specific report.

    Args:
        request (Request): The HTTP request object.
        report_id (str): The unique identifier of the report to retrieve.

    Returns:
        Response: Response containing report information or a "Report not found" message.
    """

    report: Report | None
    file_path: str
    response: Dict[str, str]
    base_url: str

    # Retrieve the report object from the database based on the report_id.
    report = Report.objects.filter(report_id=report_id).first()

    if report is None:
        # If the report is not found, return a 404 (Not Found) response.
        return Response(
            {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
        )

    response = {
        "status": report.status,
    }

    file_path = f"report/{report_id}.csv"

    if report.status == Report.STATUS_COMPLETE:
        if os.path.exists(file_path):
            # If the report is complete and the file exists, construct a URL to retrieve the file.
            base_url = request.scheme + "://" + request.META["HTTP_HOST"]
            response[
                "report"
            ] = f'{base_url}{reverse("get_report_file", args=(report_id,))}'
        else:
            # If the report file is not found, return a 404 (Not Found) response.
            return Response(
                {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
            )

    return Response(response)


@api_view()
def get_report_file(request: Request, report_id: str) -> Response | HttpResponse:
    """
    View for retrieving the actual report file in CSV format.

    Args:
        request (Request): The HTTP request object.
        report_id (str): The unique identifier of the report to retrieve.

    Returns:
        Response or HttpResponse: Response containing the report file content or a "Report not found" message.
    """

    file_path: str
    response: HttpResponse

    file_path = f"report/{report_id}.csv"

    if os.path.exists(file_path):
        with open(file_path, "r") as fr:
            response = HttpResponse(content=fr.read(), content_type="text/csv")
            return response
    else:
        # If the report file is not found, return a 404 (Not Found) response.
        return Response(
            {"detail": "Report not found!"}, status=status.HTTP_404_NOT_FOUND
        )
