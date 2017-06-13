# py-vmware-alexa
Python Flask and Flask-Ask driven integration for Amazon Alexa and VMware API's 
------------------------------------------------------------------------------
6/13 - To run Docker Container, clone repo, switch to docker directory and run

*docker build -t containername*

when it finishes building - run your container with.. 

*docker run -d -p 443:443 containername*
------------------------------------------------------------------------------

Goals: 

-Expand VMware "core" API's leveraging SOAP API vs REST fo

-Integrate vROPS APIs for datacenter statistics 

-Integrate deeper vRA content 

-Implement NSX REST API commands 

-Create registration page with DB integration to store registration details for removal of staic configuration