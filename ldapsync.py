import json
import logging
import os
import sys
import requests

from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
from dotenv import load_dotenv
from hubspot import HubSpot
from dateutil import parser
from hubspot.crm.contacts import PublicObjectSearchRequest, ApiException
from utils import check_user
from time import sleep

load_dotenv()

parameters = {
        "username": os.getenv("GRAPHQL_USER"),
        "password": os.getenv("GRAPHQL_PASSWORD")
    }


headers = {
        "Content-Type": "application/json"
        }
auth_token_req = requests.post(os.getenv("GRAPHQL_AUTH_URI"), json=parameters, headers=headers)
if auth_token_req.status_code == 200:
    auth_token = auth_token_req.json()['token']
else:
    logging.error(f"Error: {auth_token_req.status_code}")
    sys.exit(1)

base_dn = os.getenv("LDAP_BASE_DN")

api_client = HubSpot(access_token=os.getenv('HUBSPOT_API_TOKEN'))

hubspot_properties = [
        'firstname',
        'lastname',
        'membership_level',
        'email'
        ]

members = PublicObjectSearchRequest(
    properties=hubspot_properties,
    filter_groups=[
        {
            "filters": [
                {
                    "value": "None",
                    "propertyName": "membership_level",
                    "operator": "NEQ"
                }
            ]
        }
    ], limit=100
)

members = api_client.crm.contacts.search_api.do_search(public_object_search_request=members)

users = []

for member in members.results:
    users.append(check_user(cx_method="graphql", user=member, auth_token=auth_token))


sleep(600)
