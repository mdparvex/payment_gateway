from ..base_interface import VendorInterface
import requests


class user_access(VendorInterface):
    # change it to server access token
    api_key = 'api_key'
    # change it to server url
    create_url ='' #This api from your application
    deactivate_url = ''#This api from your application
    reactivate_url = ''#

    def create(self, custom_var=None):
        return '12345678'
        
        # if custom_var is not None and 'custom_key' in custom_var and custom_var['custom_key'] != '':
        #     self.api_key = custom_var['custom_key']
        # data = {}
        # if custom_var is not None and 'first_name' in custom_var and custom_var['first_name'] != '':
        #     data['first_name'] = custom_var['first_name']
        # if custom_var is not None and 'last_name' in custom_var and custom_var['last_name'] != '':
        #     data['last_name'] = custom_var['last_name']
        

        # headers = {'Authorization': 'Api-Key ' + self.api_key}
        # response = requests.post(self.create_url, headers=headers, data=data)
        # if response.status_code == 200:
        #     json_response = response.json()
        #     if json_response['status'] == 1:
        #         return json_response['access_code']
        # else:
        #     return "bad request"

    def deactivate(self, access_code, custom_var=None):
        if custom_var is not None and 'custom_key' in custom_var and custom_var['custom_key'] != '':
            self.api_key = custom_var['custom_key']

        data = {'access_code': access_code}
        data['is_active']='false'

        headers = {'Authorization': 'Api-Key ' + self.api_key}
        response = requests.post(self.deactivate_url, headers=headers, data=data)
        return response.json()

    def reactivate(self, access_code, custom_var=None):
        if custom_var is not None and 'custom_key' in custom_var and custom_var['custom_key'] != '':
            self.api_key = custom_var['custom_key']
        data = {'access_code': access_code}

        data['is_active']='true'


        headers = {'Authorization': 'Api-Key ' + self.api_key}
        response = requests.post(self.reactivate_url, headers=headers, data=data)
