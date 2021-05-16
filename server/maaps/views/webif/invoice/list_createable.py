import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__invoice__list_createable(request):


    return HttpResponse(loader.get_template('webif/invoice/list_createable.html').render({

    }, request))
