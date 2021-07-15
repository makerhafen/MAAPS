import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from maaps.views.functions.payment import create_invoice

@staff_member_required
def webif__invoice__create(request, user_id=""):
    invoice = None
    profile = None
    unpayed_machine_sessions = None
    unpayed_materials = None
    unpayed_spacerents = None
    spacerents = None
    if user_id != "":
        profile = models.Profile.objects.get(id=user_id)
        if profile.allow_postpaid is True:
            if request.method == 'POST':
                unpayed_machine_sessions = request.POST.getlist('unpayed_machine_sessions', [])
                unpayed_materials = request.POST.getlist('unpayed_materials', [])
                unpayed_spacerents = request.POST.getlist('unpayed_spacerents', [])

                unpayed_machine_sessions = [models.MachineSessionPayment.objects.get(id=unpayed_machine_session) for unpayed_machine_session in unpayed_machine_sessions]
                unpayed_materials = [models.MaterialPayment.objects.get(id=unpayed_material) for unpayed_material in unpayed_materials]
                unpayed_spacerents = [ models.SpaceRentPayment.objects.get(id=unpayed_spacerent)  for unpayed_spacerent in unpayed_spacerents]
                all = unpayed_machine_sessions + unpayed_materials + unpayed_spacerents

                total_value = sum([obj.price for obj in all])
                invoice = create_invoice(profile, total_value, models.InvoiceType.invoice, None)
                for obj in all:
                    obj.invoice = invoice
                    obj.save()

                return redirect('webif__invoice__show', invoice_id=invoice.id)
            else:
                unpayed_machine_sessions = models.MachineSessionPayment.objects.filter(~Q(end=None), user=profile.user, invoice=None, transaction=None)
                unpayed_materials = models.MaterialPayment.objects.filter(user=profile.user, invoice=None, transaction=None)
                unpayed_spacerents = models.SpaceRentPayment.objects.filter(user=profile.user, invoice=None, transaction=None)

            return HttpResponse(loader.get_template('webif/invoice/create.html').render({
                "invoice": invoice,
                "profile": profile,
                "unpayed_machine_sessions": unpayed_machine_sessions,
                "unpayed_materials": unpayed_materials,
                "unpayed_spacerents": unpayed_spacerents,
            }, request))
        else:
            if request.method == 'POST':
                spaceRentPayments = request.POST.getlist('spaceRentPayments', [])
                prepaidDepositPayments = request.POST.getlist('prepaidDepositPayments', [])
                invoice = models.Invoice()
                invoice.user = profile.user
                invoice.created = timezone.now()
                invoice.due = timezone.now() + timedelta(days=14)
                invoice.type = models.InvoiceType.invoice
                invoice.save()
                total_value = 0
                for spaceRentPayment in spaceRentPayments:
                    spaceRentPayment = models.SpaceRentPayment.objects.get(id=spaceRentPayment)
                    spaceRentPayment.invoice = invoice
                    spaceRentPayment.save()
                    total_value += spaceRentPayment.price
                for prepaidDepositPayment in prepaidDepositPayments:
                    prepaidDepositPayment = models.PrepaidDepositPayment.objects.get(id=prepaidDepositPayment)
                    prepaidDepositPayment.invoice = invoice
                    prepaidDepositPayment.save()
                    total_value += prepaidDepositPayment.price
                invoice.value = total_value
                if profile.commercial_account is True:
                    invoice.include_tax = True
                invoice.save()
                return redirect('webif__invoice__show', invoice_id=invoice.id)
            else:
                spaceRentPayments = models.SpaceRentPayment.objects.filter(user=profile.user, invoice=None)
                prepaidDepositPayments = models.PrepaidDepositPayment.objects.filter(user=profile.user, invoice=None)

            return HttpResponse(loader.get_template('webif/invoice/create.html').render({
                "invoice": invoice,
                "profile": profile,
                "spaceRentPayments": spaceRentPayments,
                "prepaidDepositPayments": prepaidDepositPayments,

            }, request))

