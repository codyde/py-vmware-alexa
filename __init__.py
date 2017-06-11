from flask import Flask, render_template, flash, redirect, request, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_ask import Ask, statement, question
from flask_assets import Bundle, Environment
from vmapi import get_clusters, get_datastore, get_vcenter_health_status, vm_count, vm_cpu_count, vm_memory_count, powered_on_vm_count
from vraapi import vra_build

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
ask = Ask(app, "/control_center")

db = SQLAlchemy(app)

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js', 'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)

class Services(db.Model):
   id = db.Column('service_id', db.Integer, primary_key = True)
   serviceName = db.Column(db.String(100))
   serviceAddress = db.Column(db.String(50))
   servicePort = db.Column(db.Integer)
   serviceStatus = db.Column(db.Boolean)

def get_datastores():
    dsarry = []
    for i in get_datastore():
        dsround = round(i/1024/1024/1024)
        dsarry.append(dsround)
    return dsarry

def get_hosts():
    vhosts = get_clusters()
    return vhosts

@app.route('/')
def homepage():
    flash("Database Configuration Currently Not Implemented")
    return render_template('index.html')

@app.route('/commands/')
def alexacommands():
    return render_template('alexacommands.html')

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