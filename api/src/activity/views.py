from rest_framework.decorators import api_view
from rest_framework.response import Response
from util.generate_report import GenerateReport
from .tasks import trigger_report_generation
from .models import Report

# Create your views here.


@api_view()
def trigger_report(request):
    report_generator = GenerateReport()
    report_id = report_generator.get_report_id()
    trigger_report_generation.delay(report_generator)
    return Response(report_id)


@api_view()
def get_report(request):
    status = Report.objects.filter(report_id=request.report_id)
    return Response(status)
