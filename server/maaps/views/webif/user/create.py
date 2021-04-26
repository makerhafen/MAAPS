from django.shortcuts import render
from django.shortcuts import redirect
from .user_form import UserForm
import base64
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def webif__user__create(request):
    error = None
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            image_data = request.POST.get('image_data', None)
            if image_data is not None and "," in image_data:
                form.profile_picture = base64.b64decode(bytes(image_data.split(",")[-1], 'UTF-8'))
            try:
                form.save()
                return redirect('webif__user__list')
            except Exception as e:
                print("Failed to save form:", e)
                error = "%s" % e
    else:
        form = UserForm()
    return render(request, 'webif/user/create.html', {'form': form, "last_error": error})
