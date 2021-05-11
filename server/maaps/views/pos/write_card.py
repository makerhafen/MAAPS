from django.http import HttpResponse
from django.template import loader
import maaps.models as models
from django.shortcuts import redirect
from maaps.views.functions.session import get_profile_from_session


def pos__write_card(request):
    admin_profile = get_profile_from_session(request)
    if admin_profile is None:
        return redirect('pos__index')
    if not admin_profile.user.is_staff:  # this page is only allowed by admin
        request.session["profile_id"] = None
        return redirect('pos__index')

    rfid_token = request.POST.get("rfid_token", None)
    token = None
    if rfid_token is not None:
        token = models.Token.objects.get(can_write=True, enabled=True, identifier=rfid_token)
        token.can_write = False
        token.save()

    tokens = models.Token.objects.filter(can_write=True, enabled=True)
    template = loader.get_template('pos/write_card.html')
    return HttpResponse(template.render({
        "tokens": tokens,
        "written_token": token,
    }, request))
