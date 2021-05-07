from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session
from maaps.views.functions.payment import create_material_payment


def pos__payment(request):
    payment, transaction = None, None
    error = None
    value_before_payment = None

    payment_value = request.POST.get("payment_value", None)
    if payment_value is not None:
        payment_value = float(payment_value)
        if payment_value <= 0:
            error = "invalid_payment_value"
        else:
            user_profile, error = get_profile_from_post(request)
            if user_profile is not None:
                paying_user_profile = user_profile
                if user_profile.paying_user is not None:  # read user via card, his paying user pays
                    paying_user_profile = user_profile.paying_user
                payment, transaction = create_material_payment(payment_value, paying_user_profile, user_profile)

    template = loader.get_template('pos/payment.html')
    return HttpResponse(template.render({
        "payment": payment,
        "transaction": transaction,
        "last_error": error,
        "value_before_payment": value_before_payment
    }, request))
