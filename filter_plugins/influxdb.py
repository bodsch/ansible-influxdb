# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, print_function)
__metaclass__ = type

import re
import os
import operator as op
from packaging.version import Version

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
        Ansible file jinja2 tests
    """

    def filters(self):
        return {
            'influxdb_fix_release': self.influxdb_release,
            'influx_binaries': self.influx_binaries,
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

        # display.v(f"= result: {data}")
        # display.v(f"= result: {result}")

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
        # display.v(f"influx_binaries(self, {data})")

        files_with_path = []
        files = []
        _dict = {}

        if isinstance(data, list):
            display.v(f"  - {data}")

            files_with_path = [x.get('path') for x in data if x.get('path')]
            files = [os.path.basename(x) for x in files_with_path]

            _dict = {k: x  for k in files for x in files_with_path if os.path.basename(x) == k}

        return _dict
