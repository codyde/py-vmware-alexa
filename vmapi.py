import atexit
import configparser
import requests
import sys
import ssl
import re
import vsanmgmtObjects
import vsanapiutils
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from requests.packages.urllib3.exceptions import InsecureRequestWarning

__all__ = ['get_vcenter_build', 'get_cluster_status', 'get_vsan_version',
           'get_vcenter_health_status', 'vm_count', 'get_cluster']


# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

config = configparser.ConfigParser()
config.read("etc/config.txt")
url = config.get("vcenterConfig", "url")
user = config.get("vcenterConfig", "user")
password = config.get("vcenterConfig", "password")


def auth_vcenter_rest(username, password):
    print('Authenticating to vCenter REST API, user: {}'.format(username))
    resp = requests.post('{}/com/vmware/cis/session'.format(url),
                         auth=(user, password), verify=False)
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp.json()['value']


def get_rest_api_data(req_url):
    sid = auth_vcenter_rest(user, password)
    print('Requesting Page: {}'.format(req_url))
    resp = requests.get(req_url, verify=False,
                        headers={'vmware-api-session-id': sid})
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp


# Function to login to vSphere SOAP API
# returns ServiceInstance
def auth_vcenter_soap(url, username, password):
    print('Authenticating to vCenter SOAP API, user: {}'.format(username))

    context = None

    if sys.version_info[:3] > (2, 7, 8):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    pattern = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
    parsed = re.search(pattern, url)
    host = parsed.group('host')

    si = SmartConnect(host=host,
                      user=username,
                      pwd=password,
                      port=443,
                      sslContext=context)

    atexit.register(Disconnect, si)

    return si


# Function to login to vSAN Mgmt API
# return vSAN Managed Objects
def auth_vsan_soap(si):
    context = None
    if sys.version_info[:3] > (2, 7, 8):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    vcMos = vsanapiutils.GetVsanVcMos(si._stub, context=context)
    return vcMos


def get_vcenter_health_status():
    print("Retreiving vCenter Server Appliance Health ...")
    health = get_rest_api_data('{}/appliance/health/system'.format(url))
    j = health.json()
    return '{}'.format(j['value'])


def vm_count():
    countarry = []
    for i in get_rest_api_data('{}/vcenter/vm'.format(url)).json()['value']:
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
    i = get_api_data('{}/vcenter/vm?filter.names={}'.format(url, name))
    return results.json()['value']


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


# Example of using vSphere SOAP API
def get_vcenter_build():
    print("Retrieving vCenter Server Version and Build information ...")
    si = auth_vcenter_soap(url, user, password)
    return (si.content.about.apiVersion, si.content.about.build)


# Example of using vSphere SOAP API
# Not in use until we Alexa Skill can accept input
def getClusterInstance(clusterName, serviceInstance):
    content = serviceInstance.RetrieveContent()
    searchIndex = content.searchIndex
    datacenters = content.rootFolder.childEntity
    for datacenter in datacenters:
        cluster = searchIndex.FindChild(datacenter.hostFolder, clusterName)
        if cluster is not None:
            return cluster
    return None


# Example of using vSphere SOAP API
def get_first_cluster(si):
    content = si.RetrieveContent()
    viewManager = content.viewManager
    container = viewManager.CreateContainerView(content.rootFolder,
                                                [vim.ClusterComputeResource],
                                                True)

    for c in container.view:
        cluster_view = c
        break

    container.Destroy()

    return cluster_view


# Example of using vSAN Mgmt API
def get_cluster_status():
    print("Retrieving vSphere Cluster Status ...")
    si = auth_vcenter_soap(url, user, password)
    vcMos = auth_vsan_soap(si)

    cluster = get_first_cluster(si)
    vccs = vcMos['vsan-cluster-config-system']
    vsanCluster = vccs.VsanClusterGetConfig(cluster=cluster)
    vsanEnabled = vsanCluster.enabled
    drsEnabled = cluster.configuration.drsConfig.enabled
    haEnabled = cluster.configuration.dasConfig.enabled
    return (drsEnabled, haEnabled, vsanEnabled)


# Example of using vSAN Mgmt API
def get_vsan_version():
    print("Retrieving vSAN Cluster Status ...")
    si = auth_vcenter_soap(url, user, password)
    vcMos = auth_vsan_soap(si)

    cluster = get_first_cluster(si)
    vchs = vcMos['vsan-cluster-health-system']
    results = vchs.VsanVcClusterQueryVerifyHealthSystemVersions(cluster)
    return results.vcVersion
