from django.http import HttpResponse
from django.template import loader
import maaps.models as models

def pos__write_card(request):
    rfid_token = request.POST.get("rfid_token", None)
    token = None
    if rfid_token is not None:
        token = models.Token.objects.get(can_write=True, identifier = rfid_token)
        token.can_write = False
        token.save()

    tokens = models.Token.objects.filter(can_write=True)
    template = loader.get_template('pos/write_card.html')
    return HttpResponse(template.render({
        "tokens": tokens,
        "written_token": token,
    }, request))
