import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__invoice__create(request, user_id=""):
    invoice = None
    profile = None
    if user_id != "":
        profile = models.Profile.objects.get(id=user_id)

        unpayed_machine_sessions_cnt = models.MachineSessionPayment.objects.filter(~Q(end=None), user=profile.user, invoice=None, transaction=None).count()
        unpayed_materials_cnt = models.MaterialPayment.objects.filter(user=profile.user, invoice=None, transaction=None).count()
        invoice = None
        if unpayed_machine_sessions_cnt > 0 or unpayed_materials_cnt > 0:
            invoice = models.Invoice()
            invoice.user = profile.user
            invoice.save()

    return HttpResponse(loader.get_template('webif/invoice/create.html').render({
        "invoice": invoice,
        "profile": profile
    }, request))
