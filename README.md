wireguard
=========

Role to manage wireguard configuration

# Role Variables

## Top Level

* `wireguard_iptable_module` default: ``none`` (`'iptables'`|`'iptables_raw'`|`'none'`)
* `wireguard_generate_mobile` default: `False`
* `wireguard_mobile_conf_dir` default: `'.'`
* `wireguard_mobile_parameters` default: `{}`
* `wireguard`

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
