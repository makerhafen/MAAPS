import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__user__contract(request, user_id):
    profile = models.Profile.objects.get(id=user_id)
    return HttpResponse(loader.get_template('webif/user/show_contract.html').render({
        "profile": profile
    }, request))
