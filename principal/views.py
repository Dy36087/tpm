from django.shortcuts import render


def index(request):
    return render(request, "ptm.html")


def ptmprincipal(request):
    return render(request, "ptm.html")
