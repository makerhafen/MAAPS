import io
import uuid
from django import forms
from django.core.files import File
from django.contrib.auth.models import User
from maaps.models import Profile


class PublicRegisterForm(forms.Form):
    email = forms.EmailField(label="E-Mail-Adresse")
    first_name = forms.CharField(label="Vorname")
    last_name = forms.CharField(label="Nachname")
    company_name = forms.CharField(label="Firma (optional)", required=False)
    street = forms.CharField(label="Straße und Hausnummer (optional)", required=False)
    postalcode = forms.CharField(label="PLZ (optional)", required=False)
    city = forms.CharField(label="Stadt (optional)", required=False)
    
    profile_picture = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.")
        return email

    def save(self):
        first_name = self.cleaned_data["first_name"].strip()
        last_name = self.cleaned_data["last_name"].strip()
        email = self.cleaned_data["email"].strip()

        # Generiere eindeutigen Usernamen
        base_username = f"{first_name.lower()}.{last_name.lower()}".replace(" ", "")
        # Sonderzeichen säubern falls notwendig, unidecode falls verfügbar
        try:
            from unidecode import unidecode
            base_username = unidecode(base_username)
        except ImportError:
            pass

        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            counter += 1
            username = f"{base_username}{counter}"

        user = User()
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.set_password(str(uuid.uuid4()))
        user.save()

        # Das Signal post_save (User__add_profile) legt Profile und Token automatisch an.
        profile = user.profile
        profile.company_name = self.cleaned_data.get("company_name", "")
        profile.street = self.cleaned_data.get("street", "")
        profile.postalcode = self.cleaned_data.get("postalcode", "")
        profile.city = self.cleaned_data.get("city", "")

        if self.profile_picture is not None:
            img_io = io.BytesIO(self.profile_picture)
            profile.profile_picture.save("image.jpg", File(img_io))

        profile.save()
        return user
