import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__invoice__show(request, invoice_id):
    invoice = models.Invoice.objects.get(id=invoice_id)

    invoice_items = []
    for machineSessionPayment in invoice.machineSessionPayments.all():
        invoice_items.append(machineSessionPayment)
    for materialPayment in invoice.materialPayments.all():
        invoice_items.append(materialPayment)
    for spaceRentPayment in invoice.spaceRentPayments.all():
        invoice_items.append(spaceRentPayment)
    invoice_items.sort(key=lambda x: x.created)

    return HttpResponse(loader.get_template('webif/invoice/show.html').render({
        "invoice": invoice,
        "invoice_items": invoice_items
    }, request))
