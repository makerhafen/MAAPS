import maaps.models as models
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def webif__user__list(request):
    profile = models.Profile.objects.all()
    return render(request,"webif/user/list.html",{'profiles':profile})



