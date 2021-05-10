import maaps.models as models
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect

from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__user__create_new_card(request, user_id):
    profile = models.Profile.objects.get(id=user_id)
    tokens = models.Token.objects.filter(enabled=True, profile=profile)
    for token in tokens:
        token.enabled = False
        token.save()

    new_token = models.Token()
    new_token.profile = profile
    new_token.enabled = True
    new_token.can_write = True
    new_token.save()
    return redirect('webif__user__show', user_id=profile.id)
