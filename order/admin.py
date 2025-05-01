from django.contrib import admin
from .models.customer import Customer
from .models.order import Order
from .models.price import Price

# Register your models here.
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Price)

