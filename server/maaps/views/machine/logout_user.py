from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
import maaps.models as models
from maaps.views.functions.session import get_machine_from_session, find_session_redirect


def machine__logout_user(request):
    machine = get_machine_from_session(request)
    if machine is None:
        return find_session_redirect(machine)

    current_session = machine.currentSession
    current_payment_session = None
    if current_session != None:
        if hasattr(current_session, "paymentsession"):

            current_payment_session = current_session.paymentsession
            current_payment_session.end = timezone.now()

            timediff_hours = (current_payment_session.end - current_payment_session.start).total_seconds()/3600.0
            total_price = round(machine.price_per_usage + timediff_hours * machine.price_per_hour,2)

            current_payment_session.totalpayment = total_price

            if current_payment_session.user.profile.allow_invoice is False:
                transaction = models.Transaction()
                transaction.user = current_payment_session.user
                transaction.value = current_payment_session.totalpayment
                transaction.type = models.TransactionType.from_deposit_for_material
                transaction.save()
                current_payment_session.transaction = transaction
                current_payment_session.user.profile.prepaid_deposit -= current_payment_session.totalpayment
                current_payment_session.user.profile.save()

            current_payment_session.save()

        machine.currentSession = None
        machine.save()
        current_session.end = timezone.now()
        current_session.save()


    template = loader.get_template('machine/logout_user.html')
    return HttpResponse(template.render({
        "machine": machine,
        "last_machine_session" : current_session,
        "last_payment_session" : current_payment_session,
    }, request))

