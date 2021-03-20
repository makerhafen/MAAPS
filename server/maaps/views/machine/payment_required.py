from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, find_session_redirect
from maaps.views.functions.payment import user_can_pay, create_payment_session


def machine__payment_required(request):
    machine = get_machine_from_session(request)
    if machine is  None:
        return find_session_redirect(machine)

    paying_user_profile = machine.currentSession.user.profile
    if machine.currentSession.user.profile.paying_user is not None:
        paying_user_profile = machine.currentSession.user.profile.paying_user
    _user_can_pay, error = user_can_pay(paying_user_profile)
    if _user_can_pay is True:
        confirm_payment = request.POST.get("confirm_payment", None)
        if confirm_payment == "confirm_payment":
            error = create_payment_session(machine, paying_user_profile)
            if error is None:
                return find_session_redirect(machine)

    return HttpResponse(loader.get_template('machine/payment_required.html').render({
        "machine": machine,
        "last_error": error,
        "paying_user": paying_user_profile.user,
        "user_can_pay": _user_can_pay,
    }, request))