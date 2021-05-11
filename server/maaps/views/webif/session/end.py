from django.shortcuts import render
from django.shortcuts import redirect
import base64
from django.contrib.admin.views.decorators import staff_member_required
import maaps.models as models
from maaps.views.functions.session import get_profile_from_session, end_session


@staff_member_required
def webif__session_end(request, session_id):
    session = models.MachineSession.objects.get(id=session_id)
    end_session(session)
    return redirect('webif__dashboard')
