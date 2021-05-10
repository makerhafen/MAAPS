from django.http import HttpResponse
from django.template import loader
import maaps.models as models
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.utils import timezone


@staff_member_required
def webif__info(request):
    return HttpResponse(loader.get_template('webif/info.html').render({}, request))
