import base64
from django.shortcuts import render, redirect
from .register_form import PublicRegisterForm


def webif__user__register(request):
    error = None
    if request.method == "POST":
        form = PublicRegisterForm(request.POST)
        if form.is_valid():
            image_data = request.POST.get('image_data', None)
            if image_data is not None and "," in image_data:
                try:
                    form.profile_picture = base64.b64decode(bytes(image_data.split(",")[-1], 'UTF-8'))
                except Exception as e:
                    print("Failed to decode profile picture:", e)

            try:
                user = form.save()
                return render(request, 'webif/user/register_success.html', {'registered_user': user})
            except Exception as e:
                print("Failed to save registration form:", e)
                error = f"{e}"
        else:
            print("Registration form not valid")
    else:
        form = PublicRegisterForm()

    return render(request, 'webif/user/register.html', {
        'form': form,
        'last_error': error
    })
