#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function
import os
import sys

from ansible.module_utils.basic import AnsibleModule

# # influx bucket --help
# NAME:
#    influx bucket - Bucket management commands
#
# USAGE:
#    influx bucket command [command options] [arguments...]
#
# COMMANDS:
#    create            Create bucket
#    delete            Delete bucket
#    list, find, ls    List buckets
#    update, find, ls  Update bucket
#
# OPTIONS:
#    --help, -h  show help


class InfluxBucket(object):
    """
    """

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.host = module.params.get("host")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")
        self. = module.params.get("")

        self._influx = module.get_bin_path("influx", True)

    def run(self):
        """
          runner
        """
        result = dict(
            failed=False,
            changed=False,
            ansible_module_results="none"
        )

        args = []

        self.module.log(msg=f"  args: '{}'".format(args))

        return result

    def _bucket_create(self):
        """
        """

    def _bucket_delete(self):
        """
        """

    def _bucket_list(self):
        """
        """

    def _bucket_update(self):
        """
        """

    def _bucket_password(self):
        """
        """

    def _exec(self, commands, check_rc=True):
        """
          execute shell program
        """
        rc, out, err = self.module.run_command(commands, check_rc=check_rc)

        self.module.log(msg=f"  rc : '{rc}'")
        self.module.log(msg=f"  out: '{out}'")
        self.module.log(msg=f"  err: '{err}'")

        return rc, out, err

# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            host=dict(
                required=True,
                type="str"
            ),
        ),
        supports_check_mode=False,
    )

    o = InfluxBucket(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
