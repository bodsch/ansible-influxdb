#!/usr/bin/python3
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

        # rc, out, err = self.bucket_list()
        #
        # _out = json.loads(out)
        #
        # global_buckets = list(
        #     map(lambda d: d.get('name', 'default value'), _out)
        # )
        # self.module.log(msg=f" - existion global buckets: {', '.join(global_buckets)}")

        for bucketname, v in self.buckets.items():
            """
            """
            _state = v.get("state", "create")
            _organization = v.get("organization", {}).get("name", None)
            buckets = []

            self.module.log(msg=f"   bucket: '{bucketname}'")
            self.module.log(msg=f"     values: '{v}'")

            rc, out, err = self.bucket_list(bucketname, v)

            if rc == 0:
                _out = json.loads(out)

                buckets = list(
                    map(lambda d: d.get('name', 'default value'), _out)
                )
                self.module.log(msg=f" - existion buckets for org {_organization}: {', '.join(buckets)}")

            if _state == "create":
                """
                  create new bucket
                """
                if bucketname in buckets:
                    res = {}
                    res[bucketname] = dict(
                        state=f"bucket: '{bucketname}' already for organization {_organization} created."
                    )
                    result_state.append(res)
                    continue

                rc, out, err = self.bucket_create(bucketname, v)

                if rc == 0:
                    res = {}
                    res[bucketname] = dict(
                        state=f"bucket: '{bucketname}' successfuly for organization {_organization} created."
                    )
                    result_state.append(res)
                else:
                    res = {}
                    res[bucketname] = dict(
                        state=err,
                        failed=True
                    )
                    result_state.append(res)

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

    def bucket_list(self, bucket_name=None, values={}):
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
        if values and len(values) > 0:
            organisation = values.get("organization", {}).get("name")
        else:
            organisation = None

        args = []
        args.append(self._influx)
        args.append("bucket")
        args.append("list")

        if organisation:
            args.append("--org")
            args.append(organisation)

        if bucket_name:
            args.append("--name")
            args.append(bucket_name)

        args += self._common_options()

        rc, out, err = self._exec(args, False)

        if rc != 0:
            self.module.log(msg=f"args: {args}")

        return rc, out, err

    def bucket_create(self, bucket_name, values):
        """
            # influx bucket create --help
            NAME:
               influx bucket create - Create bucket

            USAGE:
               influx bucket create [command options] [arguments...]

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
               --org-id value                 The ID of the organization [$INFLUX_ORG_ID]
               --org value, -o value          The name of the organization [$INFLUX_ORG]
               --name value, -n value         New bucket name [$INFLUX_BUCKET_NAME]
               --description value, -d value  Description of the bucket that will be created
               --retention value, -r value    Duration bucket will retain data, or 0 for infinite
               --shard-group-duration value   Shard group duration used internally by the storage engine
               --schema-type value            The schema type (implicit, explicit) (default: implicit)
        """
        organisation = values.get("organization", {}).get("name")
        description = values.get("description")
        retention = values.get("retention")
        schema_type = values.get("schema_type")
        shard_group_duration = values.get("shard_group_duration")

        args = []
        args.append(self._influx)
        args.append("bucket")
        args.append("create")
        args.append("--name")
        args.append(bucket_name)
        args.append("--org")
        args.append(organisation)

        if description:
            args.append("--description")
            args.append(description)

        if retention:
            args.append("--retention")
            args.append(retention)

        if shard_group_duration:
            args.append("--shard-group-duration")
            args.append(shard_group_duration)

        if schema_type:
            args.append("--schema-type")
            args.append(schema_type)

        args += self._common_options()

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def _bucket_delete(self):
        """
        """

    def _bucket_update(self):
        """
        """

    def _bucket_password(self):
        """
        """

    def _common_options(self):
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
        # self.module.log(msg=f"  out: '{out}'")
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
