from dotenv import load_dotenv
import os
import base64
from requests import post
import json

load_dotenv('.env')
# client_id = os.getenv('client_id')
# client_secret = os.getenv('client_secret')

client_id = '45529491a7f54ebe85672f16205f93e5'
client_secret = '4567d8ad07ac41c68ee8dca335e680af'

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    
    return token

def get_auth_header(token):
    return{"Authorization":"Bearer " + token}