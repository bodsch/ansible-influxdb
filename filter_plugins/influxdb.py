# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, print_function, annotations)

__metaclass__ = type

import re
import os
import operator as op
from ipaddress import ip_address
from packaging.version import Version
from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
    """

    def filters(self):
        return {
            'influxdb_fix_release': self.influxdb_release,
            'influxdb_fix_binary': self.influxdb_fix_binary,
            'influx_binaries': self.influx_binaries,
            'influxdb_update_release': self.influxdb_update_release,
            'influxdb_bind': self.influxdb_bind,
        }

    def influxdb_release(self, data, influxdb_version, version=None):
        """
        """
        # display.v(f"influxdb_release(self, {data}, {influxdb_version}, {version})")
        # influxdb_files = data.get("files", {})
        # display.v(f"  - {influxdb_files}")
        if version:
            if self.version_compare(influxdb_version, ">", version):
                value = data.get("files", {}).get("influxdb")
                data["files"]["influxdb"] = re.sub(r'-linux-amd64', '_linux_amd64', value)

        return data

    def influxdb_fix_binary(self, data, influxdb_version, influxdb_type=""):
        """
        """
        display.v(f"influxdb_fix_binary(self, {data}, {influxdb_version}, {influxdb_type})")

        result = []

        if influxdb_type == 'client':
            if int(influxdb_version) == 2:
                result.append(influxdb_version)
                result.append("client")
                data += '-'.join(result)
            if int(influxdb_version) == 3:
                data = "influxctl"

        else:
            if int(influxdb_version) in [2,3]:
                result.append(influxdb_version)

            if int(influxdb_version) == 3:
                result.append("core")

            data += '-'.join(result)


        display.v(f"= result: {data}")

        return data

    def version_compare(self, ver1, specifier, ver2):
        """
        """
        lookup = {'<': op.lt, '<=': op.le, '==': op.eq, '>=': op.ge, '>': op.gt}

        try:
            return lookup[specifier](Version(ver1), Version(ver2))
        except KeyError:
            # unknown specifier
            return False

    def influx_binaries(self, data):
        """
        """
        display.v(f"influx_binaries(self, {data})")

        files_with_path = []
        files = []
        _dict = {}

        if isinstance(data, list):
            files_with_path = [x.get('path') for x in data if x.get('path')]
            files = [os.path.basename(x) for x in files_with_path]

            _dict = {k: x for k in files for x in files_with_path if os.path.basename(x) == k}

        display.v(f"= result: {_dict}")

        return _dict

    def influxdb_update_release(self, data, core_version, client_version):
        """
        """
        display.v(f"influxdb_update_release(self, {data}, {core_version}, {client_version})")

        _main_version = core_version[0:1]

        _download_url_core = "https://dl.influxdata.com/influxdb/releases"
        _download_url_client = "https://dl.influxdata.com/influxctl/releases"

        if int(_main_version) < 3:
            _download_url_client = _download_url_core

        if int(_main_version) == 2:
            _file_core = f"influxdb2-{core_version}_linux_amd64.tar.gz"
            _file_client = f"influxdb2-client-{client_version}-linux-amd64.tar.gz"
            _binaries_core = "influxd"
            _binaries_client = "influx"

        if int(_main_version) == 3:
            _file_core = f"influxdb3-core-{core_version}_linux_amd64.tar.gz"
            _file_client = f"influxctl-v{client_version}-linux-x86_64.tar.gz"
            _binaries_core = "influxdb3"
            _binaries_client = "influxctl"

        _data = data.copy()

        _data['download_urls']['core'] = _download_url_core
        _data['download_urls']['client'] = _download_url_client
        _data['files']['core'] = _file_core
        _data['files']['client'] = _file_client
        _data['binaries']['core'] = _binaries_core
        _data['binaries']['client'] = _binaries_client

        display.v(f"= result: {_data}")

        return _data


    def influxdb_bind(self, data, core_version):
        """
        """
        display.v(f"influxdb_bind(self, {data}, {core_version})")

        result = "http://"

        if int(core_version) == 1:
            return None

        if int(core_version) == 2:
            raw = data.get("bind_address")
            host, port = _parse_ip_port(raw)

            ip_str = host if host else "0.0.0.0"
            if not _validate_ip(ip_str):
                result = None
            else:
                result = _format_url(ip_str, port)

        if int(core_version) == 3:
            raw = data.get("bind")
            host, port = _parse_ip_port(raw)
            # Für v3 muss IP vorhanden und gültig sein
            if host in (None, '') or port is None or not _validate_ip(host):
                result = None
            else:
                result = _format_url(host, port)

        display.v(f"= result: {result}")

        return result



def _parse_ip_port(value: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Parse "IP:PORT" or "[IPv6]:PORT" or ":PORT" (empty IP allowed).
    Returns (ip_str_or_empty, port) where ip_str_or_empty can be '' if missing.
    Invalid -> (None, None).
    """
    if not isinstance(value, str) or not value:
        return None, None

    # IPv6 in brackets: [::1]:8086
    if value.startswith('['):
        try:
            host, rest = value.split(']', 1)
            host = host[1:]  # strip leading '['
            if not rest.startswith(':'):
                return None, None
            port_str = rest[1:]
        except ValueError:
            return None, None
        return host, _parse_port(port_str)

    # IPv4 or empty host: ":8086" or "127.0.0.1:8086"
    if ':' not in value:
        return None, None
    host, port_str = value.rsplit(':', 1)
    return host, _parse_port(port_str)


def _parse_port(port_str: str) -> Optional[int]:
    try:
        p = int(port_str)
        return p if 1 <= p <= 65535 else None
    except Exception:
        return None


def _validate_ip(ip_str: str) -> bool:
    try:
        ip_address(ip_str)
        return True
    except Exception:
        return False


def _format_url(ip_str: str, port: int) -> str:
    # Bracket IPv6 in URLs
    try:
        ip_obj = ip_address(ip_str)
        if ip_obj.version == 6:
            return f"http://[{ip_str}]:{port}"
    except Exception:
        pass
    return f"http://{ip_str}:{port}"
