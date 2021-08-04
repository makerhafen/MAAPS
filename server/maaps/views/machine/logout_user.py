from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from maaps.views.functions.session import get_machine_from_session, find_session_redirect, end_session


def machine__logout_user(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)
    if machine.current_session is None:
        return find_session_redirect(machine)

    current_session, current_payment_session = end_session(machine.current_session)
    if current_session.start is None:  # user aborted before start
        return redirect('machine__login')


    template = loader.get_template('machine/logout_user.html')
    return HttpResponse(template.render({
        "machine": machine,
        "last_machine_session": current_session,
        "last_payment_session": current_payment_session,
    }, request))
