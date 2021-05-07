from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
import maaps.models as models
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session


def pos__deposit(request):
    admin_profile = get_profile_from_session(request)
    if admin_profile is None:
        return redirect('pos__index')
    if not admin_profile.user.is_staff: # this page is only allowed by admin
        request.session["profile_id"] = None
        return redirect('pos__index')

    transaction = None
    value_before_payment = None
    error = None
    deposit_value = request.POST.get("deposit_value", None)
    if deposit_value is not None:
        deposit_value = float(deposit_value)
        if deposit_value <= 0:
            error = "invalid_deposit_value"
        else:
            user_profile, error = get_profile_from_post(request)
            if user_profile is not None:
                transaction = models.Transaction()
                transaction.user = user_profile.user
                transaction.value = deposit_value
                transaction.type = models.TransactionType.from_cash_for_deposit
                transaction.authorized_by = admin_profile.user
                transaction.save()
                value_before_payment = user_profile.prepaid_deposit
                user_profile.prepaid_deposit += deposit_value
                user_profile.save()

    template = loader.get_template('pos/deposit.html')
    return HttpResponse(template.render({
        "transaction": transaction,
        "last_error": error,
        "value_before_payment": value_before_payment
    }, request))
