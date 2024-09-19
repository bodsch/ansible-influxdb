# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, print_function)
__metaclass__ = type

import re
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
        }

    def influxdb_release(self, data, influxdb_version, version=None):
        """
        """
        display.v(f"influxdb_release(self, {data}, {influxdb_version}, {version})")

        influxdb_files = data.get("files", {})

        display.v(f"  - {influxdb_files}")

        if version:
            if self.version_compare(influxdb_version, ">", version):

                for k,v in influxdb_files.items():
                    data["files"][k] = re.sub(r'-linux-amd64', '_linux_amd64', v)

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
