from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2 import Environment, FileSystemLoader
from ansible import errors
from ansible.module_utils._text import to_text
from ansible.errors import AnsibleFilterError
import ipaddress
import hashlib
import sys
import json
import copy
import nacl.utils
from nacl.public import PrivateKey, Box


def sha256(s):
    """
    Computes the sha256 hash of the input string
    """
    return hashlib.sha256(s.encode()).digest()


def wg_pubkey(s):
    """
    Computes the wireguard public key corresponding to the input private key
    """
    encoder = nacl.encoding.Base64Encoder
    key = nacl.public.PrivateKey(s, encoder)
    return to_text(encoder.encode(bytes(key.public_key)))


def gen_ip(s, subnet='2001:db8::/48', with_prefixlen=False,
        with_maxprefixlen=False):
    """
    This filter expects a string input (normally a wireguard public key)
    and turns it into an ip address.

    The process of turning the input string into this ip address happens
    in 3 steps:
    1. Compute the sha256sum of the input
    2. Select the first n bytes of the resulting sum (n=4 for ipv4, n=16
       for ipv6 - this depends on the subnet argument)
    3. Mask the resulting ip address with the subnet, so that the
       resulting ip address is within that subnet
    """
    if sys.version_info.major < 3:
        subnet = unicode(subnet)

    network = ipaddress.ip_network(subnet)
    mask = network.netmask.packed
    head = network.network_address.packed
    tail = sha256(s + '\n')
    ip_bytes = bytearray()

    if sys.version_info.major < 3:
        for m, t, h in zip(mask, tail, head):
            ip_bytes.append(ord(h)&ord(m)|ord(t)&(ord(m)^255))
    else:
        for m, t, h in zip(mask, tail, head):
            ip_bytes.append(h&m|t&(m^255))

    cls = network.netmask.__class__
    res = to_text(cls(bytes(ip_bytes)))

    if with_prefixlen and with_maxprefixlen:
        raise AnsibleFilterError(
            "|gen_ip: you cannot include both prefixlen and maxprefixlen"
            )

    if with_prefixlen:
        res += "/%d" % network.prefixlen

    if with_maxprefixlen:
        res += "/%d" % network.netmask.max_prefixlen

    return to_text(res)


def remove_self(config):
    """
    Self-remove from the peers dictionary
    """
    c = dict(config)
    pubkey = get_pubkey(c)
    peers = {k: v for k, v in c['peers'].items() if v["pubkey"] != pubkey}
    c['peers'] = peers
    return c


def get_pubkey(config):
    """
    Return the public key at the root of the config
    """
    res = None
    if 'pubkey' in config:
        return config['pubkey']
    return wg_pubkey(config['privkey'])


def auto_assign_ips(config):
    """
    Automatically assign ip addresses to the configuration, derived from
    the auto_assign_ranges provided in the configuration
    """
    # Make a copy of the config that we can safely modify
    c = copy.deepcopy(config)

    # If there is no ip to assign, return immediately
    subnets = c.get('auto_assign_ranges', [])
    if not subnets:
        return c

    # Assign an ip to the host
    pubkey = get_pubkey(c)
    address = c.get('address', [])
    if not isinstance(address, list):
        raise AnsibleFilterError(
                '|auto_assign_ips: "address" should be a list')
    for subnet in subnets:
        generated = gen_ip(pubkey, subnet=subnet, with_prefixlen=True)
        if generated not in address:
            address += [generated]
    c['address'] = address

    # Assign allowedips to the peers
    for peername, peervars in c.get('peers', dict()).items():
        allowedips = peervars.get('allowedips', [])
        if not isinstance(allowedips, list):
            raise AnsibleFilterError(
                    '|auto_assign_ips: "allowedips" should be a list')

        for subnet in subnets:
            generated = gen_ip(peervars['pubkey'], subnet=subnet, with_maxprefixlen=True)
            if generated not in allowedips:
                allowedips += [generated]
        c['peers'][peername]['allowedips'] = allowedips

    return c


def first_subnet(subnets, version=4):
    """
    Returns the first subnetwork of a list, filtered by version
    """
    for subnet in subnets:
        network = ipaddress.ip_network(subnet)
        if network.version == version:
            return subnet
    return ""


def dns_records(config, hostname, version=4):
    """
    Returns dns records for each host of the config
    """
    res = []

    subnet = first_subnet(config.get('auto_assign_ranges', []), version=version)
    if not subnet:
        return []

    #Not needed?
    #pubkey = get_pubkey(config)
    #if pubkey:
    #    res += [[hostname, gen_ip(pubkey, subnet=subnet)]]

    peers = config.get('peers', dict())
    for peername in sorted(list(peers.keys())):
        peervars = peers[peername]
        res += [[peername, gen_ip(peervars['pubkey'], subnet=subnet)]]

    return res


class FilterModule(object):

    def filters(self):
        return {
            'gen_ip': gen_ip,
            'auto_assign_ips': auto_assign_ips,
            'remove_self': remove_self,
            'dns_records': dns_records,
        }
