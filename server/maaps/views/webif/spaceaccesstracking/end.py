from django.shortcuts import render
from django.shortcuts import redirect
import base64
from django.contrib.admin.views.decorators import staff_member_required
import maaps.models as models
from maaps.views.functions.session import get_profile_from_session, end_session
from django.utils import timezone


@staff_member_required
def webif__spaceaccesstracking_end(request, spaceaccesstracking_id):
    spaceAccessTracking = models.SpaceAccessTracking.objects.get(id=spaceaccesstracking_id)
    spaceAccessTracking.end = timezone.now()
    spaceAccessTracking.save()
    return redirect('webif__dashboard')
