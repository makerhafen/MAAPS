from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from maaps.views.functions.session import get_machine_from_session, find_session_redirect


def machine__show_session(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    if machine.currentSession.start is None:
        machine.currentSession.start = timezone.now()
        machine.currentSession.save()

    return HttpResponse(loader.get_template('machine/show_session.html').render({
        "machine": machine
    }, request))