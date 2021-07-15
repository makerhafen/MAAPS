import maaps.models as models
from django.utils import timezone
from datetime import timedelta
import math

def user_can_pay(user_profile):
    _user_can_pay = user_profile.prepaid_deposit > 0 or user_profile.allow_postpaid
    if _user_can_pay is False:
        return False, "no_deposit_available"
    return True, ""


def create_payment_session(machine, paying_user_profile):
    r, error = user_can_pay(paying_user_profile)
    if r is False:
        return error
    paymentsession = models.MachineSessionPayment()
    price_per_usage, price_per_hour = machine.get_price(paying_user_profile)
    paymentsession.price_per_usage = price_per_usage
    paymentsession.price_per_hour = price_per_hour
    paymentsession.user = paying_user_profile.user
    paymentsession.start = timezone.now()
    paymentsession.machinesession = machine.current_session
    paymentsession.save()
    machine.current_session.machineSessionPayment = paymentsession
    machine.current_session.save()
    return None


def create_material_payment(value, paying_user_profile, user_profile, machine):
    transaction = None
    payment = models.MaterialPayment()
    payment.price = value
    payment.user = paying_user_profile.user
    payment.creator = user_profile.user
    if paying_user_profile.allow_postpaid is False:
        transaction = models.Transaction()
        transaction.user = paying_user_profile.user
        transaction.value = value
        transaction.type = models.TransactionType.from_deposit_for_material
        transaction.save()
        payment.transaction = transaction
        paying_user_profile.prepaid_deposit -= value
        paying_user_profile.save()
    if machine is not None:
        if machine.current_session is not None:
            payment.machinesession = machine.current_session
    payment.save()
    return payment, transaction

def create_invoice(user_profile, value, invoice_type, transaction = None ):
    invoice = models.Invoice()
    invoice.value = value
    invoice.transaction = transaction
    invoice.user = user_profile.user
    invoice.created = timezone.now()
    invoice.due = timezone.now() + timedelta(days=14)
    invoice.type = invoice_type
    invoice.include_tax = user_profile.commercial_account
    invoice.total = invoice.value
    if invoice.include_tax:
        invoice.taxes =  invoice.total * 0.19
        invoice.total += invoice.taxes
    invoice.save()
    return invoice

def create_transaction_and_invoice(user_profile, value, type):
    transaction = models.Transaction()
    transaction.user = user_profile.user
    transaction.value = value
    transaction.type = type
    transaction.save()
    return create_invoice(user_profile, value, models.InvoiceType.receipt, transaction)


def pay_prepaid_deposit(user_profile, value, transaction_type):
    invoice = create_transaction_and_invoice(user_profile, value, transaction_type)
    prepaidDepositPayment = models.PrepaidDepositPayment()
    prepaidDepositPayment.user = user_profile.user
    prepaidDepositPayment.price = value
    prepaidDepositPayment.invoice = invoice
    prepaidDepositPayment.save()
    user_profile.prepaid_deposit += value
    user_profile.save()
    return invoice

def _get_price(profile, identifier ):
    price = models.Price.objects.get(identifier = identifier)
    if profile.get_paying_user().commercial_account:
        return price.commercial
    elif profile.get_paying_user().discount_account:
        return price.discount
    else:
        return price.default

def pay_spaceRentPayment(user_profile, value, transaction_type):
    invoice = create_transaction_and_invoice(user_profile, value, transaction_type)
    spaceRentPayment = models.SpaceRentPayment()
    try:
        current_spaceRentPayment = models.SpaceRentPayment.objects.filter(
                                        for_user=user_profile.user,
                                        user=user_profile.user,
                                        start__lt=timezone.now(),
                                        end__gt=timezone.now()
                                    )[0]
        spaceRentPayment.start = current_spaceRentPayment.end
    except:
        spaceRentPayment.start = timezone.now()

    price_per_month = _get_price(user_profile, identifier="spaceRentPayment.monthly")
    days_payed = int(math.ceil(round(31.0 / price_per_month * value,2)))

    spaceRentPayment.end = spaceRentPayment.start + timedelta(days=days_payed)
    spaceRentPayment.user = user_profile.user
    spaceRentPayment.for_user = user_profile.user
    spaceRentPayment.invoice = invoice
    spaceRentPayment.save()
    return invoice