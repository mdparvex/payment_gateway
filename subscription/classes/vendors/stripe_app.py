from ..base_interface import VendorInterface
from order.models.order import Order
from subscription.models.subscribe_vendor import SubscribeVendor
from subscription.models.subscription_status import SubscriptionStatus
from subscription.models.payment_history import PaymentHistory
from order.models.customer import Customer
from order.models.price import Price
import datetime
import json
import importlib
import stripe

def create_payment_history(store_type, order, amount, date, status, event_type=""):
    PaymentHistory.objects.create(store_type=store_type, order=order, amount=amount, date=date, status=status,
                                  event_type=event_type)
    return

class stripe_app(VendorInterface):

    def create(self, custom_var=None):
        pass

    def verify_card(self, data, vendor_obj):
        secret_key = vendor_obj.config_data["secret_key"]
        print(f'secret key: {secret_key}')
        credit_card = None
        expiry_year = None
        expiry_month = None
        street_number = None
        if 'street_number' in data['card']:
            street_number = data['card']['street_number']

        street_name = None
        if 'street_name' in data['card']:
            street_name = data['card']['street_name']

        country_code = None
        if 'country' in data['card']:
            country_code = data['card']['country']

        postal_code = None
        if 'postal' in data['card']:
            postal_code = data['card']['postal']

        phone_number = None
        if 'phone' in data['card']:
            phone_number = data['card']['phone']

        first_name = None
        if 'first_name' in data['card']:
            first_name = data['card']['first_name']

        last_name = None
        if 'last_name' in data['card']:
            last_name = data['card']['last_name']

        email = None
        if 'email' in data['card']:
            email = data['card']['email']
        print('inside function')
        try:
            customer = Customer.objects.get(credit_card=credit_card, expiry_year=expiry_year,
                                            expiry_month=expiry_month, street_number=street_number,
                                            street_name=street_name, country_code=country_code,
                                            postal_code=postal_code, phone_number=phone_number, first_name=first_name,
                                            last_name=last_name, email=email)
        except Customer.DoesNotExist:
            customer = Customer(credit_card=credit_card, expiry_year=expiry_year,
                                expiry_month=expiry_month, street_number=street_number,
                                street_name=street_name, country_code=country_code,
                                postal_code=postal_code, phone_number=phone_number, first_name=first_name,
                                last_name=last_name, email=email)
            customer.save()

        
            stripe.api_key = secret_key
            stripe_customer = stripe.Customer.create(
                email=email,
                name=first_name + " " + last_name,
                metadata={"customer_id": customer.customer_id, 'vendor_id': vendor_obj.subscribe_vendor_id}
            )
            print(f'stripe: {stripe_customer}')
            customer.third_party_id = stripe_customer['id']
            customer.third_party_additional_data = stripe_customer

        customer.save()

        return {"customer_id": customer.customer_id}
    

    def purchase(self, data, vendor_obj):
        if 'customer_id' not in data:
            raise Exception("Invalid Customer")
        if 'price_id' not in data:
            raise Exception("Invalid Price Id")
        
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
           
            order = Order.objects.get(status=True,customer_id=customer)
            
            try:  
                existing_sub = SubscriptionStatus.objects.get(subscription_id=order.order_id)
                if not order.cancel_requested:
                    raise Exception("Order already Exists")
            except SubscriptionStatus.DoesNotExist:
                order.status = False
                order.save()

        except Order.DoesNotExist:
            pass
        except Customer.DoesNotExist:
            raise Exception('Invalid Customer')
        
        prices = data['price_id']
        pid = prices['id']
        
        try:
            priceObj = Price.objects.get(price_id=pid)
        except Price.DoesNotExist:
            raise Exception("Invalid Price Id")
        stripe.api_key = vendor_obj.config_data["secret_key"]
        stripe_items_to_purchase, coupon_code = [{'price': priceObj.custom_price_id['price_id']}], {}

        total_amount = priceObj.price_point
        

        order = Order(customer_id=customer,order_price=priceObj, total_amount_charged=total_amount, plan_type=priceObj.plan_duration_days)
        order.save()

        primary_subscription = stripe.Subscription.create(
            customer=customer.third_party_id,
            items=stripe_items_to_purchase,
            payment_settings={'save_default_payment_method': 'on_subscription'},
            trial_period_days=7,
            metadata={"order_id": order.order_id,
                        "customer_id": customer.customer_id,
                        'vendor_id': vendor_obj.subscribe_vendor_id}

        )
        print(primary_subscription)
        #client_secret = primary_subscription['latest_invoice']['payment_intent']['client_secret']
        order.order_data = primary_subscription
        order.customer_order_id = primary_subscription['id']

        sub_status = primary_subscription['status'].lower()
        if 'status' in primary_subscription and sub_status in ['approval_pending', 'active', 'incomplete', 'trialing']:
            order.status = True
        else:
            order.status = False

        order.save()
        print("Primary Subscription", primary_subscription)

        json_response = {
            'status': True,
            'receipt_id': order.order_id,
            'transaction_number': order.customer_order_id,
            'auth_code': '',
            'next_recur_date': ''
        }
        return json_response
    
    def complete_purchase(self, data, vendor_obj):
        if 'order_id' not in data:
            raise Exception("Requires Order")

        try:
            order_info = Order.objects.get(order_id=data['order_id'])
        except Order.DoesNotExist:
            raise Exception("Order Does not exist")

        order_prices = order_info.order_price

        try:
            sub_status = SubscriptionStatus.objects.get(subscription_id=order_info.order_id)
            # subscription already exists
            response = {
                'message': "Already Enabled",
                'login_access_code': sub_status.login_access_code,
                'order_id': sub_status.subscription_id,
                'subscription_status': sub_status.subscription_status
            }
            return response
        except SubscriptionStatus.DoesNotExist:
            pass

        custom_vendor_arg = json.loads(vendor_obj.custom_arg)
        login_access_code = ''
        if 'third_party_lib' in custom_vendor_arg:
            vendor_class_name = custom_vendor_arg['third_party_lib']
            try:
                module = importlib.import_module("subscription.classes.vendors." + vendor_class_name)
            except:
                return {"message": "Invalid Third Party Lib"}

            vendor_class = getattr(module, vendor_class_name)
            custom_vendor_obj = vendor_class()
            first_name = "learningHub"

            if order_info.customer_id.first_name != "" and order_info.customer_id.first_name is not None:
                first_name = order_info.customer_id.first_name
            arg = {}
            if order_info.customer_id.last_name != "" and order_info.customer_id.last_name is not None:
                arg['last_name'] = order_info.customer_id.last_name
            if 'custom_key' in custom_vendor_arg:
                arg['custom_key'] = custom_vendor_arg['custom_key']
            arg['first_name'] = first_name

            '''
            Same user repurchases again
            '''
            if 'login_access_code' in data:
                # reactivate current user
                try:
                    sub_status = SubscriptionStatus.objects.get(login_access_code=data['login_access_code'])
                    sub_status.subscription_id = order_info.order_id
                    sub_status.subscription_status = order_info.status
                    sub_status.subscribe_vendor = vendor_obj
                    sub_status.save()
                    reactivate = custom_vendor_obj.reactivate(sub_status.login_access_code, arg)
                    response = {
                        'message': "Completed Purchase",
                        'login_access_code': sub_status.login_access_code,
                        'order_id': sub_status.subscription_id,
                        'subscription_status': sub_status.subscription_status,
                        "resp_status": reactivate
                    }
                    return response
                except SubscriptionStatus.DoesNotExist:
                    pass
            login_access_code = custom_vendor_obj.create(arg)
            print(login_access_code)

        sub_status = SubscriptionStatus(login_access_code=login_access_code,
                                        subscription_id=order_info.order_id,
                                        subscription_status=order_info.status,
                                        subscribe_vendor=vendor_obj)
        sub_status.save()

        response = {
            'message': "Completed Purchase",
            'login_access_code': sub_status.login_access_code,
            'order_id': sub_status.subscription_id,
            'subscription_status': sub_status.subscription_status
        }
        return response
    
    def full_cancellation(self, order_info,vendor_obj):
        
        if "secret_key" in vendor_obj.config_data:
            secret_key = vendor_obj.config_data["secret_key"]
        else:
            raise Exception("Invalid Config in Campaign")
        stripe.api_key = secret_key

        json_response = stripe.Subscription.modify(
            order_info.customer_order_id,
            cancel_at_period_end=True
        )
        print(json_response)
        # order_info.order_data = json_response
        order_info.cancel_requested = True
        cancellate_date = order_info.get_future_cancel_date()
        order_info.cancel_date = cancellate_date
        order_info.save()

        return True
    
    def cancel(self, data, vendor_obj):
        if 'order_id' not in data:
            raise Exception("Require order id")
        if 'price_id' not in data:
            raise Exception("Requires price id")

        try:
            order_info = Order.objects.get(order_id=data['order_id'])
        except Order.DoesNotExist:
            raise Exception("Order Does not exist")

        try:
            sub_status = SubscriptionStatus.objects.get(subscription_id=order_info.order_id)
            sub_vendor = sub_status.subscribe_vendor
            if sub_vendor != vendor_obj:
                try:
                    module = importlib.import_module("subscription.classes.vendors." + sub_vendor.vendor_name)
                except:
                    raise Exception("Invalid Vendor")

                vendor_class = getattr(module, sub_vendor.vendor_name)
                vendor_obj = vendor_class()
                return vendor_obj.custom(data=data, vendor_obj=sub_vendor)
        except SubscriptionStatus.DoesNotExist:
            pass

        subscription_status = self.full_cancellation(order_info,vendor_obj)
        sub_status.subscription_status=False
        sub_status.save()

        return {'message': 'successfully cancelled'}

    def custom(self, *arg, **kwargs):
        if 'data' not in kwargs:
            raise Exception("Missing Data")

        if 'vendor_obj' not in kwargs:
            raise Exception("Missing Vendor")

        data = kwargs['data']
        vendor_obj = kwargs['vendor_obj']
        if 'type' not in data:
            raise Exception("Missing Type")

        if data['type'] == 'card_verification':
            return self.verify_card(data, vendor_obj)
        elif data['type'] == 'purchase':
            return self.purchase(data, vendor_obj)
        elif data['type'] == 'complete_purchase':
            return self.complete_purchase(data, vendor_obj)
        elif data['type'] == 'cancel':
            return self.cancel(data, vendor_obj)

    def webhook(self, *arg, **kwargs):
        if 'request' not in kwargs:
            raise Exception("Request Missing")
        if 'vendor' not in kwargs:
            raise Exception("Require Vendor")
        vendor_obj = kwargs['vendor']
        request = kwargs['request']

        store_type = 1
        amount = 0
        
        payload = request.body.decode('utf-8')
        signature = request.headers.get('stripe-signature')
        request_data = request.data
        data = request_data['data']
        event_type = request_data['type']
        if event_type in ['invoice.paid', 'invoice.payment_succeeded']:
            order_id = data['object']['lines']['data'][0]['metadata']['order_id']
        else:
            order_id = data['object']['metadata']['order_id']
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            raise Exception("Order Does Not Exist")

        if 'webhook_secret' not in order.campaign.config_data:
            raise Exception("Webhook secret missing")
        webhook_secret = SubscribeVendor.config_data['webhook_secret']

        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=signature, secret=webhook_secret)

        data = event['data']
        if data['object'] and data['object']['amount_paid']:
            # amount = data['object']['amount_paid']
            try:
                amount = int(data['object']['amount_paid']) / 100
            except:
                amount = order.order_price.price_point
        else:
            if order.order_price:
                amount = order.order_price.price_point
            else:
                amount = 0
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
        if event_type in ['customer.subscription.deleted', 'BILLING.SUBSCRIPTION.CANCELLED']:
            if order.cancel_requested == False:
                order.cancel_requested = True
                cancellate_date = order.get_future_cancel_date()
                order.cancel_date = cancellate_date
                amount = 0
                order.save()
                # subscription_status = SubscriptionStatus.objects.get(subscription_id=order.order_id)
                # subscription_status.subscription_status = False
                # order.status = False
                # subscription_status.save()
                # order.save()
                # self.notify_deactivate_to_third_party(subscription_status.login_access_code, vendor_obj,
                #                                     False, False)
                
                create_payment_history(
                    store_type, order, amount, datetime.now(), 3, event_type)
                # store_type,order,amount,date,status
        elif event_type in ['customer.subscription.paused', 'invoice.payment_action_required', 'invoice.payment_failed',
                            'BILLING.SUBSCRIPTION.PAYMENT.FAILED', 'BILLING.SUBSCRIPTION.EXPIRED',
                            'BILLING.SUBSCRIPTION.SUSPENDED']:
            subscription_status = SubscriptionStatus.objects.get(subscription_id=order.order_id)
            subscription_status.subscription_status = False
            subscription_status.save()
            amount = 0
            # shohel added
            create_payment_history(
                store_type, order, amount, datetime.now(), 2, event_type)
        elif event_type in ['customer.subscription.resumed', 'BILLING.SUBSCRIPTION.ACTIVATED',
                            'BILLING.SUBSCRIPTION.RE-ACTIVATED']:
            subscription_status = SubscriptionStatus.objects.get(subscription_id=order.order_id)
            subscription_status.subscription_status = True
            subscription_status.save()
            amount = 0
            # shohel added
            create_payment_history(
                store_type, order, amount, datetime.now(), 1, event_type)
        elif event_type in ['invoice.paid', 'PAYMENT.SALE.COMPLETED']:
            subscription_status = SubscriptionStatus.objects.get(
                subscription_id=order.order_id)
            subscription_status.subscription_status = True
            subscription_status.save()
            # shohel added
            create_payment_history(
                store_type, order, amount, datetime.now(), 1, event_type)