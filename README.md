
# Ansible Role:  `influxdb`

Ansible role to install and configure [influxdb2](https://github.com/influxdata/influxdb).

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-influxdb/main.yml?branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-influxdb)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-influxdb)][releases]
[![Ansible Downloads](https://img.shields.io/ansible/role/d/bodsch/influxdb?logo=ansible)][galaxy]

[ci]: https://github.com/bodsch/ansible-influxdb/actions
[issues]: https://github.com/bodsch/ansible-influxdb/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-influxdb/releases
[galaxy]: https://galaxy.ansible.com/ui/standalone/roles/bodsch/influxdb


This role installs, manages and configures (**ONLY**) InfluxDB2.

Pull-Requests and Issues are welcome :)


If `latest` is set for `influxdb_version`, the role tries to install the latest release version.
**Please use this with caution, as incompatibilities between releases may occur!**

The `influxd` binary are installed below `/opt/influxd/${influxdb_version}` and later linked to `/usr/bin`.  
The `influx` binary are installed below `/opt/influx/${influxdb_cli_version}` and later linked to `/usr/bin`.  
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
* Artix Linux
* Debian based
    - Debian 10 / 11 / 12
    - Ubuntu 20.10 / 22.04

> **RedHat-based systems are no longer officially supported! May work, but does not have to.**


## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-influxdb/tags)!


## Configuration

```yaml
# see: https://docs.influxdata.com/influxdb/v2/reference/release-notes/influxdb/
influxdb_version: "2.4.0"
# see: https://docs.influxdata.com/influxdb/v2/reference/release-notes/influx-cli/
influxdb_cli_version: "{{ influxdb_version }}"

influxdb_scm:
  use_tags: false
  without_beta: false
  version_filter:
    - ".*test*"
    - ".*preview"
    - ".*beta"
    - ".*rc"

influxdb_release: {}
  # download_url: ""
  # api_url: ""
  # files:
  #   influxdb: ""
  #   influx_client: ""
  # binaries:
  #   influxd: ""
  #   influx: ""

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

### `influxdb_scm`

If you want to install the latest version of Influxd, you can configure the variable `influxdb_version` with `latest`.

The corresponding version will then be read from [GitHub](https://github.com/influxdata/influxdb/releases).

> **Unfortunately, this does not work with the CLI client!**


### `influxdb_release`

Only needed to download the binary archives.

Default configuration:

```yaml
influxdb_release:
  download_url: "https://dl.influxdata.com/influxdb/releases"
  api_url: ""
  files:
    influxdb: "{{ influxdb_bin_version }}-{{ influxdb_version }}-{{ ansible_facts.system | lower }}-{{ system_architecture }}.tar.gz"
    influx_client: "{{ influxdb_bin_version }}-client-{{ influxdb_cli_version }}-{{ ansible_facts.system | lower }}-{{ system_architecture }}.tar.gz"
  binaries:
    influxd: "influxd"
    influx: "influx"
```

### `influxdb_service`


```yaml
influxdb_service:
  # supported log levels are debug, info, and error (default info)
  log:
    level: info
  # add an instance id for replications to prevent collisions and allow querying by edge node
  instance_id: "{{ ansible_hostname }}"
  # Don't expose metrics over HTTP at /metrics
  metrics:
    enabled: true
  # Disable the InfluxDB UI
  ui:
    enabled: true
  http:
    # bind address for the REST HTTP API (default ":8086")
    bind_address: ":8086"
    timeouts:
      # max duration the server should keep established connections alive while waiting for new requests.
      # Set to 0 for no timeout (default 3m0s)
      idle: "3m"
      # max duration the server should spend trying to read HTTP headers for new requests.
      # Set to 0 for no timeout (default 10s)
      read_header: ""
      # max duration the server should spend trying to read the entirety of new requests.
      # Set to 0 for no timeout
      read: ""
      # max duration the server should spend on processing+responding to requests.
      # Set to 0 for no timeout
      write: ""

  tls:
    # TLS certificate for HTTPs
    cert: ""
    # TLS key for HTTPs
    key: ""
    # Minimum accepted TLS version (default "1.2")
    min-version: ""
    # Restrict accept ciphers to:
    #   ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, ECDHE_RSA_WITH_AES_128_GCM_SHA256, ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
    #   ECDHE_RSA_WITH_AES_256_GCM_SHA384, ECDHE_ECDSA_WITH_CHACHA20_POLY1305, ECDHE_RSA_WITH_CHACHA20_POLY1305
    strict-ciphers: []

  influxql:
    # The maximum number of group by time bucket a SELECT can create.
    # A value of zero will max the maximum number of buckets unlimited.
    max_select_buckets: ""
    # The maximum number of points a SELECT can process.
    # A value of 0 will make the maximum point count unlimited.
    # This will only be checked every second so queries will not be aborted immediately when hitting the limit.
    max_select_point: ""
    # The maximum number of series a SELECT can run.
    # A value of 0 will make the maximum series count unlimited.
    max_select_series: ""
  query:
    # the number of queries that are allowed to execute concurrently.
    # Set to 0 to allow an unlimited number of concurrent queries (default 1024)
    concurrency: ""
    # the initial number of bytes allocated for a query when it is started.
    # If this is unset, then query-memory-bytes will be used
    initial_memory_bytes: ""
    # the maximum amount of memory used for queries.
    # Can only be set when query-concurrency is limited.
    # If this is unset, then this number is query-concurrency * query-memory-bytes
    max_memory_bytes: ""
    # maximum number of bytes a query is allowed to use at any given time.
    # This must be greater or equal to query-initial-memory-bytes
    memory_bytes: ""
    # the number of queries that are allowed to be awaiting execution before new queries are rejected.
    # Must be > 0 if query-concurrency is not unlimited (default 1024)
    queue_size: ""
  storage:
    # The maximum size a shard's cache can reach before it starts rejecting writes. (default 1.0 GiB)
    cache_max_memory_size: ""
    # The size at which the engine will snapshot the cache and write it to a TSM file, freeing up memory. (default 25 MiB)
    cache_snapshot_memory_size: ""
    # The length of time at which the engine will snapshot the cache and write it to a new TSM file if the shard hasn't received writes or deletes. (default 10m0s)
    cache_snapshot_write_cold_duration: ""
    # The duration at which the engine will compact all TSM files in a shard if it hasn't received a write or delete. (default 4h0m0s)
    compact_full_write_cold_duration: ""
    # The rate limit in bytes per second that we will allow TSM compactions to write to disk. (default 48 MiB)
    compact_throughput_burst: ""
    # The maximum number of concurrent full and level compactions that can run at one time.
    # A value of 0 results in 50% of runtime.GOMAXPROCS(0) used at runtime.  Any number greater than 0 limits compactions to that value.
    # This setting does not apply to cache snapshotting.
    max_concurrent_compactions: ""
    # The threshold, in bytes, when an index write-ahead log file will compact into an index file.
    # Lower sizes will cause log files to be compacted more quickly and result in lower heap usage at the expense of write throughput. (default 1.0 MiB)
    max_index_log_file_size: ""
    # Skip field-size validation on incoming writes.
    no_validate_field_size: false
    # The interval of time when retention policy enforcement checks run. (default 30m0s)
    retention_check_interval: ""
    # The maximum number of concurrent snapshot compactions that can be running at one time across all series partitions in a database.
    series_file_max_concurrent_snapshot_compactions: ""
    # The size of the internal cache used in the TSI index to store previously calculated series results.
    series_id_set_cache_size: ""
    # The default period ahead of the endtime of a shard group that its successor group is created. (default 30m0s)
    shard_precreator_advance_period: ""
    # The interval of time when the check to pre-create new shards runs. (default 10m0s)
    shard_precreator_check_interval: ""
    # Controls whether we hint to the kernel that we intend to page in mmap'd sections of TSM files.
    tsm_use_madv_willneed: false
    # Validates incoming writes to ensure keys only have valid unicode characters.
    validate_keys: false
    # The amount of time that a write will wait before fsyncing.
    # A duration greater than 0 can be used to batch up multiple fsync calls.
    # This is useful for slower disks or when WAL write contention is seen. (default 0s)
    wal_fsync_delay: ""
    # The max number of writes that will attempt to write to the WAL at a time. (default <nprocs> * 2)
    wal_max_concurrent_writes: ""
    # The max amount of time a write will wait when the WAL already has storage-wal-max-concurrent-writes active writes. Set to 0 to disable the timeout. (default 10m0s)
    wal_max_write_delay: ""
    # The max amount of time the engine will spend completing a write request before cancelling with a timeout. (default 10s)
    write_timeout: ""

  vault:
    # address of the Vault server expressed as a URL and port, for example: https://127.0.0.1:8200/.
    vault_addr: ""
    # path to a PEM-encoded CA certificate file on the local disk.
    # This file is used to verify the Vault server's SSL certificate.
    # This environment variable takes precedence over VAULT_CAPATH.
    vault_cacert: ""
    # path to a directory of PEM-encoded CA certificate files on the local disk. These certificates are used to verify the Vault server's SSL certificate.
    vault_capath: ""
    # path to a PEM-encoded client certificate on the local disk. This file is used for TLS communication with the Vault server.
    vault_client_cert: ""
    # path to an unencrypted, PEM-encoded private key on disk which corresponds to the matching client certificate.
    vault_client_key: ""
    # timeout variable. The default value is 60s.
    vault_client_timeout: ""
    # maximum number of retries when a 5xx error code is encountered. The default is 2, for three total attempts. Set this to 0 or less to disable retrying.
    vault_max_retries: ""
    # do not verify Vault's presented certificate before communicating with it. Setting this variable is not recommended and voids Vault's security model.
    vault_skip_verify: false
    # name to use as the SNI host when connecting via TLS.
    vault_tls_server_name: ""
    # vault authentication token
    vault_token: ""
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
