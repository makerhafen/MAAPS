import io
import uuid

from django import forms
from django.core.files import File

from maaps.models import Profile, User, Machine


class UserForm(forms.Form):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Vorname")
    last_name = forms.CharField(label="Nachname")
    company_name = forms.CharField(label="Firma", required=False)
    street = forms.CharField(label="Strasse und Hausnummer", required=False)
    postalcode = forms.CharField(label="PLZ", required=False)
    city = forms.CharField(label="Stadt", required=False)
    allow_invoice = forms.BooleanField(label="Bezahlung auf Rechnung", required=False)
    commercial_account = forms.BooleanField(label="Kommerzieller Account", required=False)
    monthly_payment = forms.BooleanField(label="Monatlich zahlen", required=False)
    birthdate = forms.DateField(label="Geburtsdatum (Pflicht bei Minderjährigen!)", required=False)
    paying_user = forms.ModelChoiceField(queryset=Profile.objects.all(), required=False, label="Ein anderer Benutzer zahlt für diesen Benutzer")

    profile_picture = None

    class Meta:
        model = Profile
        fields = ("email", "first_name", "last_name", "company_name", "allow_invoice", "commercial_account", "paying_user", "city")

    def save(self, commit=True):
        try:
            user = self.profile.user
        except:
            user = User()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if user.username == "":
            user.username = "%s.%s" % (user.first_name.lower(), user.last_name.lower())
        user.email = self.cleaned_data["email"]
        if user.has_usable_password() is False:
            user.set_password('%s' % uuid.uuid4())
        user.save()
        if self.profile_picture is not None:
            img_io = io.BytesIO(self.profile_picture)
            user.profile.profile_picture.save("image.jpg", File(img_io))
        user.profile.allow_invoice = self.cleaned_data["allow_invoice"]
        user.profile.company_name = self.cleaned_data["company_name"]
        user.profile.paying_user = self.cleaned_data["paying_user"]
        user.profile.commercial_account = self.cleaned_data["commercial_account"]
        user.profile.monthly_payment = self.cleaned_data["monthly_payment"]
        user.profile.street = self.cleaned_data["street"]
        user.profile.postalcode = self.cleaned_data["postalcode"]
        user.profile.city = self.cleaned_data["city"]
        user.profile.birthdate = self.cleaned_data["birthdate"]
        user.profile.save()
        allowed_machines = [int(allowed_machine) for allowed_machine in self.allowed_machines]
        all_machines = Machine.objects.all()
        for machine in all_machines:
            if machine.id in allowed_machines and user not in machine.allowed_users.all():
                machine.allowed_users.add(user)
                machine.save()
            if machine.id not in allowed_machines and user in machine.allowed_users.all():
                machine.allowed_users.remove(user)
                machine.save()

        return user
