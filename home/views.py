from django.shortcuts import render, HttpResponse

# Create your views here.
from django.views.decorators.clickjacking import xframe_options_exempt


def index(request):
    return render(request, "home/index.html")

@xframe_options_exempt
def profile_page(request, username):
    if username == "ahn":
        template = "home/profile/ahn.html"
    elif username == "min":
        template = "home/profile/min.html"
    elif username == "kang":
        template = "home/profile/kang.html"
    elif username == "kim":
        template = "home/profile/kim.html"
    elif username == "lee":
        template = "home/profile/lee.html"
    else:
        return HttpResponse("Profile not found", status=404)
    return render(request, template, {"username": username})