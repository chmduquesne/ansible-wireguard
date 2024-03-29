[![Build Status](https://travis-ci.org/chmduquesne/ansible-wireguard.svg?branch=master)](https://travis-ci.org/chmduquesne/ansible-wireguard)
[![Ansible Galaxy](http://img.shields.io/badge/ansible--galaxy-chmduquesne.wireguard-blue.svg)](https://galaxy.ansible.com/chmduquesne/wireguard/)

# wireguard

Role to manage wireguard configuration

# Role Variables

## Top Level

Required:

* `wireguard` accepts a dictionary `{name: parameters}`. How to configure each interface.
* `wireguard_mobile` (default: `{}`) accepts a dictionary `{name: parameters}`. How to configure peers that are not managed by ansible, interface by interface.

Optional:

* `wireguard_mobile_conf_dir` (default: `'/etc/wireguard/mobile'`) accepts a path. Directory where to optionally generate the mobile hosts configuration.
* `wireguard_unbound_records_dir` (default: `'/etc/unbound/records.d'`) accepts a path. Directory where to optionally generate unbound records.

## Wireguard

* `wireguard.{interface}` accepts a dictionary formatted as described below. How to configure the interface `{interface}`.

### Wireguard interface

Required:

* `wireguard.{interface}.privkey` accepts a string. Private key to use for the interface.

Optional:

* `wireguard.{interface}.listenport` accepts a port number. Port to use for the interface.
* `wireguard.{interface}.dns` accepts an ip address or a hostname. DNS server to use for the interface.
* `wireguard.{interface}.peers` accepts a peer dictionary formatted as described in section *Wireguard interface peers*. How to configure the peers.
* `wireguard.{interface}.mtu` accepts an int. MTU to use for the interface.
* `wireguard.{interface}.address` accepts a list of ip addresses. Addresses to assign to the interface.

Convenience:

* `wireguard.{interface}.auto_assign_ranges` accepts a list of ip ranges. For each range and for each peer, an ip address is derived from the pubkey within the range, and is assigned as an additional allowedips. For the target host, the generated ip address is appended to `wireguard.{interface}.address`. The logic of `auto_assign_ranges` replicates and is fully compatible with [wg-ip](https://github.com/chmduquesne/wg-ip).
* `wireguard.{interface}.unbound_records` (default: `False`) accepts a bool. If `wireguard.{interface}.auto_assign_ranges` is not empty, dns records will be generated for each peer in a format understood by unbound.

#### Wireguard interface peers

* `wireguard.{interface}.peers.{peername}` accepts a dictionary as described below. How to configure the peer `{peername}`.

#### Wireguard interface peer parameters

Required:

* `wireguard.{interface}.peers.{peername}.pubkey` accepts a string. Public key to use for `{peername}`.

⚠ If an entry has a public key corresponding to `wireguard.{interface}.privkey`, it is automatically removed and will not appear in the generated configuration.

Optional:

* `wireguard.{interface}.peers.{peername}.privkey` accepts a string. (only useful in combination with `wireguard_generate_mobile`) If `{peername}` is mobile, private key to use in the configuration generation. If not provided, a placeholder will be used.
* `wireguard.{interface}.peers.{peername}.allowedips` accepts a list of ip ranges. AllowedIPs to use for `{peername}`.

## Wireguard mobile

* `wireguard_mobile.{interface}` accepts a dictionary `{hostname:
  configuration}`. How to configure hosts that are not managed by ansible
  for the interface `{interface}`. Each key of this dictionary must be a
  host name, and each value is a dictionary which follows the same
  structure as the `wireguard.{interface}` variable. It will be used to
  expand the same template as for `wireguard.{interface}` in the
  directory `{{ wireguard_mobile_conf_dir }}`.


# Example playbook

Here is an example playbook:

```YAML
  - hosts: wireguard
    roles:
        - role: chmduquesne.wireguard
```

We have a central server `server`, a laptop `laptop`, a desktop `desktop`
which are all managed with ansible. Additionally, we have an android
cellphone `phone` which is not managed with ansible, but for which we
still want to generate a configuration on the server.

We define an auxiliary dictionary in `group_vars/all/vars.yml`, to store
shared settings:

```YAML
# File group_vars/all/vars.yml
# - all vault_wg0_ variables would be defined in group_vars/all/vault.yml
# - all _pubkeys variables are wireguard public keys
# - vault_wg0_server_endpoint = example.com:8000
# - vault_wg0_global_inet6_range = 2001:db8:85a3:1::/64
# - vault_wg0_dns = fd1a:6126:2887::1
wireguard_global_settings:
  wg0:
    peers:
      server:
        pubkey: "{{ vault_wg0_server_pubkey }}"
        endpoint: "{{ vault_wg0_server_endpoint }}"
        allowedips:
          - "0.0.0.0/0"
          - "::/0"
        persistentkeepalive: 20
      laptop:
        pubkey: "{{ vault_wg0_laptop_pubkey }}"
      desktop:
        pubkey: "{{ vault_wg0_desktop_pubkey }}"
      phone:
        pubkey: "{{ vault_wg0_phone_pubkey }}"
    auto_assign_ranges:
      - 10.0.0.0/8
      - fd1a:6126:2887::/48
      - "{{ vault_wg0_global_inet6_range }}"
    mtu: 1360
    dns: "{{ vault_wg0_dns }}"
```

The server configuration:
```YAML
# File host_vars/server/vars.yml
# - all vault_wg0_ variables would be defined in host_vars/server/vault.yml
# - all _privkey variables are wireguard private keys matching the
#   respective publi keys

wireguard:
  wg0:
    privkey: "{{ vault_wg0_privkey }}"
    listenport: 500
    unbound_records: True
    dns: False
    peers: "{{ wireguard_global_settings.wg0.peers }}"
    auto_assign_ranges: "{{ wireguard_global_settings.wg0.auto_assign_ranges }}"
    mtu: "{{ wireguard_global_settings.wg0.mtu }}"

wireguard_mobile:
  wg0:
    phone:
      privkey: "{{ vault_wg0_phone_privkey }}"
      dns: "{{ wireguard_global_settings.wg0.dns }}"
      peers:
        server: "{{ wireguard_global_settings.wg0.peers.server }}"
      auto_assign_ranges: "{{ wireguard_global_settings.wg0.auto_assign_ranges }}"
```

laptop and desktop configurations:
```YAML
# Files host_vars/{laptop,desktop}/vars.yml
# - vault_wg0_privkey would be defined in host_vars/{laptop,desktop}/vault.yml
#   and match the respective pubkey from wireguard_global_settings.wg0.peers
wireguard:
  wg0:
    privkey: "{{ vault_wg0_privkey }}"
    peers:
      server: "{{ wireguard_global_settings.wg0.peers.dedibox }}"
    auto_assign_ranges: "{{ wireguard_global_settings.wg0.auto_assign_ranges }}"
    mtu: "{{ wireguard_global_settings.wg0.mtu }}"
    dns: "{{ wireguard_global_settings.wg0.dns }}"
```

# License

MIT

# Author Information

Christophe-Marie Duquesne
