from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import requests
from json import dumps, loads
from os import getenv
import os
import google.auth.transport.requests
import google.oauth2.id_token

URL_MAIN = "https://europe-west1-pric-labo.cloudfunctions.net/test"


def main(request):
    auth_req = google.auth.transport.requests.Request()
    token_main = google.oauth2.id_token.fetch_id_token(auth_req, URL_MAIN)
    headers_main = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(token_main)}
    response = requests.post(url=URL_MAIN, data=dumps({"subgroup": key, "voiv": voiv}), headers=headers_main)
    if response.status_code == 200:
        print(f'Function completed!')
    else:
        print(response.text)
    return "Function completed!"


if __name__ == '__main__':
    if getenv('TEMP'):
        request = None
    main(request)