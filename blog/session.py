import hashlib

from django.contrib.sites import requests
from django.http import HttpResponseRedirect


class StickySessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.servers = ['http://localhost:8001', 'http://localhost:8002']
        self.server_status = {server: True for server in self.servers}

    def get_server_for_ip(self, client_ip):
        healthy_servers = [server for server, healthy in self.server_status.items() if healthy]
        if not healthy_servers:
            return None

        index = int(hashlib.md5(client_ip.encode()).hexdigest(), 16) % len(self.servers)
        return self.servers[index]

    def health_check(self):
        for server in self.servers:
            try:
                response = requests.get(f"{server}/health", timeout=2)
                self.server_status[server] = response.status_code == 200
            except:
                self.server_status[server] = False

    def __call__(self, request):
        self.health_check()

        client_ip = request.META.get('REMOTE_ADDR')
        if client_ip:
            selected_server = self.get_server_for_ip(client_ip)
            print(f"Client IP: {client_ip} -> Routed to Server: {selected_server}")

        response = self.get_response(request)
        return response
