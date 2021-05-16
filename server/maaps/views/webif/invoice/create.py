import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect


@staff_member_required
def webif__invoice__create(request, user_id=""):
    invoice = None
    profile = None
    if user_id != "":
        profile = models.Profile.objects.get(id=user_id)
        if request.method == 'POST':
            unpayed_machine_sessions = request.POST.getlist('unpayed_machine_sessions', [])
            unpayed_materials = request.POST.getlist('unpayed_materials', [])
            unpayed_spacerents = request.POST.getlist('unpayed_spacerents', [])
            invoice = models.Invoice()
            invoice.user = profile.user
            invoice.save()
            total_value = 0
            for unpayed_machine_session in unpayed_machine_sessions:
                unpayed_machine_session = models.MachineSessionPayment.objects.get(id=unpayed_machine_session)
                unpayed_machine_session.invoice = invoice
                unpayed_machine_session.save()
                total_value += unpayed_machine_session.price
            for unpayed_material in unpayed_materials:
                unpayed_material = models.MaterialPayment.objects.get(id=unpayed_material)
                unpayed_material.invoice = invoice
                unpayed_material.save()
                total_value += unpayed_material.price
            for unpayed_spacerent in unpayed_spacerents:
                unpayed_spacerent = models.SpaceRentPayment.objects.get(id=unpayed_spacerent)
                unpayed_spacerent.invoice = invoice
                unpayed_spacerent.save()
                total_value += unpayed_spacerent.price
            invoice.value = total_value
            if profile.commercial_account is True:
                invoice.include_tax = True
            invoice.save()

            return redirect('webif__invoice__show', invoice_id=invoice.id)
        else:
            unpayed_machine_sessions = models.MachineSessionPayment.objects.filter(~Q(end=None), user=profile.user, invoice=None, transaction=None)
            unpayed_materials = models.MaterialPayment.objects.filter(user=profile.user, invoice=None, transaction=None)
            unpayed_spacerents = models.SpaceRentPayment.objects.filter(user=profile.user, invoice=None, transaction=None)

            #if unpayed_machine_sessions_cnt > 0 or unpayed_materials_cnt > 0 or unpayed_spacerent_cnt > 0:
                #invoice = models.Invoice()
                #invoice.user = profile.user
                #invoice.save()
            #    pass

    return HttpResponse(loader.get_template('webif/invoice/create.html').render({
        "invoice": invoice,
        "profile": profile,
        "unpayed_machine_sessions": unpayed_machine_sessions,
        "unpayed_materials": unpayed_materials,
        "unpayed_spacerents": unpayed_spacerents,
    }, request))
