import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


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
