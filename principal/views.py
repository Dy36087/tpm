from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
    return HttpResponse("PTM app is running")


@login_required
def ptmprincipal(request):
    return HttpResponse("PTM protected area")
