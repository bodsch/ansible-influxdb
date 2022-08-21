#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
import json

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
        self.skip_verify = module.params.get("skip_verify")
        self.http_debug = module.params.get("http_debug")
        self.configs_path = module.params.get("configs_path")
        self.active_config = module.params.get("active_config")
        self.token = module.params.get("token")
        self.buckets = module.params.get("buckets")

        self._influx = module.get_bin_path("influx", True)

    def run(self):
        """
          runner
        """
        result_state = []

        result = dict(
            rc=0,
            failed=False,
            changed=False,
            msg="Influxdb buckets ..."
        )

        self.module.log(msg=" - list existing buckets")

        rc, out, err = self.bucket_list()

        _out = json.loads(out)

        buckets = list(
            map(lambda d: d.get('name', 'default value'), _out)
        )
        self.module.log(msg=f" - existion buckets: {', '.join(buckets)}")





        # define changed for the running tasks
        # migrate a list of dict into dict
        combined_d = {key: value for d in result_state for key, value in d.items()}

        # find all changed and define our variable
        changed = (len({k: v for k, v in combined_d.items() if v.get('changed')}) > 0)
        # find all failed and define our variable
        failed = (len({k: v for k, v in combined_d.items() if v.get('failed')}) > 0)

        result = dict(
            changed=changed,
            failed=failed,
            state=result_state
        )

        return result


    def bucket_list(self, bucket_name=None):
        """
            # influx bucket list --help
            NAME:
               influx bucket list - List buckets

            USAGE:
               influx bucket list [command options] [arguments...]

            COMMON OPTIONS:
               --host value                     HTTP address of InfluxDB [$INFLUX_HOST]
               --skip-verify                    Skip TLS certificate chain and host name verification [$INFLUX_SKIP_VERIFY]
               --configs-path value             Path to the influx CLI configurations [$INFLUX_CONFIGS_PATH]
               --active-config value, -c value  Config name to use for command [$INFLUX_ACTIVE_CONFIG]
               --http-debug
               --json                           Output data as JSON [$INFLUX_OUTPUT_JSON]
               --hide-headers                   Hide the table headers in output data [$INFLUX_HIDE_HEADERS]
               --token value, -t value          Token to authenticate request [$INFLUX_TOKEN]

            OPTIONS:
               --org-id value          The ID of the organization [$INFLUX_ORG_ID]
               --org value, -o value   The name of the organization [$INFLUX_ORG]
               --id value, -i value    The bucket ID, required if name isn't provided
               --name value, -n value  The bucket name, org or org-id will be required by choosing this
               --limit value           Total number of buckets to fetch from the server, or 0 to return all buckets (default: 0)
               --offset value          Number of buckets to skip over in the list (default: 0)
               --page-size value       Number of buckets to fetch per request to the server (default: 20)
        """
        args = []
        args.append(self._influx)
        args.append("bucket")
        args.append("list")

        if bucket_name:
            args.append("--name")
            args.append(bucket_name)

        args += self._default_args()

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def bucket_create(self):
        """
        """

    def _bucket_delete(self):
        """
        """

    def _bucket_update(self):
        """
        """

    def _bucket_password(self):
        """
        """

    def _default_args(self):
        """
        """
        args = []
        args.append("--host")
        args.append(self.host)
        args.append("--json")
        args.append("--hide-headers")

        if self.token:
            args.append("--token")
            args.append(self.token)

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

        # self.module.log(msg=f"  rc : '{rc}'")
        self.module.log(msg=f"  out: '{out}'")
        # self.module.log(msg=f"  err: '{err}'")

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
            token=dict(
                required=False,
                type="str"
            ),
            buckets=dict(
                required=True,
                type="dict"
            )
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
