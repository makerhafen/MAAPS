from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
import maaps.models as models
from maaps.views.functions.session import get_profile_from_post, get_profile_from_session
from django.utils import timezone
from datetime import timedelta
from maaps.views.functions.payment import pay_spaceRentPayment, pay_prepaid_deposit


def webif__user__deposit(request, profile_id):

    transaction = None
    value_before_payment = None
    error = None
    deposit_value = request.POST.get("deposit_value", None)
    transaction_type = request.POST.get("type", None)
    user_profile = models.Profile.objects.get(id=profile_id)

    if deposit_value is not None:
        deposit_value = float(deposit_value)
        if deposit_value <= 0:
            error = "invalid_deposit_value"
        else:
            if user_profile is not None:
                invoice = None
                if transaction_type == models.TransactionType.from_cash_for_deposit or transaction_type == models.TransactionType.from_bank_for_deposit:
                    transaction, invoice = pay_prepaid_deposit(user_profile, deposit_value, transaction_type)

                if transaction_type == models.TransactionType.from_cash_for_rent or transaction_type == models.TransactionType.from_bank_for_rent:
                    transaction, invoice = pay_spaceRentPayment(user_profile, deposit_value, transaction_type)

                return redirect('webif__invoice__show',invoice_id=invoice.id)

    template = loader.get_template('webif/user/deposit.html')
    return HttpResponse(template.render({
        "transaction": transaction,
        "last_error": error,
        "profile": user_profile,
        "value_before_payment": value_before_payment
    }, request))
