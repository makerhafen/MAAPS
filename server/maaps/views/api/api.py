from django.http import HttpResponse, HttpResponseNotFound
import maaps.models as models
from maaps.views.functions.session import get_profile_from_url_token, end_session


def get_machine_by_token_or_id(machine_token):
    try:
        if machine_token.isdigit():
            return models.Machine.objects.get(pk=int(machine_token))
        tkn = models.Token.objects.filter(identifier__contains=machine_token, machine__isnull=False).first()
        if tkn:
            return tkn.machine
        return models.Machine.objects.get(name=machine_token)
    except Exception:
        return None


def api_login_user_to_machine(request, machine_token, user_token):
    machine = get_machine_by_token_or_id(machine_token)
    if machine is None:
        return HttpResponseNotFound("Machine not found")

    user_profile, error = get_profile_from_url_token(user_token)
    if user_profile is not None:
        if machine.user_is_allowed(user_profile.user):
            machinesession = models.MachineSession()
            machinesession.machine = machine
            machinesession.user = user_profile.user
            machinesession.save()
            machine.current_session = machinesession
            machine.save()
            return HttpResponse(f"session:{machinesession.pk}")
    return HttpResponse("Unauthorized or error", status=400)


def api_logout_user_from_machine(request, machine_token, user_token):
    machine = get_machine_by_token_or_id(machine_token)
    if machine is None or machine.current_session is None:
        return HttpResponseNotFound("Machine or active session not found")

    user_profile, error = get_profile_from_url_token(user_token)
    if user_profile and machine.current_session.user.profile == user_profile:
        current_session, current_payment_session = end_session(machine.current_session)
        return HttpResponse("Logout successful")

    return HttpResponse("Logout failed", status=400)
