import ipaddress

from fastapi import Request


def get_anon_ip(request: Request) -> str:
    if request.client is None:
        return ""

    raw_ip = request.client.host
    ip = ipaddress.ip_address(raw_ip)
    match ip:
        case ipaddress.IPv4Address():
            network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
            return str(network.network_address)
        case ipaddress.IPv6Address():
            network = ipaddress.IPv6Network(f"{ip}/64", strict=False)
            return str(network.network_address)
