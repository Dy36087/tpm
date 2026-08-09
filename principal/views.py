from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "ptm.html")


@login_required
def ptmprincipal(request):
    return render(request, "ptm.html")
