FROM centos

MAINTAINER Cody De Arkland <cdearkland@vmware.com>

EXPOSE 443

WORKDIR /srv/avss/appdata

RUN yum install -y epel-release && \
    yum install -y python34 \
    python34-pip \
    uwsgi \
    uwsgi-plugin-python3 \
    uwsgi-logger-file \
    nginx \
    git \
    wget \
    gcc \
    python34-devel.x86_64 \
    openssl-devel.x86_64 && \
    yum clean all

RUN python3 -m pip install --user virtualenv

RUN mkdir -p /etc/uwsgi.d && \
    mkdir -p /srv && \
    python3 -m virtualenv /srv/vapy

RUN . /srv/vapy/bin/activate; pip3 install flask flask-ask requests configparser flask_sqlalchemy flask_assets pyvmomi

COPY . /srv/vapy/appdata
RUN mv configs/nginx.conf /etc/nginx/nginx.conf
RUN mv configs/avss.ini /etc/uwsgi.d/avss.ini
RUN mv configs/alexavsphereskill.conf /etc/nginx/conf.d/alexavsphereskill.conf
RUN mkdir -p /etc/letsencrypt/live/pyva.humblelab.com/
RUN mv configs/*.pem /etc/letsencrypt/live/pyva.humblelab.com/
RUN mv configs/startup.sh /srv/vapy/startup.sh
RUN rmdir /srv/vapy/appdata/configs

RUN chown uwsgi:nginx /srv/vapy && \
    chown uwsgi:nginx /etc/uwsgi.d/avss.ini && \
    chmod 755 /srv/vapy/startup.sh && chmod 777 /srv/vapy/appdata/etc/config.ini

CMD /srv/vapy/startup.sh
CMD ["/bin/bash"]