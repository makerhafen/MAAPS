from django.shortcuts import render
from django.shortcuts import redirect
from .user_form import UserForm
import base64
from django.contrib.admin.views.decorators import staff_member_required
import maaps.models as models


@staff_member_required
def webif__user__create(request):
    error = None
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            image_data = request.POST.get('image_data', None)
            allowed_machines = request.POST.getlist('allowed_machines', None)
            form.allowed_machines = allowed_machines
            if image_data is not None and "," in image_data:
                form.profile_picture = base64.b64decode(bytes(image_data.split(",")[-1], 'UTF-8'))
            try:
                user = form.save()
                return redirect('webif__user__show',user_id=user.profile.id)
            except Exception as e:
                print("Failed to save form:", e)
                error = "%s" % e
        else:
            print("form not valid")
    else:
        form = UserForm()
    machines = models.Machine.objects.all()
    return render(request, 'webif/user/create.html', {'form': form, "last_error": error, "machines": machines})
