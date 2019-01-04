wireguard
=========

Role to manage wireguard configuration

# Role Variables

## Top Level

* `wireguard_iptable_module` optional, default: `'none'`, accepts: `'iptables'|'iptables_raw'|'none'`
* `wireguard_generate_mobile` optional, default: `False`, accepts a boolean
* `wireguard_mobile_conf_dir` optional, default: `'.'`, accepts a path
* `wireguard_mobile_parameters` optional, default: `{}` accepts a dictionary name: parameters
* `wireguard` **required**, accepts a dictionary name: parameters

## Wireguard

Assuming interface name wg0:

* `wireguard.wg0` accept a dictionary formatted as described below

### Wireguard interface

Native wireguard variables

* `wireguard.wg0.privkey` **required**, accepts a string
* `wireguard.wg0.pubkey` optional, accepts a string
* `wireguard.wg0.listenport` optional, accepts a port number
* `wireguard.wg0.dns`, optional, accepts an ip address
* `wireguard.wg0.peers`, optional, accepts a peer dictionary formatted as described below
* `wireguard.wg0.mtu`, optional, accepts an int

Convenience variables

* `wireguard.wg0.auto_assign_ips`
* `wireguard.wg0.out_gw`
* `wireguard.wg0.in_gw`
* `wireguard.wg0.unbound_records`

#### Wireguard interface peers

* `wireguard.wg0.peers.machine0`

#### Wireguard interface peer parameters

* `wireguard.wg0.peers.machine0.pubkey`
* `wireguard.wg0.peers.machine0.privkey`
* `wireguard.wg0.peers.machine0.allowedips`
* `wireguard.wg0.peers.machine0.mobile`

# Dependencies

This role can optionally use the module `iptables_raw` to do additional
firewall configuration.

# Example Playbook

TODO

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

# License

MIT

# Author Information

Christophe-Marie Duquesne
