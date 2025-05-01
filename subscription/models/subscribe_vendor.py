from django.db import models
from rest_framework import serializers


class SubscribeVendor(models.Model):
    subscribe_vendor_id = models.BigAutoField(primary_key=True)
    internal_api_key = models.CharField(max_length=255)
    user_friendly_name = models.CharField(max_length=100, default="", blank=True)
    vendor_name = models.CharField(max_length=100)
    custom_arg = models.TextField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    vendor_redirect_url = models.TextField(null=True, blank=True)
    vendor_cancel_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.vendor_name)


class SubscribeVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribeVendor
        fields = ('user_friendly_name', 'vendor_name', 'internal_api_key')
