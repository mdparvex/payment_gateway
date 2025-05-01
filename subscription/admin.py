from django.contrib import admin
from .models.payment_history import PaymentHistory
from .models.subscribe_vendor import SubscribeVendor
from .models.subscription_status import SubscriptionStatus

# Register your models here.
admin.site.register(PaymentHistory)
admin.site.register(SubscribeVendor)
admin.site.register(SubscriptionStatus)
