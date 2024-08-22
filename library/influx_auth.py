#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
import json

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

        self.state = module.params.get("state")
        self.host = module.params.get("host")
        self.skip_verify = module.params.get("skip_verify")
        self.http_debug = module.params.get("http_debug")
        self.configs_path = module.params.get("configs_path")
        self.active_config = module.params.get("active_config")
        self.token = module.params.get("token")
        self.authentications = module.params.get("authentications")

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
            msg="Influxdb authentications ..."
        )

        self.module.log(msg=" - list existing authentications")

        rc, out, err = self._auth_list()

        _out = json.loads(out)

        authentications = list(
            map(lambda d: d.get('token', 'default value'), _out)
        )
        self.module.log(msg=f" - existion authentications: {', '.join(authentications)}")

        self.module.log(msg=" - create new authentications")
        for username, v in self.authentications.items():
            """
            """
            _state = v.get("state", "create")
            # self.module.log(msg=f"   org: '{organization}'")
            # self.module.log(msg=f"     values: '{v}'")

            if _state and v.get("organization", {}).get("admin", False):
                """
                  create new authentication
                """
                rc, out, err = self._auth_create(username, v)

                if rc == 0:
                    res = {}
                    res[username] = dict(
                        state=f"authentication for '{username}' successfuly created."
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

    def _auth_list(self, user_name=None):
        """
        """
        args = []
        args.append(self._influx)
        args.append("auth")
        args.append("list")

        if user_name:
            args.append("--name")
            args.append(user_name)

        args += self._common_options()

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def _auth_create(self, user_name, values):
        """
            # influx auth create --help
            NAME:
               influx auth create - Create authorization

            USAGE:
               influx auth create [command options] [arguments...]

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
               --user value, -u value         The user name
               --description value, -d value  Token description
               --write-bucket value           The bucket id
               --read-bucket value            The bucket id
               --operator                     Grants all permissions in all organizations
               --all-access                   Grants all permissions in a single organization
               --read-authorizations          Grants the permission to read authorizations
               --write-authorizations         Grants the permission to create or update authorizations
               --read-buckets                 Grants the permission to perform read actions against organization buckets
               --write-buckets                Grants the permission to perform mutative actions against organization buckets
               --read-dashboards              Grants the permission to read dashboards
               --write-dashboards             Grants the permission to create or update dashboards
               --read-orgs                    Grants the permission to read organizations
               --write-orgs                   Grants the permission to create organizations
               --read-tasks                   Grants the permission to read tasks
               --write-tasks                  Grants the permission to create or update tasks
               --read-telegrafs               Grants the permission to read telegraf configs
               --write-telegrafs              Grants the permission to create telegraf configs
               --read-users                   Grants the permission to read users
               --write-users                  Grants the permission to create or update users
               --read-variables               Grants the permission to read variables
               --write-variables              Grants the permission to create or update variables
               --read-secrets                 Grants the permission to read secrets
               --write-secrets                Grants the permission to create or update secrets
               --read-labels                  Grants the permission to read labels
               --write-labels                 Grants the permission to create or update labels
               --read-views                   Grants the permission to read views
               --write-views                  Grants the permission to create or update views
               --read-documents               Grants the permission to read documents
               --write-documents              Grants the permission to create or update documents
               --read-notificationRules       Grants the permission to read notificationRules
               --write-notificationRules      Grants the permission to create or update notificationRules
               --read-notificationEndpoints   Grants the permission to read notificationEndpoints
               --write-notificationEndpoints  Grants the permission to create or update notificationEndpoints
               --read-checks                  Grants the permission to read checks
               --write-checks                 Grants the permission to create or update checks
               --read-dbrp                    Grants the permission to read dbrp
               --write-dbrp                   Grants the permission to create or update dbrp
               --read-annotations             Grants the permission to read annotations
               --write-annotations            Grants the permission to create or update annotations
               --read-sources                 Grants the permission to read sources (OSS only)
               --write-sources                Grants the permission to create or update sources (OSS only)
               --read-scrapers                Grants the permission to read scrapers (OSS only)
               --write-scrapers               Grants the permission to create or update scrapers (OSS only)
               --read-notebooks               Grants the permission to read notebooks (OSS only)
               --write-notebooks              Grants the permission to create or update notebooks (OSS only)
               --read-remotes                 Grants the permission to read remotes (OSS only)
               --write-remotes                Grants the permission to create or update remotes (OSS only)
               --read-replications            Grants the permission to read replications (OSS only)
               --write-replications           Grants the permission to create or update replications (OSS only)
               --read-instance                Grants the permission to read instance (OSS only)
               --write-instance               Grants the permission to create or update instance (OSS only)
               --read-flows                   Grants the permission to read flows (Cloud only)
               --write-flows                  Grants the permission to create or update flows (Cloud only)
        """
        self.module.log(msg=f"create authentication for {user_name}")

        organisation = values.get("organization", {}).get("name")
        org_admin = values.get("organization", {}).get("admin", False)
        operator = values.get("operator", False)

        args = []
        args.append(self._influx)
        args.append("auth")
        args.append("create")
        args.append("--json")
        args.append("--user")
        args.append(user_name)

        if operator:
            args.append("--operator")
        elif org_admin:
            args.append("--org")
            args.append(organisation)
            args.append("--all-access")

        args += self._common_options()

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def _args_create(self):
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

    def _args_delete(self):
        """
        """

    def _args_list(self, user_name=None, user_id=None):
        """
        """
        pass

    def _args_update(self):
        """
        """
        pass

    def _args_password(self):
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
            authentications=dict(
                required=True,
                type="dict"
            )
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
