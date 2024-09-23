# django-automation
Home automation with Python Django

#### Objective:
- Lightweight home automation system exclusively made in Python Django.
- It is MQTT oriented for any development of connected objects (IOT).
- It fully integrates the zigbee2mqtt gateway and its Zigbee components.

#### Principle
- Servers and IOTs are installed in a local network or a private network (VPN)
- A Mosquitto MQTT server ensures the connections of the IOTs.
- A zigbee2mqt coordinator guarantees the Zigbee connections to Mosquitto.
- The django server and its workers provide the configuration services and the web interface.

#### OS and Machines used
- Machines under Linux preferably, but it is not mandatory.
- Gateway or [zigbee2mqtt coordinator](https://www.zigbee2mqtt.io/guide/adapters/)
- Servers: on PC, Raspberry pi3, pi4, orangepi, bananapi (ex: BPI-R3)

## Installation
#### Zigbee2Mqtt
- Zigbee IOTs see [Zigbee2MQTT](https://www.zigbee2mqtt.io/)
- Installation of the [Zigbee2MQTT coordinator](https://www.zigbee2mqtt.io/guide/installation/)
- On a raspberry pi4 or pi5 we will not directly install the zigbee dongle directly on the machine (take a usb cable)

#### django-automation
Here everything will be installed on the same machine, but it is not necessary.

- Hardware selection

    - Ideal: Raspberry pi4 or pi5
    - Very good: Bananapi BPI-R3, but leaflet impossible to install
    
- Download jango-automation-master.zip [here](https://github.com/deunix-educ/django-automation)

        tar xzfv django-automation-master.zip
        or
        git clone git@github.com:deunix-educ/django-automation.git
        cd django-automation
        chmod +x etc/bin/*.sh
        chmod +x automation/manage.py

- Install system packages first (sudo or root user)

        sudo apt update
        sudo apt -y install build-essential openssl git pkg-config redis supervisor
        sudo apt -y install python3-dev python3-pip python3-venv libmariadb-dev libpq-dev

        # zigbee2mqtt node.js 
        sudo curl -sL https://deb.nodesource.com/setup_10.x | sudo bash - 
        sudo apt -y install nodejs 
        
        # mosquitto 
        sudo apt -y install mosquitto 
        
        # influxdb V2 
        sudo curl https://repos.influxdata.com/influxdata-archive.key | gpg --dearmor | sudo tee /usr/share/keyrings/influxdb 
        sudo echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian stable main" | sudo tee /etc/apt/sources.list.d/influxdb.list 
        sudo apt update 
        sudo apt -y install influxdb2 
        
        # supervisor 
        sudo cp /etc/supervisor/supervisord.conf /etc/supervisor/supervisord.conf.old 
        sudo cat >> /etc/supervisor/supervisord.conf << EOF [inet_http_server] port=*:9001 username=root password=toor EOF 
        
- configure the servers Configuration example in etc/conf 
        
    - mosquitto: Adapter /etc/mosquitto/mosquitto.conf 

        sudo mosquitto_passwd -c /etc/mosquitto/conf.d/passwd automation 
        
    - zigbee2mqtt: Adapt the configuration file 

        /home/automation/zigbee2mqtt/data/configuration.yaml 
        
    - django-automation: Adapt etc/conf/automation_service.conf

        sudo cp etc/conf/automation_service.conf /etc/supervisor/conf.d/
        sudo supervisorctl reread

    - Edit and Configure Environment Variables automation/.env-example

        cp automation/.env-example automation/.env

    - Create the python environment (.venv)

        etc/bin/venv-install.sh etc/install/requirements.txt

    - Test the application

        cd automation
        ./manage.py makemigrations
        ./manage.py migrate
        ./manage.py initapp

        # examples
        ./manage.py loaddata ../etc/install/unit.json
        ./manage.py loaddata ../etc/install/automation.json
        ./manage.py loaddata../etc/install/django_celery_beat.json

        # prepare for gunicorn
        ./manage.py collectstatic
        sudo supervisorctl update

        # Supervisor access
        http://server-ip:9001

        # django-automation access
        http://server-ip
        