from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, get_machine_from_post, find_session_redirect


def machine__login_machine(request):
    machine = get_machine_from_session(request)
    if machine != None:
        return find_session_redirect(machine)
    machine, error = get_machine_from_post(request)
    if machine is not None:
        return find_session_redirect(machine)
    return HttpResponse(loader.get_template('machine/login_machine.html').render({
        "last_error" : error,
    }, request))
