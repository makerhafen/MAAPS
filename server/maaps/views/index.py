from django.http import HttpResponse
from django.template import loader

def index(request):
    return HttpResponse(loader.get_template('index.html').render({}, request))
