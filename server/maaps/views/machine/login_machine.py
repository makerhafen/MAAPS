from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, get_machine_from_post, find_session_redirect
from maaps.models import Token


def machine__login_machine(request, machine_token=""):
    error = None
    if machine_token != "" and machine_token is not None:
        machine_token = "M:" + machine_token
        try:
            machine = Token.objects.get(identifier=machine_token).machine
            request.session["machine_id"] = machine.id
        except Exception:
            error = "unknown_token"
    if error is None:
        machine = get_machine_from_session(request)
        if machine is not None:
            return find_session_redirect(machine)
        machine, error = get_machine_from_post(request)
        if machine is not None:
            return find_session_redirect(machine)

    return HttpResponse(loader.get_template('machine/login_machine.html').render({
        "last_error": error,
    }, request))
