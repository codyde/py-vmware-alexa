FROM centos

MAINTAINER Cody De Arkland <cdearkland@vmware.com>

RUN yum install -y epel-release && \
yum install -y python34 python34-pip uwsgi uwsgi-plugin-python3 uwsgi-logger-file nginx git wget gcc python34-devel.x86_64 openssl-devel.x86_64 && \ 
yum clean all && \
python3 -m pip install --user virtualenv

RUN mkdir -p /srv && python3 -m virtualenv /srv/avss
RUN . /srv/avss/bin/activate; pip3 install flask flask-ask requests configparser flask_sqlalchemy flask_assets
RUN . /srv/avss/bin/activate; yum install -y uwsgi
COPY py-vmware-alexa /srv/avss/appdata
RUN mkdir -p /etc/uwsgi.d
COPY nginx.conf /etc/nginx/nginx.conf
COPY avss.ini /etc/uwsgi.d/avss.ini
COPY alexavsphereskill.conf /etc/nginx/conf.d/alexavsphereskill.conf
COPY fullchain.pem /etc/letsencrypt/live/pyva.humblelab.com/fullchain.pem
COPY privkey.pem /etc/letsencrypt/live/pyva.humblelab.com/privkey.pem
ADD startup.sh /srv/avss/startup.sh

RUN chown uwsgi:nginx /srv/avss && \
chown uwsgi:nginx /etc/uwsgi.d/avss.ini && \ 
chmod 755 /srv/avss/startup.sh && chmod 777 /srv/avss/appdata/etc/config.ini

EXPOSE 443
CMD /srv/avss/startup.sh
