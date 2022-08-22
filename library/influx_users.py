#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
import json

# # influx user --help
# NAME:
#    influx user - User management commands
#
# USAGE:
#    influx user command [command options] [arguments...]
#
# COMMANDS:
#    create          Create user
#    delete          Delete user
#    list, find, ls  List users
#    update
#    password
#
# OPTIONS:
#    --help, -h  show help


class InfluxUser(object):
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
        self.users = module.params.get("users")

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
            msg="Influxdb users ..."
        )

        rc, out, err = self.user_list()

        _out = json.loads(out)

        users = list(
            map(lambda d: d.get('name', 'default value'), _out)
        )
        self.module.log(msg=f" - existion users: {', '.join(users)}")

        for username, v in self.users.items():
            """
            """
            _state = v.get("state", "create")
            # self.module.log(msg=f"   org: '{organization}'")
            # self.module.log(msg=f"     values: '{v}'")

            if _state == "create":
                """
                  create new user
                """
                if username in users:
                    res = {}
                    res[username] = dict(
                        state=f"user: '{username}' already created."
                    )
                    result_state.append(res)
                    continue

                rc, out, err = self.user_create(username, v)

                if rc == 0:
                    res = {}
                    res[username] = dict(
                        state=f"user: '{username}' successfuly created."
                    )
                    result_state.append(res)
                else:
                    res = {}
                    res[username] = dict(
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

    def user_list(self, user_name=None):
        """
        """
        args = []
        args.append(self._influx)
        args.append("user")
        args.append("list")

        if user_name:
            args.append("--name")
            args.append(user_name)

        args += self._common_options()

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def user_create(self, user_name, values):
        """
            # influx user create --help
            NAME:
               influx user create - Create user

            USAGE:
               influx user create [command options] [arguments...]

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
               --org-id value              The ID of the organization [$INFLUX_ORG_ID]
               --org value, -o value       The name of the organization [$INFLUX_ORG]
               --name value, -n value      The user name [$INFLUX_NAME]
               --password value, -p value  The user password
        """
        organisation = values.get("organization", {}).get("name")
        password = values.get("password")

        args = []
        args.append(self._influx)
        args.append("user")
        args.append("create")
        args.append("--name")
        args.append(user_name)
        args.append("--org")
        args.append(organisation)
        args.append("--password")
        args.append(password)

        args += self._common_options()

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def _user_delete(self):
        """
        """
        pass

    def _user_update(self):
        """
        """
        pass

    def _user_password(self):
        """
        """
        pass

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
            users=dict(
                required=True,
                type="dict"
            )
        ),
        supports_check_mode=False,
    )

    o = InfluxUser(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
