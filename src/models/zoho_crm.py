from decouple import config
from urllib import parse
from requests import post, put, get, delete
import json
import datetime
import os

logging = config('Logging', cast=bool)


class Authorization():
    def __init__(self, *,
                 scope: str = 'ZohoCRM.users.all,ZohoCRM.org.all,ZohoCRM.settings.all,ZohoCRM.modules.all',
                 response_type: str = 'code',
                 access_type: str = 'offline',
                 grant_token: str = None):
        self.testing = config('Local_Development', cast=bool)
        self.access_token = None
        self.client_id = config('Zoho_Client_ID', cast=str)
        self.client_secret = config('Zoho_Client_Secret', cast=str)
        self.redirect_uri = config('Zoho_Redirect_URI', cast=str)
        self.scope = scope
        self.response_type = response_type
        self.access_type = access_type
        self.grant_token = grant_token
        self.refresh_token = None
        self.token_type = None
        self.access_token_exp = None
        if logging: print("Zoho Authorization object initialized")

    def auth_url(self):
        if logging: print("Zoho Authorization.auth_url started")

        url = 'https://accounts.zoho.com/oauth/v2/auth?scope={scope}&client_id={client_id}&response_type={response}&access_type={access}&redirect_uri={redirect}'.format(
            scope=self.scope,
            client_id=self.client_id,
            response=self.response_type,
            access=self.access_type,
            redirect=self.redirect_uri
        )

        print('Authorization URL\n{}'.format(url))

        if logging: print("Zoho Authorization.auth_url ended")
        return url

    def oauth2callback(self, grant_token):
        if logging: print("Zoho Authorization.oauth2callback started")

        self.grant_token = grant_token if not self.testing else input("Enter generated grant token:")
        url = 'https://accounts.zoho.com/oauth/v2/token?code={grant_token}&redirect_uri={redirect_uri}&client_id={client_id}&client_secret={client_secret}&grant_type=authorization_code'.format(
            grant_token=self.grant_token,
            redirect_uri=self.redirect_uri,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        response = post(url)
        if logging: print("Zoho Authorization.oauth2callback response.text:\n {}".format(json.loads(response.text)))

        self.strp_tokens(response)

        if logging: print("Zoho Authorization.oauth2callback ended")
        return "Refresh Token: {}".format(self.refresh_token)

    def strp_tokens(self, response_json):
        if logging: print('Zoho Authorization.strp_tokens started')

        self.access_token = response_json['access_token']
        if "refresh_token" in response_json: self.refresh_token = response_json['refresh_token']
        self.token_type = response_json['token_type']
        self.access_token_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=59)

        os.environ["Access_Token"] = self.access_token
        os.environ["Refresh_Token"] = self.refresh_token
        os.environ["Access_Token_Exp"] = self.access_token_exp.strftime('%m-%d-%YT%H:%M:%S')

        if logging: print('Zoho Authorization.strp_tokens ended')

    def get_token(self):
        if logging: print('Zoho Authorization.get_token started')

        self.access_token = config("Access_Token", cast=str)
        self.access_token_exp = datetime.datetime.strptime(config("Access_Token_Exp", cast=str),'%m-%d-%YT%H:%M:%S')
        self.refresh_token = config("Refresh_Token", cast=str)

        if self.access_token_exp < datetime.datetime.utcnow():
            if logging: print('Zoho Authorization getting new access token')

            url = "https://accounts.zoho.com/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token".format(
                refresh_token=self.refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            response = post(url)
            response_json = response.json()
            self.strp_tokens(response_json)

        if logging: print('Zoho Authorization.get_token ended')
        return self.access_token


class Record():
    def __init__(self, module: str):
        self.module = module
        self.auth_header = {"Authorization": "Zoho-oauthtoken {}".format(Authorization().get_token())}
        self.logged_name = "Zoho {} Record".format(self.module) if logging else None

        if logging: print("{} object initialized".format(self.logged_name))

    def list_records(self):
        pass

    def bulk_update(self, data: list):
        if logging: print("{} bulk_update started".format(self.logged_name))

        url = "https://www.zohoapis.com/crm/v2/{}".format(self.module)
        body = {"data": data}
        response = put(url, headers=self.auth_header, json=body)

        if logging: print(
            "{name} bulk_update response\n{r}\n{name} bulk_update ended".format(name=self.logged_name, r=response))
        return response

    def bulk_insert(self):
        pass

    def bulk_upsert(self):
        pass

    def bulk_delete(self):
        pass

    def list_deleted(self):
        pass

    def search(self, *,
               criteria: str = None,
               email: str = None,
               phone: str = None,
               word: str = None,
               page: int = None,
               per_page: int = None):

        if logging: print("{} search started".format(self.logged_name))

        url = "https://www.zohoapis.com/crm/v2/{}/search".format(self.module)
        params = {}
        if criteria: params.update({"criteria": criteria})
        if email: params.update({"email": email})
        if phone: params.update({"phone": phone})
        if word: params.update({"word": word})
        if page: params.update({"page": page})
        if per_page: params.update({"per_page": per_page})
        try:
            response = get(url, headers=self.auth_header, params=params)
            records = response.json()['data']
        except:
            records=None

        if logging: print("{} search ended".format(self.logged_name))
        return records

    def get_record(self, id: str):
        if logging: print("{} get_record started".format(self.logged_name))

        url = 'https://www.zohoapis.com/crm/v2/{}/{}'.format(self.module, id)
        response = get(url, headers=self.auth_header)
        record = response.json()['data'][0]

        if logging: print(
            "{name} get_record response\n{r}\n{name} get_record ended".format(name=self.logged_name, r=response))
        return record

    def insert(self):
        pass

    def update(self, id: str, data: list):
        if logging: print("{} update started".format(self.logged_name))

        url = "https://www.zohoapis.com/crm/v2/{}/{}".format(self.module, id)
        body = {"data": data}
        response = put(url, headers=self.auth_header, json=body)

        if logging: print("{name} update response\n{r}\n{name} update ended".format(name=self.logged_name, r=response))
        return response

    def delete(self):
        pass

    def convert(self):
        pass


class Users():
    def __init__(self, id: str = None):
        self.id = id
        self.auth_header = {"Authorization": "Zoho-oauthtoken {}".format(Authorization().get_token())}
        self.logged_name = "Zoho Users" if logging else None

        if logging: print("{} object initialized".format(self.logged_name))

    def list_users(self, type: str) -> list:
        url = "https://www.zohoapis.com/crm/v2/users"
        response = get(url, params={'type': type}, headers=self.auth_header)
        users = response.json()['users']
        return users

    def get_user(self):
        url = "https://www.zohoapis.com/crm/v2/users/{user_id}".format(user_id=self.id)
        response = get(url, headers=self.auth_header)
        return response.json()['users'][0]
