from django.http import HttpResponse, HttpResponse400
from django.template import loader
import maaps.models as models
from maaps.views.functions.session import get_machine_from_session, get_profile_from_post, find_session_redirect, \
    get_profile_from_url_token


def api_login_user_to_machine(request, machine_id, user_token):
    machine = models.Machine.objects.get(pk=machine_id)
    user_profile, error = get_profile_from_url_token(user_token)
    if user_profile is not None:
        if machine.user_is_allowed(user_profile.user):
            machinesession = models.MachineSession()
            machinesession.machine = machine
            machinesession.user = user_profile.user
            machinesession.save()
            machine.current_session = machinesession
            machine.save()
            return HttpResponse("session:id", machinesession.pk)
    return HttpResponse400()


def api_logout_user_from_machine(request, machine_id, user_token):
    machine = models.Machine.objects.get(pk=machine_id)
    user_profile, error = get_profile_from_url_token(user_token)
    if machine.current_session.user.profile == user_profile:
        current_session, current_payment_session = end_session(machine.current_session)

    return HttpResponse400()