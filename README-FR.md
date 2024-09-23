# django-automation
Domotique avec Python Django

#### Objectif:
- Système domotique léger pour la maison exclusivement réalisé en Python Django.
- Il est orienté MQTT pour tout développement d'objets connectés (IOT).
- Il intègre complètement la passerelle zigbee2mqtt et ses composants Zigbee.

#### Principe
- Serveurs et IOTs s'installent dans un réseau local ou un réseau privé (VPN)
- Un serveur MQTT Mosquitto assure les connexions des IOTs.
- Un coordinateur zigbee2mqt garantit les connexions Zigbee vers Mosquitto.
- Le serveur django et ses workers fournissent quant à eux les services de paramétrage et l'interface web.

#### OS et Machines utilisées
- Machines sous Linux de préférence, mais ce n'est pas obligatoire.
- Passerelle ou [coordinateur zigbee2mqtt](https://www.zigbee2mqtt.io/guide/adapters/)
- Les serveurs: sur PC, Raspberry pi3, pi4, orangepi, bananapi (ex: BPI-R3) 

## Installation
#### Zigbee2Mqtt
- IOTs Zigbee voir [Zigbee2MQTT](https://www.zigbee2mqtt.io/)
- Installation du [coordinateur Zigbee2MQTT](https://www.zigbee2mqtt.io/guide/installation/)
- Sur un raspberry pi4 ou pi5 on n'installera pas directement le dongle zigbee directement sur la machine (prendre un câble usb)

#### django-automation
Ici tout sera installé sur la même machine, mais ce n'est pas nécessaire.

- Choix du matériel
        
    - Idéal: Raspberry pi4 ou pi5
    - Très bon: Bananapi BPI-R3, mais leaflet impossible à installer
    
- Télécharger jango-automation-master.zip [ici](https://github.com/deunix-educ/django-automation)

        tar xzfv django-automation-master.zip
        ou
        git clone git@github.com:deunix-educ/django-automation.git
        cd django-automation
        chmod +x etc/bin/*.sh
        chmod +x automation/manage.py
        
- Installer d'abord les packages système (sudo ou root user)
 
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
        sudo cat >> /etc/supervisor/supervisord.conf << EOF
        [inet_http_server]
        port=*:9001
        username=root
        password=toor
        EOF
        
- configurer les serveurs

    Exemple de configuration dans etc/conf 
    
    - mosquitto: Adapter /etc/mosquitto/mosquitto.conf
        sudo mosquitto_passwd -c /etc/mosquitto/conf.d/passwd automation
        
    - zigbee2mqtt: Adapter le fichier de configuratio
        /home/automation/zigbee2mqtt/data/configuration.yaml
        
    - django-automation: Adapter etc/conf/automation_service.conf
        sudo cp etc/conf/automation_service.conf /etc/supervisor/conf.d/
        sudo supervisorctl reread
        
    - Editer et Configurer les variables d'environnement automation/.env-example
        cp automation/.env-example automation/.env
        
    - Créer l'environnement python (.venv)
        etc/bin/venv-install.sh etc/install/requirements.txt
        
- Tester l'application

        cd automation
        ./manage.py makemigrations
        ./manage.py migrate
        ./manage.py initapp
        
        # exemples
        ./manage.py loaddata ../etc/install/unit.json
        ./manage.py loaddata ../etc/install/automation.json
        ./manage.py loaddata../etc/install/django_celery_beat.json
        
        # préparer pour gunicorn
        ./manage.py collectstatic
        sudo supervisorctl update
        
        # Accès supervisor
        http://ip-du-serveur:9001
        
        # Accès django-automation
        http://ip-du-serveur
        

        