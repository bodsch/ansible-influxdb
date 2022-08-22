#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

# # influx ping --help
# NAME:
#     ping - Check the InfluxDB /health endpoint
#
# USAGE:
#     ping [command options] [arguments...]
#
# COMMON OPTIONS:
#    --host value                     HTTP address of InfluxDB [$INFLUX_HOST]
#    --skip-verify                    Skip TLS certificate chain and host name verification [$INFLUX_SKIP_VERIFY]
#    --configs-path value             Path to the influx CLI configurations [$INFLUX_CONFIGS_PATH]
#    --active-config value, -c value  Config name to use for command [$INFLUX_ACTIVE_CONFIG]
#    --http-debug
#
# OPTIONS:


class InfluxPing(object):
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

        self._influx = module.get_bin_path("influx", True)

    def run(self):
        """
          runner
        """
        args = []
        args.append(self._influx)
        args.append("ping")

        args += self._common_options()

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
            return dict(
                failed=True,
                changed=False,
                rc=rc,
                cmd=" ".join(args),
                stdout=out,
                stderr=err
            )

    def _common_options(self):
        """
        """
        args = []
        args.append("--host")
        args.append(self.host)

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

        return args

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
        ),
        supports_check_mode=False,
    )

    i = InfluxPing(module)
    result = i.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
