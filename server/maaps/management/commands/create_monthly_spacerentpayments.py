from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
import maaps.models
from django.utils import timezone

class Command(BaseCommand):
    help = 'Monatliche Mietzahlungen generieren, alle 24h per cron aufrufen'

    def handle(self, *args, **options):
        profiles = maaps.models.Profile.objects.filter(monthly_payment=True)
        for profile in profiles:
            try:
                last_spaceRentPayment = maaps.models.SpaceRentPayment.objects.filter(
                                        user=profile.user,
                                        #end__lt=timezone.now() + timedelta(days=7)
                                    ).order_by('-end')[0]
            except: # for users that have no current spacerentpayment, for example during migration
                spaceRentPayment = maaps.models.SpaceRentPayment()
                spaceRentPayment.type = maaps.models.SpaceRentPaymentType.monthly
                price = maaps.models.Price.get(identifier="spaceRentPayment.monthly")
                paying_user_profile = profile
                if profile.paying_user is not None:
                    paying_user_profile = profile.paying_user.profile

                if paying_user_profile.commercial_account:
                    spaceRentPayment.price = price.commercial
                elif paying_user_profile.discount_account:
                    spaceRentPayment.price = price.discount
                else:
                    spaceRentPayment.price = price.default
                spaceRentPayment.start = timezone.now()
                spaceRentPayment.end = timezone.now()+timedelta(days=31)
                spaceRentPayment.user = profile.user
                spaceRentPayment.for_user = profile.user
                spaceRentPayment.save()
                continue
            print(last_spaceRentPayment.end )
            if last_spaceRentPayment.end < timezone.now() + timedelta(days=7):
                print("old")
                print(last_spaceRentPayment)
                new_spaceRentPayment = maaps.models.SpaceRentPayment()
                new_spaceRentPayment.user = profile.user
                new_spaceRentPayment.type = maaps.models.SpaceRentPaymentType.monthly
                new_spaceRentPayment.start = last_spaceRentPayment.end
                new_spaceRentPayment.end = new_spaceRentPayment.start + timedelta(days=31)
                new_spaceRentPayment.save()
                print(last_spaceRentPayment)
        print("foobar")
        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"'))