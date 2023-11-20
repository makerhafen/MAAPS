import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import random
import datetime
import string
def webif__contract(request):
    mref = "MH-"
    mref += "%s" % datetime.datetime.now().year
    mref += "-"
    mref += "".join(["%s"%random.randint(0,9) for _ in range(3)])
    mref += "-"
    mref += "".join(random.sample(string.ascii_lowercase, 3))
    return HttpResponse(loader.get_template('webif/contract.html').render({"mref": mref}, request))

def webif__contract_paypal(request):
    return HttpResponse(loader.get_template('webif/contract_paypal.html').render({}, request))
