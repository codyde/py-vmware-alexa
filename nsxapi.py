import requests
from requests.auth import HTTPBasicAuth
import configparser
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable SSL warning

def validateNSX():
    Config = configparser.ConfigParser()
    Config.read("/srv/avss/appdata/etc/config.ini")
    url = Config.get("nsxConfig", "url")
    user = Config.get("nsxConfig", "user")
    password = Config.get("nsxConfig", "password")
    tenant = Config.get("nsxConfig", "tenant")
    nsxUrl = "{}/api/4.0/firewall/globalroot-0/config".format(url)
    headers = {
        "accept":"application/json",
        'content-type':'application/json'
    }
    res = requests.get(nsxUrl, headers=headers, auth=HTTPBasicAuth(user, password), verify=False)
    if res.status_code != 200: 
        return("API Down")
    else:
        return("API is Online")

def createNsxWire(lsName):
    Config = configparser.ConfigParser()
    Config.read("/srv/avss/appdata/etc/config.ini")
    url = Config.get("nsxConfig", "url")
    user = Config.get("nsxConfig", "user")
    password = Config.get("nsxConfig", "password")
    tenant = Config.get("nsxConfig", "tenant")
    nsxUrl = "{}api/2.0/vdn/scopes/vdnscope-1/virtualwires".format(url)
    xml = """<virtualWireCreateSpec>
<name>{}</name>
<description></description>
<tenantId></tenantId>
<controlPlaneMode>UNICAST_MODE</controlPlaneMode>
<guestVlanAllowed>false</guestVlanAllowed>
</virtualWireCreateSpec>""".format(lsName)
    headers = {
        "accept":"application/xml",
        'content-type':'application/xml'
    }
    res = requests.post(nsxUrl, headers=headers, auth=HTTPBasicAuth(user, password), data=xml, verify=False)
    if res.status_code != 201:
        return "Error Occured During Creation"
    else: 
        return lsName+" successfully created"


        