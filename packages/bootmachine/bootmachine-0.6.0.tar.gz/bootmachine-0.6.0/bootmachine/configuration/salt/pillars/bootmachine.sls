# Permission of 600 recommended for this file

# SERVERS
servers:

  rackspacev2-salt-fedora18-b:
    public_ip: 166.78.181.224
    private_ip: 10.182.9.37
    roles: ['test-additional-minions']

  rackspacev2-salt-fedora18-a:
    public_ip: 166.78.63.131
    private_ip: 10.182.23.56
    roles: ['salt-master']


# SSH
ssh_port: 30303

# USERS
users:

  rizumu:
    fullname: bootmachine
    uid: 1000
    gid: 1000
    group: rizumu
    extra_groups: [sshers, wheel, ops]
    ssh_auth:
      keys: [

       ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA3i6Tnj/0dOsH7nEaCN/X+ikAtmMzqBgyhI3hux/3oHsHZroK+F7x0/heOIDZwuLeYwnca3QK617MXXw4snZru/CC0jHE0LTOftX5akVzm4meJd1qMuQnbQKhjJprswfw/bUSm3Nypu2vnAxBxyghJ04HQZ24QwO7fFsVTqXpySY/xHw4zrvPf6FfSDCefqSWADpLRJEcLhY7qmPlF9rvRjEJYOotROImyS2kwUk3WWGhvvUkBMlr+9JsrD9hrrbQj7vOAlH7CPeA2q6UhnEbT4tIPQYt7QYC7hS2oGcg/KQt7YVX1pmOmUyKJmpgql1fawAX6e57/6G2Aem3RkWuPw== bootmachine.key,

      ]


# SALT
saltmaster_hostname: rackspacev2-salt-fedora18-a
saltmaster_private_ip: 10.182.23.56
saltmaster_public_ip: 166.78.63.131
saltminion_private_ips:

  - 10.182.9.37

  - 10.182.23.56

salt_remote_states_dir: /srv/salt/states/
salt_remote_pillars_dir: /srv/salt/pillars/

# ARCH SPECIFIC
pacman_extra_repos:
salt_aur_pkgver: 0.15.1
salt_aur_pkgrel: 1