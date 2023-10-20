from rest_framework.decorators import api_view
from rest_framework.response import Response
from util.handler import main_operation

# Create your views here.


@api_view()
def trigger_report(request):
    main_operation()
    return Response("Trigger Report")


@api_view()
def get_report(request):
    return Response("Get Report")
