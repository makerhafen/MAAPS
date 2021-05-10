from django.http import HttpResponse
from django.template import loader
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect
from maaps.views.functions.session import get_machine_from_session, find_session_redirect


def machine__auto_logout(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    autologout_in_minutes = request.POST.get("autologout_in_minutes", None)
    if autologout_in_minutes is not None:
        autologout_in_minutes = int(autologout_in_minutes)
        if autologout_in_minutes > 0:
            machine.current_session.autologout_at = timezone.now() + timedelta(minutes=autologout_in_minutes)
        else:
            machine.current_session.autologout_at = None
        machine.current_session.save()
        return redirect('machine__show_session')

    timediff_total_minutes = None
    if machine.current_session.autologout_at is not None:
        timediff_total_minutes = (machine.current_session.autologout_at - timezone.now()).total_seconds() / 60

    return HttpResponse(loader.get_template('machine/auto_logout.html').render({
        "machine": machine,
        "timediff_total_minutes": timediff_total_minutes,
    }, request))
