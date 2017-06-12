from flask import Flask, render_template, flash, redirect, request, url_for, jsonify, session
from flask_ask import Ask, statement, question
from flask_assets import Bundle, Environment
from vmapi import get_clusters, get_datastore, get_vcenter_health_status, vm_count, vm_cpu_count, vm_memory_count, powered_on_vm_count
from vraapi import vra_build
import sys,os
import configparser

app = Flask(__name__)
app.secret_key = "super secret key"
ask = Ask(app, "/control_center")

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js', 'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)

def get_datastores():
    dsarry = []
    for i in get_datastore():
        dsround = round(i/1024/1024/1024)
        dsarry.append(dsround)
    return dsarry

def get_hosts():
    vhosts = get_clusters()
    return vhosts

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
            Config.write(cfgfile)
            cfgfile.close()
        return render_template('configure.html')
    else:
        return redirect(url_for('homepage'))

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

@ask.intent("CountIntent")
def share_count():
    counting = vm_count()
    count_msg = 'The total number of virtual machines registered in this v-center is {}'.format(counting)
    return question(count_msg)

@ask.intent("memoryCount")
def memory_count():
    memCount = vm_memory_count()/1024
    count_msg = 'You have provisioned {} gigabytes of memory'.format(memCount)
    return question(count_msg)

@ask.intent("HostInClusterIntent")
def hosts_in_cluster():
    hosts = get_cluster()
    length = len(hosts)
    hosts_in_cluster_mgr = 'You currently have {} clusters within the environment'.format(length)
    return question(hosts_in_cluster_mgr)

@ask.intent("HealthIntent")
def share_vcenter_health():
    health = get_vcenter_health_status()
    health_msg = 'The current health of the cluster is {}'.format(health)
    return question(health_msg)

@ask.intent("DSIntent")
def share_ds_free():
    ds = get_datastores()
    dsTotal = len(ds)
    ds_msg = 'You currently have {} datastores. The current free datastore space on each in gigabytes is {}'.format(dsTotal,ds)
    return question(ds_msg)

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

@ask.intent("NoIntent")
def no_intent():
    bye_text = 'Giddeon Shutting Down'
    return statement(bye_text)

if __name__ == '__main__':
    app.run(debug=True)