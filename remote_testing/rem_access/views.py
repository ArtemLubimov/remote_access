from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Create your views here.


def index(request):
    """

    :param request:
    :return:
    """
    if request.POST:
        return HttpResponseRedirect(reverse('result'))
    return render(request, 'index.html')


def result(request):
    """

    :param request:
    :return:
    """
    return HttpResponse("result.")
