from django.http import HttpResponse
from django.template import loader
import maaps.models as models
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.utils import timezone


@staff_member_required
def webif__prices(request):
    spaceRentPayment_monthly = models.Price.objects.get(identifier="spaceRentPayment.monthly")
    spaceRentPayment_daily = models.Price.objects.get(identifier="spaceRentPayment.daily")
    machines = models.Machine.objects.filter()

    return HttpResponse(loader.get_template('webif/prices.html').render({
        "spaceRentPayment_monthly" : spaceRentPayment_monthly,
        "spaceRentPayment_daily" : spaceRentPayment_daily,
        "machines" : machines,
    }, request))
