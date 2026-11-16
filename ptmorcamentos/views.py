from django.shortcuts import render

# Create your views here.


def ptmorcamentosindex(request):
    return render(request, 'ptmorcamentosindex.html')

def ptmorcamentonovo(request):
    return render(request, 'ptmorcamentonovo.html')