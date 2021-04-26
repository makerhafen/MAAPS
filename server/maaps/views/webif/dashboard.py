from django.http import HttpResponse
from django.template import loader
import maaps.models as models
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.utils import timezone


@staff_member_required
def webif__dashboard(request):
    machineSessions_active = models.MachineSession.objects.filter(end=None)
    machineSessions_ended = models.MachineSession.objects.filter(end__gt=timezone.now() - timedelta(hours=1))
    template = loader.get_template('webif/dashboard.html')
    return HttpResponse(template.render({
        "machineSessions_active": machineSessions_active,
        "machineSessions_ended": machineSessions_ended,
    }, request))
