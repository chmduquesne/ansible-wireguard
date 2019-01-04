wireguard
=========

Role to manage wireguard configuration

# Role Variables

This role has multiple optional features.

## Top Level

Required:

* `wireguard` accepts a dictionary \{name: parameters\}. How to configure each interface.

Optional:

* `wireguard_iptable_module` default: `'none'`, accepts: `'iptables'|'iptables_raw'|'none'`. Which ansible module to use for managing the firewall. Leave unchanged if you do not wish for any firewall modification.
* `wireguard_generate_mobile` default: `False`, accepts a boolean. Whether to generate configurations for hosts that cannot be managed with ansible.
* `wireguard_mobile_conf_dir` default: `'.'`, accepts a path. **Local** (on the machine running ansible) directory where to generate the mobile hosts configuration.
* `wireguard_mobile_parameters` default: `{}` accepts a dictionary name: parameters. Parameters used to override the configuration when generatin mobile hosts configuration (e.g. if you want DNS on the mobile hosts, but not on the host you are configuring)
* `wireguard_unbound_records_dir` default: `'/etc/unbound/records.d'`, accepts a path. Directory where to optionally generate unbound records.

## Wireguard

* `wireguard.wg0` accepts: a dictionary formatted as described below. How to configure the interface `wg0`.

### Wireguard interface

Required wireguard variables:

* `wireguard.wg0.privkey`, accepts a string. Private key to use for `wg0`.

Optional wireguard variables:

* `wireguard.wg0.pubkey` accepts a string. Public key to use for `wg0` (only useful in combination with `auto_assign_ips`).
* `wireguard.wg0.listenport` accepts a port number. Port to use for the `wg0`.
* `wireguard.wg0.dns`, accepts an ip address or a hostname. DNS server to use for `wg0`.
* `wireguard.wg0.peers`, accepts a peer dictionary formatted as described below. Peer parameters. If `{{ inventory_hostname }}` appears in the peers section, it will be skipped.
* `wireguard.wg0.mtu`, accepts an int. MTU to use for `wg0`
* `wireguard.wg0.address`, accepts a list of ip addresses. Addresses to assign to `wg0`.

Convenience variables:

* `wireguard.wg0.auto_assign_ips` accepts a list of ip ranges. For each range and for each peer, an ip address is derived from the pubkey within the range, and is assigned as an additional allowedips. For the target host, the generated ip address is appended to `wireguard.wg0.address`.
* `wireguard.wg0.out_gw` accepts an interface name. If `{{ wireguard_iptable_module }}` is not `'none'`, the firewall will be configured to accept forwarding packets from `wg0` to this interface.
* `wireguard.wg0.in_gw` accepts an interface name. If `{{ wireguard_iptable_module }}` is not `'none'`, the firewall will be configured to accept forwarding packets from this interface to `wg0`.
* `wireguard.wg0.unbound_records` default: `False`, accepts a bool. If `wireguard.wg0.auto_assign_ips` is not empty, dns records will be generated for each peer in a format understood by unbound.

#### Wireguard interface peers

* `wireguard.wg0.peers.machine0`, accepts a dictionary as described below. How to configure the peer `machine0`.

#### Wireguard interface peer parameters

Required:

* `wireguard.wg0.peers.machine0.pubkey`, accepts a string. Public key to use for `machine0`.

Optional:

* `wireguard.wg0.peers.machine0.privkey`, accepts a string. (only useful in combination with `wireguard_generate_mobile`) If `machine0` is mobile, private key to use in the configuration generation.
* `wireguard.wg0.peers.machine0.allowedips`, accepts a list of ip ranges. AllowedIPs to use for `machine0`.
* `wireguard.wg0.peers.machine0.mobile`, default: False, accepts a boolean. Whether to generate a configuration for `machine0` when `wireguard_generate_mobile` is true.

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
