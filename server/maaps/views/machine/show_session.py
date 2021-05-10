from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from maaps.views.functions.session import get_machine_from_session, find_session_redirect, end_session


def machine__show_session(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)
    if machine.current_session is None:
        return find_session_redirect(machine)

    if machine.current_session.start is None:
        machine.current_session.start = timezone.now()
        machine.current_session.save()

    if machine.current_session.autologout_at is not None:
        if machine.current_session.autologout_timediff[0] <= 0:
            current_session, current_payment_session = end_session(machine)
            return find_session_redirect(machine)

    return HttpResponse(loader.get_template('machine/show_session.html').render({
        "machine": machine
    }, request))
