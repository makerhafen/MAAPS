from django.http import HttpResponse
from django.template import loader
import maaps.models as models
from maaps.views.functions.session import get_machine_from_session, get_profile_from_post, find_session_redirect, get_profile_from_url_token


def machine__login_user(request, user_token=""):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)
    user_profile, error = get_profile_from_post(request)

    if user_profile is None and user_token != "":
        user_profile, error = get_profile_from_url_token(user_token)

    if user_profile is not None:
        if machine.user_is_allowed(user_profile.user):
            machineSession = models.MachineSession()
            machineSession.machine = machine
            machineSession.user = user_profile.user
            machineSession.save()
            machine.currentSession = machineSession
            machine.save()
            return find_session_redirect(machine)
        else:
            error = "user_not_allowed"

    return HttpResponse(loader.get_template('machine/login_user.html').render({
        "machine": machine,
        "last_error": error,
    }, request))