#
# encoding: utf-8
#from django.utils.translation import gettext_lazy as _
import time
from django.core.management import BaseCommand
from ..modules.ssh_tunnel import SshTunnelWorker

class Command(BaseCommand):

    def handle(self, *args, **options):
        daemon = None
        try:
            daemon = SshTunnelWorker()
            daemon.run_forever()
        except Exception as e:
            print(f'\n    ssh tunnel worker error {e}')
        finally:
            if daemon:
                print(f'\n    Stop ssh tunnel worker\n')
                daemon.stop_services()
                time.sleep(5)
