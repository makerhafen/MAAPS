from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machine_from_session, find_session_redirect, get_profile_from_post
from maaps.views.functions.payment import create_material_payment


def machine__pay_material(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    payment, transaction = None, None
    error = None
    value_before_payment = None

    payment_value = request.POST.get("payment_value", None)
    if payment_value != None:
        payment_value = float(payment_value)
        if payment_value > 0.001:
            user_profile, error = get_profile_from_post(request)
            if user_profile is not None:
                if user_profile.paying_user != None:
                    paying_user_profile = user_profile.paying_user
                else:
                    paying_user_profile = user_profile

                value_before_payment = paying_user_profile.prepaid_deposit
                payment, transaction = create_material_payment(payment_value, paying_user_profile, user_profile)

    template = loader.get_template('machine/pay_material.html')
    return HttpResponse(template.render({
        "machine": machine,
        "payment": payment,
        "transaction": transaction,
        "last_error": error,
        "value_before_payment": value_before_payment
    }, request))
