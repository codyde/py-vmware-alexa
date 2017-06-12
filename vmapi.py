import requests
import configparser
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable SSL warnings

def get_vcenter_health_status():
    health = get_api_data('{}/appliance/health/system'.format(url))
    j = health.json()
    return '{}'.format(j['value'])


def vm_count():
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    countarry = []
    for i in get_api_data('{}/vcenter/vm'.format(url)).json()['value']:
        countarry.append(i['name'])
    p = len(countarry)
    return p

def vm_memory_count():
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    memcount = []
    for i in get_api_data('{}/vcenter/vm'.format(url)).json()['value']:
        memcount.append(i['memory_size_MiB'])
    p = sum(memcount)
    return p

def vm_cpu_count():
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    cpucount = []
    for i in get_api_data('{}/vcenter/vm'.format(url)).json()['value']:
        cpucount.append(i['cpu_count'])
    p = sum(cpucount)
    return p

def powered_on_vm_count():
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    onCount = []
    for i in get_api_data('{}/vcenter/vm'.format(url)).json()['value']:
        if i['power_state'] == 'POWERED_ON':
            onCount.append(i['name'])
    p = len(onCount)
    return p

def get_vm(name):
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    i = get_api_data('{}/vcenter/vm?filter.names={}'.format(url,name)).json()['value']
    return i

def get_clusters():
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    resp = get_api_data('{}/vcenter/host'.format(url))
    k = resp.json()
    hosts = []
    for i in k['value']:
        hosts.append(i['name'])
    return hosts

def get_datastore():
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    resp3 = get_api_data('{}/vcenter/datastore'.format(url))
    dsresp = resp3.json()
    datastores = []
    for i in dsresp['value']:
        datastores.append(i['free_space'])
    return datastores


def auth_vcenter(username,password):
    config = configparser.ConfigParser()
    config.read("/srv/avss/appdata/etc/config.ini")
    url = config.get("vcenterConfig", "url")
    user = config.get("vcenterConfig", "user")
    password = config.get("vcenterConfig", "password")
    print('Authenticating to vCenter, user: {}'.format(username))
    resp = requests.post('{}/com/vmware/cis/session'.format(url), auth=(user, password), verify=False)
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp.json()['value']

def get_api_data(req_url):
    sid = auth_vcenter(user,password)
    print('Requesting Page: {}'.format(req_url))
    resp = requests.get(req_url, verify=False, headers={'vmware-api-session-id':sid})
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp
