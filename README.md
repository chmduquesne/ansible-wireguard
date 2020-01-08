[![Build Status](https://travis-ci.org/chmduquesne/ansible-wireguard.svg?branch=master)](https://travis-ci.org/chmduquesne/ansible-wireguard)
[![Ansible Galaxy](http://img.shields.io/badge/ansible--galaxy-chmduquesne.wireguard-blue.svg)](https://galaxy.ansible.com/chmduquesne/wireguard/)

# wireguard

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

* `wireguard.{interface}` accepts: a dictionary formatted as described below. How to configure the interface `{interface}`.

### Wireguard interface

Required wireguard variables:

* `wireguard.{interface}.privkey`, accepts a string. Private key to use for `wg0`.

Optional wireguard variables:

* `wireguard.{interface}.pubkey` accepts a string. Public key to use for the interface (only useful in combination with `auto_assign_ranges`).
* `wireguard.{interface}.listenport` accepts a port number. Port to use for the interface.
* `wireguard.{interface}.dns`, accepts an ip address or a hostname. DNS server to use for the interface.
* `wireguard.{interface}.peers`, accepts a peer dictionary formatted as described below. Peer parameters. If `{{ inventory_hostname }}` appears in the peers section, it will be skipped.
* `wireguard.{interface}.mtu`, accepts an int. MTU to use for the interface
* `wireguard.{interface}.address`, accepts a list of ip addresses. Addresses to assign to the interface.

Convenience variables:

* `wireguard.{interface}.auto_assign_ranges` accepts a list of ip ranges. For each range and for each peer, an ip address is derived from the pubkey within the range, and is assigned as an additional allowedips. For the target host, the generated ip address is appended to `wireguard.{interface}.address`.
* `wireguard.{interface}.out_gw` accepts an interface name. If `{{ wireguard_iptable_module }}` is not `'none'`, the firewall will be configured to accept forwarding packets from `{interface}` to `wireguard.{interface}.out_gw`.
* `wireguard.{interface}.in_gw` accepts an interface name. If `{{ wireguard_iptable_module }}` is not `'none'`, the firewall will be configured to accept forwarding packets from `wireguard.{interface}.in_gw` to `{interface}`.
* `wireguard.{interface}.unbound_records` default: `False`, accepts a bool. If `wireguard.{interface}.auto_assign_ranges` is not empty, dns records will be generated for each peer in a format understood by unbound.

#### Wireguard interface peers

* `wireguard.{interface}.peers.{peername}`, accepts a dictionary as described below. How to configure the peer `machine0`.

#### Wireguard interface peer parameters

Required:

* `wireguard.{interface}.peers.{peername}.pubkey`, accepts a string. Public key to use for `machine0`.

Optional:

* `wireguard.{interface}.peers.{peername}.privkey`, accepts a string. (only useful in combination with `wireguard_generate_mobile`) If `{peername}` is mobile, private key to use in the configuration generation. If not provided, a placeholder will be used.
* `wireguard.{interface}.peers.{peername}.allowedips`, accepts a list of ip ranges. AllowedIPs to use for `{peername}`.
* `wireguard.{interface}.peers.{peername}.mobile`, default: False, accepts a boolean. Whether to generate a configuration for `{peername}` when `wireguard_generate_mobile` is true.

# Dependencies

This role can optionally use the module `iptables_raw` to do additional
firewall configuration.

# Example Playbook

Here is an example playbook:

    - hosts: wireguard
      roles:
         - role: chmduquesne.wireguard

Typically, to avoid repeating yourself, you should use the `|combine` filter extensively. For example, you could have the following `group_vars/all/vars.yml`:

    wireguard_iptable_module: "iptables_raw"
    
    wireguard_default:
      wg0:
        mtu: 1280
        dns: "{{ vault_wg0_dns }}"
        peers:
          # we use machine0 as an exit gateway
          machine0:
            pubkey: "{{ vault_wg0_machine0_pubkey }}"
            endpoint: "{{ vault_wg0_machine0_endpoint }}"
            allowedips:
              - "0.0.0.0/0"
              - "::/0"
            persistentkeepalive: 20
          # machine1 could be an entry gateway
          machine1:
            pubkey: "{{ vault_wg0_machine1_pubkey }}"
            allowedips:
              - "{{ vault_wg0_machine1_inet6_range }}"
          # machine2 and machine3 are mobile peers, not configured with ansible
          machine2:
            pubkey: "{{ vault_wg0_machine2_pubkey }}"
            privkey: "{{ vault_wg0_machine2_privkey }}"
            mobile: true
          machine3:
            pubkey: "{{ vault_wg0_machine3_pubkey }}"
            privkey: "{{ vault_wg0_machine3_privkey }}"
            mobile: true
          # machine4 is a regular peer
          machine4:
            pubkey: "{{ vault_wg0_machine4_pubkey }}"
        auto_assign_ips:
          - 10.0.0.0/8
          - fd1a:6126:2887::/48
          - "{{ vault_wg0_global_inet6_range }}"

Then, for `host_vars/machine0/vars.yml`:

    wireguard_override:
      wg0:
        privkey: "{{ vault_wg0_privkey }}"
        listenport: 500
        out_gw: enp0s20
        unbound_records: True
        dns: False
    wireguard: "{{ wireguard_default | combine(wireguard_override, recursive=True) }}"
    
    wireguard_generate_mobile: true
    wireguard_mobile_conf_dir: "wg_configs"
    wireguard_mobile_parameters:
      wg0:
        dns: "{{ wireguard_default.wg0.dns }}"

Then, for `host_vars/machine1/vars.yml`:

    wireguard_override:
      wg0:
        privkey: "{{ vault_wg0_privkey }}"
        in_gw: wlan0
        dns: False
        # Generate an uint32 from the interface name
        table: "{{ 'wg0'|checksum|truncate(4, end='')|int(base=16) }}"
    wireguard: "{{ wireguard_default|combine(wireguard_override, recursive=True) }}"

And for `host_vars/machine4/vars.yml`:

    wireguard_override:
      wg0:
        privkey: "{{ vault_wg0_privkey }}"
    wireguard: "{{ wireguard_default | combine(wireguard_override, recursive=True) }}"

`machine2` and `machine3` are not managed by ansible, and therefore they
do not require `host_vars` configuration.

# License

MIT

# Author Information

Christophe-Marie Duquesne
