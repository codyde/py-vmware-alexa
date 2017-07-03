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
    r = requests.get(nsxUrl, headers=headers, auth=HTTPBasicAuth(user, password), verify=False)
    if r.status_code != 200: 
        return("API Down")
    else:
        return("API is Online")

        