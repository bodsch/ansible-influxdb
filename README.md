
# Ansible Role:  `influxdb`

Ansible role to install and configure [influxdb2](https://github.com/influxdata/influxdb).

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-influxdb/main.yml?branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-influxdb)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-influxdb)][releases]
[![Ansible Quality Score](https://img.shields.io/ansible/quality/50067?label=role%20quality)][quality]

[ci]: https://github.com/bodsch/ansible-influxdb/actions
[issues]: https://github.com/bodsch/ansible-influxdb/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-influxdb/releases
[quality]: https://galaxy.ansible.com/bodsch/influxdb


This role installs, manages and configures (**ONLY**) InfluxDB2.

Pull-Requests and Issues are welcome :)


If `latest` is set for `influxdb_version`, the role tries to install the latest release version.
**Please use this with caution, as incompatibilities between releases may occur!**

The binaries are installed below `/usr/local/bin/influxdb/${influxdb_version}` and later linked to `/usr/bin`.
This should make it possible to downgrade relatively safely.

The downloaded archive is stored on the Ansible controller, unpacked and then the binaries are copied to the target system.
The cache directory can be defined via the environment variable `CUSTOM_LOCAL_TMP_DIRECTORY`.
By default it is `${HOME}/.cache/ansible/influxdb`.

If this type of installation is not desired, the download can take place directly on the target system.
However, this must be explicitly activated by setting `influxdb_direct_download` to `true`.

## Requirements & Dependencies

Ansible Collections

- [bodsch.core](https://github.com/bodsch/ansible-collection-core)
- [bodsch.scm](https://github.com/bodsch/ansible-collection-scm)

```bash
ansible-galaxy collection install bodsch.core
ansible-galaxy collection install bodsch.scm
```
or
```bash
ansible-galaxy collection install --requirements-file collections.yml
```


## Operating systems

Tested on

* Arch Linux
* Debian based
    - Debian 10 / 11
    - Ubuntu 20.10


## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-influxdb/tags)!


## Configuration

```yaml
influxdb_version: "2.4.0"

influxdb_release_download_url: https://dl.influxdata.com/influxdb/releases

influxdb_system_user: influxdb
influxdb_system_group: influxdb
influxdb_config_dir: /etc/influxdb
influxdb_storage_dir: /var/lib/influxdb

influxdb_direct_download: false

influxdb_service: {}

influxdb_config:
  http-bind-address: 127.0.0.1:8086
  reporting-disabled: true

influxdb_primary:
  organization: example-org
  bucket: example-bucket
  username: example-user
  password: LA9NMTb6WZ285zPGPgyUJEucuJUjr6W7
  token: example-token

influxdb_organizations: {}

influxdb_users: {}

influxdb_buckets: {}
```

### `influxdb_service`


```yaml
influxdb_service:
  # supported log levels are debug, info, and error (default info)
  log:
    level: error
```

### `influxdb_organizations`


```yaml
influxdb_organizations:
  main-org:
    state: create
    description: Main organization
  guest-org:
    state: create
```

### `influxdb_users`


```yaml
influxdb_users:

  foo:
    state: create
    organization:
      name: main-org
    password: secretPassword
    permissions: []

  guest01:
    state: create
    organization:
      name: guest-org
    password: secretPassword
```

### `influxdb_buckets`


```yaml
influxdb_buckets:

  bucket01:
    state: create
    description: First bucket
    organization:
      name: main-org
    retention: 1d

  bucket02:
    description: Second bucket
    organization:
      name: main-org
```

---

## Author and License

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
