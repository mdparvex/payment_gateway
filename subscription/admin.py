from django.contrib import admin
from rest_framework_api_key.models import APIKey
from .models.payment_history import PaymentHistory
from .models.subscribe_vendor import SubscribeVendor
from .models.subscription_status import SubscriptionStatus

# Register your models here.
# Register your models here.
class SubscribeVendorAdmin(admin.ModelAdmin):
    list_display = ('user_friendly_name', 'vendor_name', 'internal_api_key')

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('internal_api_key',)
        # self.list_display = ('vendor_name', 'internal_api_key')
        form = super(SubscribeVendorAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        """ Given a model instance save it to the database."""
        super().save_model(request, obj, form, change)
        # creating api key
        if not change:
            api_key, key = APIKey.objects.create_key(name=obj.vendor_name)
            obj.internal_api_key = key
            obj.save()
admin.site.register(PaymentHistory)
admin.site.register(SubscribeVendor,SubscribeVendorAdmin)
admin.site.register(SubscriptionStatus)
