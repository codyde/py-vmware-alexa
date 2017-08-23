import requests

def auth_vcenter_rest():
    url = "https://hlcorevc01.humblelab.com"
    username = "administrator@vsphere.local"
    password = "VMware123!"
    print('Authenticating to vCenter REST API, user: {}'.format(username))
    resp = requests.post('{}/rest/com/vmware/cis/session'.format(url),
                         auth=(username, password), verify=False)
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp.json()['value']


def get_rest_api_data(req_url):
    sid = auth_vcenter_rest()
    print('Requesting Page: {}'.format(req_url))
    resp = requests.get(req_url, verify=False,
                        headers={'vmware-api-session-id': sid})
    if resp.status_code != 200:
        if resp.status_code == 401:
            print("401 received; clearing stale SID")
            AuthConfig.remove_option('auth', 'sid')
            AuthConfig.remove_section('auth')
        print('Error! API responded with: {}'.format(resp.status_code))
        auth_vcenter_rest()
        get_rest_api_data(req_url)
        return
    return resp

def get_vms():
    url = "https://hlcorevc01.humblelab.com"
    i = get_rest_api_data('{}/rest/vcenter/vm'.format(url))
    return i.json()['value']
