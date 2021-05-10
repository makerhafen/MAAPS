from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, find_session_redirect, get_profile_from_post, get_profile_from_url_token
from maaps.views.functions.payment import create_payment_session


def machine__other_user_pays(request, user_token = ""):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    payer_user_profile, error = get_profile_from_post(request)
    if payer_user_profile is not None:
        error = create_payment_session(machine, payer_user_profile)
        if error is None:
            return find_session_redirect(machine)

    if payer_user_profile is None and user_token != "":
        payer_user_profile, error = get_profile_from_url_token(user_token)
        if user_token is not None:
            error = create_payment_session(machine, payer_user_profile)
        if error is None:
            return find_session_redirect(machine)

    return HttpResponse(loader.get_template('machine/other_user_pays.html').render({
        "machine": machine,
        "last_error": error,
    }, request))
