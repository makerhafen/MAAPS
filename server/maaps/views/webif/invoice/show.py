import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__invoice__show(request, invoice_id):
    invoice = models.Invoice.objects.get(id=invoice_id)

    return HttpResponse(loader.get_template('webif/invoice/show.html').render({
        "invoice": invoice
    }, request))
