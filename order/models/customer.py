from django.db import models
import uuid

def get_unique_cusomer_id():
    return 'customer_' + str(uuid.uuid4())

class Customer(models.Model):
    cid = models.BigAutoField(primary_key=True)
    customer_id = models.CharField(default=get_unique_cusomer_id, max_length=250, unique=True)
    credit_card = models.TextField(blank=True, null=True)
    expiry_year = models.CharField(max_length=4,blank=True, null=True)
    expiry_month = models.CharField(max_length=2,blank=True, null=True)
    street_number = models.CharField(max_length=40,blank=True, null=True)
    street_name = models.TextField(blank=True,null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=18, blank=True, null=True)
    first_name = models.CharField(max_length=40,blank=True, null=True)
    last_name = models.CharField(max_length=40, blank=True, null=True)
    email = models.CharField(max_length=40, blank=True, null=True)

    third_party_id = models.CharField(max_length=240, null=True, blank=True)
    third_party_additional_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.customer_id