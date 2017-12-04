from flask import Flask, render_template, redirect, request, url_for, jsonify, session
from flask_ask import Ask, statement, question
from flask_assets import Bundle, Environment
from vmapi import *
from vraapi import vra_build
from nsxapi import validateNSX, createNsxWire
import os
import sys
import subprocess
import configparser
import json

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['ASK_VERIFY_REQUESTS'] = False
ask = Ask(app, "/control_center")

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui-dark.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)

VMTENV = os.environ.copy()


def execute(cmd, ofile=subprocess.PIPE, efile=subprocess.PIPE,
            env=os.environ):
    proc = subprocess.Popen(cmd, stdout=ofile, stderr=efile, env=env)
    out, err = proc.communicate()
    if type(out).__name__ == "bytes":
        out = out.decode()

    return (proc, out)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == "POST":
        attempted_username = request.form['username']
        print(attempted_username)
        attempted_password = request.form['password']
        print(attempted_password)
        if attempted_username == "admin" and attempted_password == "password":
            session['logged_in'] = True
            session['wrong_pass'] = False
            session['username'] = request.form['username']
            return redirect(url_for('configurepage'))
        else:
            session['logged_in'] = False
            session['wrong_pass'] = True
    return render_template('index.html')


@app.route('/configure/', methods=['GET', 'POST'])
def configurepage():
    if session['logged_in'] is True:
        if request.method == "POST":
            url = request.form['vcenterurl']
            user = request.form['vcenteruser']
            password = request.form['vcenterpassword']
            vraurl = request.form['vraurl']
            vrauser = request.form['vrauser']
            vrapassword = request.form['vrapass']
            vratenant = request.form['vratenant']
            nsxurl = request.form['nsxurl']
            nsxuser = request.form['nsxuser']
            nsxpass = request.form['nsxpass']
            Config = configparser.ConfigParser()
            cfgfile = open("/srv/avss/appdata/etc/config.ini", 'w')
            Config.add_section('vcenterConfig')
            Config.set('vcenterConfig', 'url', url)
            Config.set('vcenterConfig', 'user', user)
            Config.set('vcenterConfig', 'password', password)
            Config.add_section('vraConfig')
            Config.set('vraConfig', 'url', vraurl)
            Config.set('vraConfig', 'user', vrauser)
            Config.set('vraConfig', 'password', vrapassword)
            Config.set('vraConfig', 'tenant', vratenant)
            Config.add_section('nsxConfig')
            Config.set('nsxConfig', 'url', nsxurl)
            Config.set('nsxConfig', 'user', nsxuser)
            Config.set('nsxConfig', 'password', nsxpass)
            Config.write(cfgfile)
            cfgfile.close()
        return render_template('configure.html')
    else:
        return redirect(url_for('homepage'))

@app.route('/api/rest/vcenter/vms')
def getvms():
    p = get_vms()
    return json.dumps(p)

@app.route('/commands/')
def alexacommands():
    return render_template('alexacommands.html')


@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('homepage'))


@ask.launch
def start_skill():
    welcome_message = 'Giddeon is online'
    return question(welcome_message)


@ask.intent("VMCountIntent")
def share_count():
    counting = vm_count()
    count_msg = 'The total number of virtual machines \
registered in this v-center is {}'.format(counting)
    payload = {"message":counting}
    requests.post("https://7mx9stmpja.execute-api.us-east-1.amazonaws.com/Production/sendnotification", data=json.dumps(counting))
    return question(count_msg)


@ask.intent("memoryCount")
def memory_count():
    memCount = vm_memory_count()/1024
    count_msg = 'You have provisioned {} gigabytes of memory'.format(memCount)
    payload = {"message":memCount}
    requests.post("https://7mx9stmpja.execute-api.us-east-1.amazonaws.com/Production/sendnotification", data=json.dumps(payload))
    return question(count_msg)


@ask.intent("dcReport")
def dc_report():
    memcount = vm_memory_count()/1024
    cpucount = vm_cpu_count()
    (version, build) = get_vcenter_build()
    health = get_vcenter_health_status()
    clustercount = len(get_cluster())
    vmcount = vm_count()
    poweredon = powered_on_vm_count()
    uptime = get_uptime()
    capacity_msg = render_template('capacity_report', memory=memcount, cpu=cpucount, 
    version=format(version), build=build, health=health, clustercount=clustercount, 
    vmcount=vmcount, poweredon=poweredon, uptime=uptime)
    return question(capacity_msg).simple_card(health)


@ask.intent("HostClustersIntent")
def hosts_in_cluster():
    hosts = get_cluster()
    length = len(hosts)
    hosts_in_cluster_mgr = 'You currently have {} clusters \
within the environment'.format(length)
    return question(hosts_in_cluster_mgr)


@ask.intent("VCenterBuildIntent")
def share_vcenter_build():
    (version, build) = get_vcenter_build()
    notice = render_template('vcenter_build', version=format(version), build=build)
    return statement(notice)


@ask.intent("ApplianceUptimeIntent")
def uptime_appliance():
    ut = get_uptime()
    uptimeMsg = 'Your current VCSA uptime is {} hours'.format(ut)
    return question(uptimeMsg)


@ask.intent("ApplianceHealthIntent")
def share_vcenter_health():
    health = get_vcenter_health_status()
    health_msg = 'The current health of the cluster is {}'.format(health)
    return question(health_msg)


@ask.intent("DSIntent")
def share_ds_free():
    ds = get_datastore()
    dsTotal = len(ds)
    ds_msg = 'You currently have {} datastores. The current free \
datastore space on each in gigabytes is {}'.format(dsTotal, ds)
    return question(ds_msg)


@ask.intent("PoweredOnVMIntent")
def get_powered_on_vms():
    pwrvm = powered_on_vm_count()
    pwr_msg = 'There are currently {} virtual machines powered on in your environment'.format(pwrvm)
    print(pwr_msg)
    return question(pwr_msg)


@ask.intent("cpuIntent")
def share_cpu_intent():
    vmcpu = vm_cpu_count()
    vmcpumsg = "You current have {} CPU provisioned in your environment".format(vmcpu)
    return question(vmcpu)


@ask.intent("HostClusterStatusIntent")
def share_cluster_status():
    (drs, ha, vsan) = get_cluster_status()
    if drs:
        drs_msg = "DRS is enabled, "
    else:
        drs_msg = "DRS is disabled, "

    if ha:
        ha_msg = "High Availablity is enabled "
    else:
        ha_msg = "High Availablity is disabled "

    if vsan:
        vsan_msg = "and Virtual SAN is enabled"
    else:
        vsan_msg = "and Virtual SAN is disabled"

    cluster_msg = drs_msg + ha_msg + vsan_msg
    return question(cluster_msg)


@ask.intent("VSANClusterIntent")
def share_vsan_version():
    version = get_vsan_version()
    vsan_msg = "Virtual SAN is running version " + version
    return question(vsan_msg)


@ask.intent("VCOSIntent")
def share_vc_os():
    (proc, out) = execute(["/usr/local/bin/powershell",
                          '/srv/avss/appdata/pcli.ps1',
                           'GetVCOS'], env=VMTENV)

    vcos_msg = "The vCenter Server is running " + format(out)
    return question(vcos_msg)


@ask.intent("BuildWindowsIntent")
def win_build():
    win = vra_build('Windows 2012')
    return question(win)


@ask.intent("BuildCentOSIntent")
def centos_build():
    centos = vra_build('CentOS')
    return question(centos)


@ask.intent("BuildNginxIntent")
def nginx_build():
    nginx = vra_build('Nginx')
    return question(nginx)

@ask.intent("CheckNsxApi")
def check_nsx():
    status = validateNSX()
    return question(status)

@ask.intent("createNSXWire")
def create_vwire(vwname):
    lsvwire = createNsxWire(vwname)
    return question(lsvwire)


@ask.intent("NoIntent")
def no_intent():
    bye_text = 'Giddeon Shutting Down'
    return statement(bye_text)


if __name__ == '__main__':
    app.run(debug=True)
