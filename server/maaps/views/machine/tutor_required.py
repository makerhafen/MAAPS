from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, find_session_redirect, get_profile_from_post


def machine__tutor_required(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    tutor_profile, error = get_profile_from_post(request)
    if tutor_profile is not None:
        if machine.user_can_tutor(tutor_profile.user):
            machine.current_session.tutor = tutor_profile.user
            machine.current_session.save()
            return find_session_redirect(machine)
        else:
            error = "tutor_not_allowed"

    machine_usage_count = machine.count_usages(machine.current_session.user)

    return HttpResponse(loader.get_template('machine/tutor_required.html').render({
        "machine": machine,
        "machine_usage_count": machine_usage_count,
        "tutor_required": machine.user_requires_tutor(machine.current_session.user),
        "tutor_required_once": machine.user_requires_tutor_once(machine.current_session.user),
        "last_error": error,
    }, request))

