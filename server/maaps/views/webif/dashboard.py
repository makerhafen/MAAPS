from django.http import HttpResponse
from django.template import loader
import maaps.models as models
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

@staff_member_required
def webif__dashboard(request):
    machinesessions_active = models.MachineSession.objects.filter(end=None)
    machinesessions_ended = models.MachineSession.objects.filter(end__gt=timezone.now() - timedelta(hours=1))
    spaceAccessTrackings_latest = models.SpaceAccessTracking.objects.filter(Q(end=None) | Q(end__gt=timezone.now() - timedelta(hours=1)))
    template = loader.get_template('webif/dashboard.html')
    return HttpResponse(template.render({
        "machineSessions_active": machinesessions_active,
        "machineSessions_ended": machinesessions_ended,
        "spaceAccessTrackings_latest": spaceAccessTrackings_latest,
    }, request))

