import maaps.models as models
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__invoice__list(request):
    invoices = models.Invoice.objects.all()
    return render(request, "webif/invoice/list.html", {'invoices': invoices})
