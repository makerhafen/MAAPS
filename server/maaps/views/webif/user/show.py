import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__user__show(request, user_id):
    profile = models.Profile.objects.get(id=user_id)
    latest_sessions = models.MachineSession.objects.filter(user=profile.user).order_by('-start')[:5]
    latest_material_payments = models.MaterialPayment.objects.filter(user=profile.user).order_by('-created')[:5]
    latest_invoices = models.Invoice.objects.filter(user=profile.user).order_by('-created')[:5]
    return HttpResponse(loader.get_template('webif/user/show.html').render({
        "profile": profile,
        "latest_sessions": latest_sessions,
        "latest_material_payments": latest_material_payments,
        "latest_invoices": latest_invoices,
    }, request))
