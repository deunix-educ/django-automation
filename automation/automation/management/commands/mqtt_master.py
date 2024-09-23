# encoding: utf-8
from django.core.management import BaseCommand
from django.conf import settings
from ..modules.mqttclient import MqttWorker


class Command(BaseCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("--host", action="store", dest="host", type=str, required=False)


    def handle(self, *args, **options):
        daemon = None
        try:
            config = settings.MQTT_MASTER_WORKER
            daemon = MqttWorker(**config)
            daemon.startMQTT()
            daemon.loop_forever()
        except Exception as e:
            print(f'\n    MqttWorker error {e}')
        finally:
            if daemon:
                daemon.stopMQTT()
