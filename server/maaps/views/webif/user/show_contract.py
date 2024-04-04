import datetime
import random

import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import string

@staff_member_required
def webif__user__contract(request, user_id):

    profile = models.Profile.objects.get(id=user_id)
    price_daily   = models.Price.objects.get(identifier="spaceRentPayment.daily")
    price_monthly = models.Price.objects.get(identifier="spaceRentPayment.monthly")

    return HttpResponse(loader.get_template('webif/user/show_contract.html').render({
        "profile": profile,
        "price_daily": price_daily,
        "price_monthly": price_monthly
    }, request))

@staff_member_required
def webif__user__contract_sepa(request, user_id):
    mref = "MH-"
    mref += "%s" % datetime.datetime.now().year
    mref += "-"
    mref += "".join(["%s"%random.randint(0,9) for _ in range(3)])
    mref += "-"
    mref += "".join(random.sample(string.ascii_lowercase, 3))

    profile = models.Profile.objects.get(id=user_id)

    return HttpResponse(loader.get_template('webif/contract.html').render({"mref": mref, "profile": profile}, request))

@staff_member_required
def webif__user__contract_paypal(request, user_id):
    profile = models.Profile.objects.get(id=user_id)

    return HttpResponse(loader.get_template('webif/contract_paypal.html').render({"profile": profile}, request))
