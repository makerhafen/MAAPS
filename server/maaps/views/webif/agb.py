import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__agb(request):
    return HttpResponse(loader.get_template('webif/agb.html').render({
    }, request))
