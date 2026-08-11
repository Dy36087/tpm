from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    return render(request, "ptm.html")


@login_required
def ptmprincipal(request):
    return render(request, "ptm.html")
