#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
import json

# # influx org --help
# NAME:
#    influx org - Organization management commands
#
# USAGE:
#    influx org command [command options] [arguments...]
#
# COMMANDS:
#    create          Create organization
#    delete          Delete organization
#    list, find, ls  List organizations
#    members         Organization membership commands
#    update          Update organization
#
# OPTIONS:
#    --help, -h  show help


class InfluxOrganizations(object):
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

        self.organizations = module.params.get("organizations")

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
            msg="Influxdb organisations ..."
        )

        rc, out, err = self.organization_list()

        _out = json.loads(out)

        organisations = list(
            map(lambda d: d.get('name', 'default value'), _out)
        )
        self.module.log(msg=f" - existion organisations: {', '.join(organisations)}")

        # self.module.log(msg=" - update existing organization")
        # for o in organisations:
        #
        #     for d in _out:
        #         organization_name = d.get("name")
        #         organization_id = d.get("id")
        #         organization_descr = d.get("description")
        #
        #         if organization_name == o:
        #             print(d)
        #             #if organization_descr != self.organizations[organization_name].get("description", None):
        #             #    rc, out, err = self.organization_update(args, _existingorganization_name, _existingorganization_id, v)
        #             break

        for organization, v in self.organizations.items():
            """
            """
            _state = v.get("state", "create")
            # self.module.log(msg=f"   org: '{organization}'")
            # self.module.log(msg=f"     values: '{v}'")

            if _state == "create":
                """
                  create new organisation
                """
                if organization in organisations:
                    res = {}
                    res[organization] = dict(
                        state=f"organization: '{organization}' already created."
                    )
                    result_state.append(res)
                    continue

                rc, out, err = self.organization_create(organization, v)

                if rc == 0:
                    res = {}
                    res[organization] = dict(
                        state=f"bucket: '{organization}' successfuly created."
                    )
                    result_state.append(res)
                else:
                    res = {}
                    res[organization] = dict(
                        state=err,
                        failed=True
                    )
                    result_state.append(res)

            if _state == "delete":
                """
                  delete existing organisation
                """
                rc, out, err = self.organization_delete(organization)

                if rc == 0:
                    res = {}
                    res[organization] = dict(
                        state=f"bucket: '{organization}' successfuly deleted."
                    )
                    result_state.append(res)
                else:
                    res = {}
                    res[organization] = dict(
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

    def organization_list(self, org_name=None):
        """
        """
        args = []
        args.append(self._influx)
        args.append("org")
        args.append("list")

        if org_name:
            args.append("--name")
            args.append(org_name)

        args += self._common_options()

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def organization_create(self, organization, values):
        """

        """
        description = values.get("description")

        args = []
        args.append(self._influx)
        args.append("org")
        args.append("create")

        args.append("--name")
        args.append(organization)

        if description:
            args.append("--description")
            args.append(description)

        args += self._common_options()

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def organization_delete(self, org_name):
        """
            # influx org delete --help
            NAME:
               influx org delete - Delete organization

            USAGE:
               influx org delete [command options] [arguments...]

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
               --id value, -i value  The organization ID [$INFLUX_ORG_ID]
        """
        rc, out, err = self.organization_list(org_name)

        if rc == 0:
            """
            """
            _out = json.loads(out)

            org_id = _out[0].get("id")

            args = []
            args.append(self._influx)
            args.append("org")
            args.append("delete")

            args.append("--id")
            args.append(org_id)

            args += self._common_options()

            rc, out, err = self._exec(args, False)

            return rc, out, err
        else:
            return 0, f"organisation {org_name} not found", ""

    def organization_update(self, org_name, org_id, values):
        """
            # influx org update --help
            NAME:
               influx org update - Update organization

            USAGE:
               influx org update [command options] [arguments...]

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
               --id value, -i value           The organization ID [$INFLUX_ORG_ID]
               --name value, -n value         New name to set on the organization [$INFLUX_ORG]
               --description value, -d value  New description to set on the organization [$INFLUX_ORG_DESCRIPTION]
        """
        description = values.get("description")

        args = []
        args.append(self._influx)
        args.append("org")
        args.append("update")

        args.append("--id")
        args.append(org_id)

        if org_name:
            args.append("--name")
            args.append(org_name)

        if description:
            args.append("--description")
            args.append(description)

        # args += self._args_update(org_id, org_name, values.get("description"))

        args += self._common_options()

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def organization_members(self):
        """
            # influx org members --help
            NAME:
               influx org members - Organization membership commands

            USAGE:
               influx org members command [command options] [arguments...]

            COMMANDS:
               add             Add organization member
               list, find, ls  List organization members
               remove          Remove organization member
          # -------------------------------------------------------
            # influx org members add --help
            NAME:
               influx org members add - Add organization member

            USAGE:
               influx org members add [command options] [arguments...]

            COMMON OPTIONS:
               --host value                     HTTP address of InfluxDB [$INFLUX_HOST]
               --skip-verify                    Skip TLS certificate chain and host name verification [$INFLUX_SKIP_VERIFY]
               --configs-path value             Path to the influx CLI configurations [$INFLUX_CONFIGS_PATH]
               --active-config value, -c value  Config name to use for command [$INFLUX_ACTIVE_CONFIG]
               --http-debug
               --token value, -t value          Token to authenticate request [$INFLUX_TOKEN]

            OPTIONS:
               --member value, -m value  The member ID
               --name value, -n value    The organization name [$INFLUX_ORG]
               --id value, -i value      The organization ID [$INFLUX_ORG_ID]
               --owner                   Set new member as an owner
          # -------------------------------------------------------
            # influx org members remove --help
            NAME:
               influx org members remove - Remove organization member

            USAGE:
               influx org members remove [command options] [arguments...]

            COMMON OPTIONS:
               --host value                     HTTP address of InfluxDB [$INFLUX_HOST]
               --skip-verify                    Skip TLS certificate chain and host name verification [$INFLUX_SKIP_VERIFY]
               --configs-path value             Path to the influx CLI configurations [$INFLUX_CONFIGS_PATH]
               --active-config value, -c value  Config name to use for command [$INFLUX_ACTIVE_CONFIG]
               --http-debug
               --token value, -t value          Token to authenticate request [$INFLUX_TOKEN]

            OPTIONS:
               --member value, -m value  The member ID
               --name value, -n value    The organization name [$INFLUX_ORG]
               --id value, -i value      The organization ID [$INFLUX_ORG_ID]
          # -------------------------------------------------------
            # influx org members list --help
            NAME:
               influx org members list - List organization members

            USAGE:
               influx org members list [command options] [arguments...]

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
               --name value, -n value  The organization name [$INFLUX_ORG]
               --id value, -i value    The organization ID [$INFLUX_ORG_ID]
          # -------------------------------------------------------
        """
        args = []

        for m in self.members.items():
            self.module.log(msg=f"  member: '{m}'")

        return args

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
            organizations=dict(
                required=True,
                type="dict"
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
        ),
        supports_check_mode=False,
    )

    o = InfluxOrganizations(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
