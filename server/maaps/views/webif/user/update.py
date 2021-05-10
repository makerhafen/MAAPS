import maaps.models as models
from django.shortcuts import render
from django.shortcuts import redirect
from .user_form import UserForm
import base64
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__user__update(request, user_id):
    profile = models.Profile.objects.get(id=user_id)
    machines = models.Machine.objects.all()
    form = UserForm(initial={
        'email': profile.user.email,
        'first_name': profile.user.first_name,
        'last_name': profile.user.last_name,
        'company_name': profile.company_name,
        'allow_invoice': profile.allow_invoice,
        'commercial_account': profile.commercial_account,
        'monthly_payment': profile.monthly_payment,
        'street': profile.street,
        'postalcode': profile.postalcode,
        'city': profile.city,
        'birthdate': profile.birthdate,
        'paying_user': profile.paying_user,
    })
    error = None
    if request.method == "POST":
        form = UserForm(request.POST)
        form.profile = profile
        if form.is_valid():
            image_data = request.POST.get('image_data', None)
            allowed_machines = request.POST.getlist('allowed_machines', None)
            form.allowed_machines = allowed_machines
            if image_data is not None and "," in image_data:
                form.profile_picture = base64.b64decode(bytes(image_data.split(",")[-1], 'UTF-8'))
            try:
                form.save()
                return redirect('webif__user__list')
            except Exception as e:
                print("Failed to save form:", e)
                error = "%s" % e
    return render(request, 'webif/user/update.html',
                  {'form': form, 'profile': profile, 'machines': machines, "last_error": error})
