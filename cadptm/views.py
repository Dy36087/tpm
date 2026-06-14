from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import PatrimonioForm


@login_required
def cadptm(request):
    saved = False
    if request.method == "POST":
        form = PatrimonioForm(request.POST)
        if form.is_valid():
            saved = True
            form = PatrimonioForm()
    else:
        form = PatrimonioForm()

    return render(request, "cadptm.html", {"form": form, "saved": saved})
