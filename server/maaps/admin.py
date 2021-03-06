from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from . import models
from django.urls import reverse
from django.utils.html import format_html


class ProfileInline(admin.StackedInline):
    model = models.Profile
    fk_name = 'user'


class MachineUsersInline(admin.TabularInline):
    model = models.Machine.allowed_users.through
    fk_name = 'user'

class ProfileAdmin(BaseUserAdmin):
    list_display = ("first_name", "last_name", "company_name", "deposit", "email", "is_staff", "allow_postpaid", "paying_user")
    inlines = (ProfileInline, MachineUsersInline)

    def company_name(self, obj):
        return obj.profile.company_name

    def deposit(self, obj):
        return obj.profile.prepaid_deposit

    def allow_postpaid(self, obj):
        return obj.profile.allow_postpaid

    def paying_user(self, obj):
        return obj.profile.paying_user


@admin.register(models.Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "enabled", "can_write", "assigned_to", "identifier")
    list_filter = ( "created", "enabled", "can_write")
    list_display_links = ["id", "assigned_to"]

    def assigned_to(self, obj):
        v = obj.machine
        if v is None:
            v = obj.profile
        if v is None:
            return "Not assigned"
        return v


@admin.register(models.Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "comment", "group_name", "ask_clean", "ask_pay_material", "show_autologout", "price_per_hour", "price_per_usage","tutor_required_count", "tutor_required_once_after_month", "current_session")

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "user", "value", "type", "comment", "link_to_invoice")
    list_filter = ( "type",)

    def user(self, obj):
        return obj.profile.user

    def link_to_invoice(self, transaction):
        link = reverse("admin:maaps_invoice_change", args=[transaction.invoice.id])
        return format_html('<a href="{}"> {}</a>', link, transaction.invoice)

    link_to_invoice.short_description = 'Invoice'


@admin.register(models.MachineSessionPayment)
class MachineSessionPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "machine", "machinesession", "start", "end", "price", "transaction", "invoice")
    list_filter = ("start", "end")
    list_display_links = ["id", "machine", "machinesession"]

    def machine(self, obj):
        try:
            return obj.machinesession.machine
        except:
            return None

@admin.register(models.MachineSession)
class MachineSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "user", "tutor", "paying_user", "start", "end", "rating_clean", "machineSessionPayment")
    list_filter = ( "machine", "start", "end", "rating_clean")
    list_display_links = ["id", "machine", "user", "tutor", "paying_user", "machineSessionPayment"]

    def machine(self, obj):
        return obj.machine

    def paying_user(self, obj):
        if obj.machineSessionPayment is not None:
            return obj.machineSessionPayment.user
        return None


@admin.register(models.MaterialPayment)
class MaterialPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "user", "creator", "price", "transaction", "invoice")
    list_filter = ( "created", )

@admin.register(models.SpaceRentPayment)
class SpaceRentPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "for_user", "created", "start", "end", "price", "type","transaction", "invoice")
    list_filter = ( "created", )

@admin.register(models.SpaceAccessTracking)
class SpaceAccessTrackingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created", "start", "end", "spaceRentPayment")
    list_filter = ("created", "start", "end")


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created", "due", "value", "transaction", "include_tax", "type")
    list_filter = ("created", "include_tax", "type")

@admin.register(models.PrepaidDepositPayment)
class PrepaidDepositPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "user", "for_user", "price", "transaction", "invoice")
    list_filter = ("created",)

admin.site.register(models.Price)
admin.site.unregister(User)
admin.site.register(User, ProfileAdmin)
