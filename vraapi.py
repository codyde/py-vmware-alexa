import requests
import configparser
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable SSL warning

def vra_auth():
    Config = configparser.ConfigParser()
    Config.read("/srv/avss/appdata/etc/config.ini")
    url = Config.get("vraConfig", "url")
    user = Config.get("vraConfig", "user")
    password = Config.get("vraConfig", "password")
    tenant = Config.get("vraConfig", "tenant")
    url = "{}/api/tokens".format(url)
    payload = '{{"username":"{}","password":"{}","tenant":"{}"}}'.format(user, password, tenant)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        }
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    j = response.json()['id']
    auth = "Bearer "+j
    return auth


def vra_build(blueprint):
    Config = configparser.ConfigParser()
    Config.read("/srv/avss/appdata/etc/config.ini")
    url = Config.get("vraConfig", "url")
    varray = {}
    auth = vra_auth()
    vraApiUrl = "{}/catalog-service/api/consumer/entitledCatalogItemViews".format(url)
    vraheaders = {'accept': "application/json", 'authorization': auth}
    tempres = requests.request("GET", vraApiUrl, headers=vraheaders, verify=False)
    for i in tempres.json()['content']:
        p = i['name']
        q = i['catalogItemId']
        varray[p] = q
    vraheaders = {
        'accept': "application/json",
        'authorization': auth
        }
    template = "{}/catalog-service/api/consumer/entitledCatalogItems/{}/requests/template".format(url, varray[blueprint])
    req = "{}/catalog-service/api/consumer/entitledCatalogItems/{}/requests".format(url, varray[blueprint])
    templateJson = requests.request("GET", template, headers=vraheaders, verify=False)
    vraCatDeploy = requests.request("Post", req, headers=vraheaders, data=templateJson, verify=False)
    buildStatus = "a "+blueprint+" Server build has been requested"
    return buildStatus