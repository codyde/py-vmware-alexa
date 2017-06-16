# py-vmware-alexa
Project Gideon: VMware API with Python and Flask and Flask-Ask (https://github.com/johnwheeler/flask-ask)

Huge thanks to John Wheeler for creating Flask-Ask; a simple toolkit for building Amazon Echo Skills! 

This project is designed to demonstrate the ease of leveraging VMware APIs vocally using an Amazon Echo or Echo Dot. REST, SOAP (via Python SDK), and PowerCLI are currently supported; however PowerCLI commands may take long to run.

This project currently leverages:
    - Docker to run all components in a container environment (https://www.docker.com/)
    - Python 3.4
        - pyVmomi Modules for VMware SOAP API (https://github.com/vmware/pyvmomi)
    - Flask (Web Application Framework) (http://flask.pocoo.org/docs/0.12/)
    - Flask-Ask (Abstraction of skills creation) (https://github.com/johnwheeler/flask-ask)
    - Letsencrypt Certificates (https://letsencrypt.org/)
    - Nginx for Web Hosting (https://nginx.org/en/)
    - uWSGI to run Python Code as a Web Applicaton (https://uwsgi-docs.readthedocs.io/en/latest/)

Developed primarilly by Cody De Arkland of https://www.thehumblelab.com and William Lam of https://virtuallyghetto.com (his github repo for his fork - https://github.com/lamw/alexavsphereskill)

To Run, leverage the following: 
    - Clone this repo (*git clone https://github.com/codyde/py-alexa-vmware.git*)
    - change to directory (*i.e. cd /py-vmware-alexa*)
    - Initiate a docker build command (*docker build -t gideon:v1 .*)
    - Run newly created docker container (*docker run -it -p 443:443 gideon:v1*)
    - Container will run at a /bin/bash prompt currently for troubleshooting, move up one directory (*cd ..*) and run *./startup.sh* to start container 
    - Connect to URL hosting application 
    - Login with Admin/Password
    - Configure Endpoints 
    - Confiugure skill in developer center 
    - Enjoy! 