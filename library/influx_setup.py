#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function
# import os
# import sys

from ansible.module_utils.basic import AnsibleModule

# # influx setup --help
# NAME:
#     setup - Setup instance with initial user, org, bucket
#
# USAGE:
#     setup [command options] [arguments...]
#
# COMMON OPTIONS:
#    --host value                     HTTP address of InfluxDB [$INFLUX_HOST]
#    --skip-verify                    Skip TLS certificate chain and host name verification [$INFLUX_SKIP_VERIFY]
#    --configs-path value             Path to the influx CLI configurations [$INFLUX_CONFIGS_PATH]
#    --active-config value, -c value  Config name to use for command [$INFLUX_ACTIVE_CONFIG]
#    --http-debug
#    --json                           Output data as JSON [$INFLUX_OUTPUT_JSON]
#    --hide-headers                   Hide the table headers in output data [$INFLUX_HIDE_HEADERS]
#
# OPTIONS:
#    --username value, -u value   Name of initial user to create
#    --password value, -p value   Password to set on initial user
#    --token value, -t value      Auth token to set on the initial user [$INFLUX_TOKEN]
#    --org value, -o value        Name of initial organization to create
#    --bucket value, -b value     Name of initial bucket to create
#    --retention value, -r value  Duration initial bucket will retain data, or 0 for infinite
#    --force, -f                  Skip confirmation prompt
#    --name value, -n value       Name to set on CLI config generated for the InfluxDB instance, required if other configs exist


class InfluxSetup(object):
    """
    """

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.host = module.params.get("host")
        self.skip_verify = module.params.get("skip_verify")
        self.http_debug = module.params.get("http_debug")
        self.configs_path = module.params.get("configs_path")
        self.active_config = module.params.get("active_config")
        self.name = module.params.get("name")
        self.username = module.params.get("username")
        self.password = module.params.get("password")
        self.token = module.params.get("token")
        self.org = module.params.get("org")
        self.bucket = module.params.get("bucket")
        self.retention = module.params.get("retention")
        self.force = module.params.get("force")

        self._influx = module.get_bin_path("influx", True)

    def run(self):
        """
          runner
        """
        result = dict(
            rc=0,
            failed=False,
            changed=False,
            ansible_module_results="none",
        )

        args = []
        args.append(self._influx)
        args.append("setup")
        args.append("--host")
        args.append(self.host)
        args.append("--json")
        args.append("--hide-headers")
        args.append("--username")
        args.append(self.username)
        args.append("--password")
        args.append(self.password)

        if self.skip_verify:
            args.append("--skip-verify")

        if self.http_debug:
            args.append("--http-debug")

        if self.configs_path:
            args.append("--configs-path")
            args.append(self.configs_path)

        if len(self.active_config) > 0:
            for a in self.active_config:
                args.append("--active-config")
                args.append(a)

        if self.token:
            args.append("--token")
            args.append(self.token)

        if self.org:
            args.append("--org")
            args.append(self.org)

        if self.bucket:
            args.append("--bucket")
            args.append(self.bucket)

        if self.retention:
            args.append("--retention")
            args.append(self.retention)

        if self.force:
            args.append("--force")

        if self.name:
            args.append("--name")
            args.append(self.name)

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        if rc == 0:
            return dict(
                failed=False,
                changed=False,
                rc=rc,
                cmd=" ".join(args),
                stdout=out,
                stderr=err
            )
        else:
            failed = True

            if "has already been set up" in err:
                failed = False

            return dict(
                failed=failed,
                changed=False,
                rc=rc,
                cmd=" ".join(args),
                stdout=out,
                stderr=err
            )

        return result

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
    """
    """
    module = AnsibleModule(
        argument_spec=dict(
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
            name=dict(
                required=False,
                type="str"
            ),
            username=dict(
                required=True,
                type="str"
            ),
            password=dict(
                required=True,
                type="str",
                no_log=True
            ),
            token=dict(
                required=False,
                type="str"
            ),
            org=dict(
                required=True,
                type="str"
            ),
            bucket=dict(
                required=True,
                type="str"
            ),
            retention=dict(
                required=False,
                type="int",
                default=0
            ),
            force=dict(
                required=False,
                type="bool"
            ),

        ),
        supports_check_mode=False,
    )

    o = InfluxSetup(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
