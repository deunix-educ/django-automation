'''
Created on 5 janv. 2023

@author: denis
'''
import logging, threading
from automation.models import SshTunnel
from sshtunnel import open_tunnel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tunnel(threading.Thread):

    def __init__(self, tunnel):
        super().__init__(daemon=True)
        self.tun_stop = threading.Event()
        self.tunnel = tunnel

    def run(self):
        server = None
        try:
            with open_tunnel(
                    (self.tunnel.host, self.tunnel.port),
                    ssh_username=self.tunnel.username,
                    ssh_password=self.tunnel.password,
                    remote_bind_address=(self.tunnel.remote_bind_host, self.tunnel.remote_bind_port),
                    local_bind_address=(self.tunnel.local_bind_host, self.tunnel.local_bind_port),
                ) as server:

                logging.info( f'\n{self.tunnel.remote_bind_host}:{self.tunnel.remote_bind_port} local forward: {self.tunnel.remote_bind_host}:{server.local_bind_port}' )
                while not self.tun_stop.is_set():
                    threading.Event().wait(1)

        except Exception as e:
            logging.error(f'\n    tunnel error {e}')
        finally:
            if server:
                logging.info(f'Stop tunnel {self.tunnel.host}:{self.tunnel.port}')
                server.stop()

    def stop(self):
        self.tun_stop.set()


class SshTunnelWorker():

    def __init__(self):
        self.worker_stop = threading.Event()
        self.tunnels = {}
        tunnels = SshTunnel.objects.filter(active=True).all()
        for tunnel in tunnels:
            self.tunnels[tunnel.id] = Tunnel(tunnel)

    def stop_services(self):
        for i in self.tunnels.keys():
            self.tunnels[i].stop()
        self.worker_stop.set()

    def run_forever(self):
        for i in self.tunnels.keys():
            self.tunnels[i].start()

        while not self.worker_stop.is_set():
            threading.Event().wait(1)

