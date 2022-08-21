#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

# # influx auth --help
# NAME:
#    influx auth - Authorization management commands
#
# USAGE:
#    influx auth command [command options] [arguments...]
#
# COMMANDS:
#    create          Create authorization
#    delete          Delete authorization
#    list, find, ls  List authorizations
#    active          Active authorization
#    inactive        Inactive authorization
#
# OPTIONS:
#    --help, -h  show help


class InfluxAuth(object):
    """
    """

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.host = module.params.get("host")
        self.host = module.params.get("host")
        self.state = module.params.get("state")
        self.host = module.params.get("host")
        self.skip_verify = module.params.get("skip_verify")
        self.http_debug = module.params.get("http_debug")
        self.configs_path = module.params.get("configs_path")
        self.active_config = module.params.get("active_config")
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
            rc=1,
            failed=False,
            changed=False,
            ansible_module_results="none"
        )
        args = []
        args.append(self._influx)
        args.append("auth")
        args.append(self.state)

        if self.state == "create":
            args += self._auth_create()

        self.module.log(msg=f"  args: '{args}'")

        return result

    def _auth_create(self):
        """
        """
        args = []

        if self.name:
            args.append("--name")
            args.append(self.name)

        if self.description:
            args.append("--description")
            args.append(self.description)

        return args

    def _auth_delete(self):
        """
        """

    def _auth_list(self):
        """
        """

    def _auth_update(self):
        """
        """

    def _auth_password(self):
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
            state=dict(
                default="create",
                choices=["create", "delete", "list", "active", "inactive"]
            ),
            host=dict(
                required=True,
                type="str"
            ),
            skip_verify=dict(
                required=False,
                type="bool"
            ),
            http_debug=dict(
                required=False,
                type="bool"
            ),
            configs_path=dict(
                required=False,
                type="path"
            ),
            active_config=dict(
                required=False,
                type="list",
                default=[]
            ),
            token=dict(
                required=False,
                type="str"
            ),
            name=dict(
                required=False,
                type="str"
            ),
            id=dict(
                required=False,
                type="id"
            ),
            description=dict(
                required=False,
                type="str"
            ),
            members=dict(
                required=False,
                type="dict"
            ),
        ),
        supports_check_mode=False,
    )

    o = InfluxAuth(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
