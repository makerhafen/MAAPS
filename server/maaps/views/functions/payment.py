import maaps.models as models
from django.utils import timezone


def user_can_pay(user_profile):
    _user_can_pay = user_profile.prepaid_deposit > 0 or user_profile.allow_invoice
    if _user_can_pay is False:
        return False, "no_deposit_available"
    return True, ""


def create_payment_session(machine, paying_user_profile):
    r, error = user_can_pay(paying_user_profile)
    if r is False:
        return error
    paymentsession = models.MachineSessionPayment()
    paymentsession.price_per_usage = machine.price_per_usage
    paymentsession.price_per_hour = machine.price_per_hour
    paymentsession.user = paying_user_profile.user
    paymentsession.start = timezone.now()
    paymentsession.machinesession = machine.currentSession
    paymentsession.save()
    machine.currentSession.paymentsession = paymentsession
    machine.currentSession.save()
    return None


def create_material_payment(value, paying_user_profile, user_profile):
    transaction = None
    payment = models.MaterialPayment()
    payment.value = value
    payment.user = paying_user_profile.user
    payment.creator = user_profile.user
    if paying_user_profile.allow_invoice is False:
        transaction = models.Transaction()
        transaction.user = paying_user_profile.user
        transaction.value = value
        transaction.type = models.TransactionType.from_deposit_for_material
        transaction.save()
        payment.transaction = transaction
        paying_user_profile.prepaid_deposit -= value
        paying_user_profile.save()
    payment.save()
    return payment, transaction
