from django.shortcuts import redirect
import maaps.models as models
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def webif__user__delete(request, id):
    profile = models.Profile.objects.get(id=id)
    try:
        profile.delete()
    except:
        pass
    return redirect('webif__user__list')