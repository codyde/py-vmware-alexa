import requests
import configparser
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable SSL warning

def vra_auth():
    config = configparser.ConfigParser()
    config.read("c:\\stuff\\py-vmware-alexa\\etc\\config.txt")
    user = config.get("vraConfig", "user")
    password = config.get("vraConfig", "password")
    tenant = config.get("vraConfig", "tenant")
    url = "https://hlcloud.humblelab.com/identity/api/tokens"
    payload = '{{"username":"{}","password":"{}","tenant":"{}"}}'.format(user,password,tenant)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        }
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    j = response.json()['id']
    auth = "Bearer "+j
    return auth


def vra_build(blueprint):
    varray = {}
    auth = vra_auth()
    vraApiUrl = "https://hlcloud.humblelab.com/catalog-service/api/consumer/entitledCatalogItemViews"
    vraheaders = {'accept': "application/json", 'authorization': auth}
    tempres = requests.request("GET", vraApiUrl, headers=vraheaders, verify=False)
    template = "https://hlcloud.humblelab.com/catalog-service/api/consumer/entitledCatalogItems/{}/requests/template"
    req = "https://hlcloud.humblelab.com/catalog-service/api/consumer/entitledCatalogItems/{}/requests"
    for i in tempres.json()['content']:
        p = i['name']
        q = i['catalogItemId']
        varray[p] = q
    vraheaders = {
        'accept': "application/json",
        'authorization': auth
        }
    template = template.format(varray[blueprint])
    req = req.format(varray[blueprint])
    templateJson = requests.request("GET", template, headers=vraheaders, verify=False)
    vraCatDeploy = requests.request("Post", req, headers=vraheaders, data=templateJson, verify=False)
    buildStatus = "a "+blueprint+" Server build has been requested"
    return buildStatus