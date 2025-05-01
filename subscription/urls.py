from django.urls import path
from .views.subscription_view import *

urlpatterns = [
    path('payment/initiet/', subscription_initiation),
    path('webhook', webhook_vendor)
]
