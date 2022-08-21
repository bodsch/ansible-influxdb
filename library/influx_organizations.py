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
        result = dict(
            rc=0,
            failed=False,
            changed=False,
            msg="Influxdb organisations ..."
        )

        self.module.log(msg=" - list existing organizations")

        rc, out, err = self._orgs_list()

        _out = json.loads(out)

        organisations = list(
            map(lambda d: d.get('name', 'default value'), _out)
        )
        self.module.log(msg=f" - existion organisations: {', '.join(organisations)}")

        # self.module.log(msg=" - update existing organization")
        # for o in organisations:
        #
        #     for d in _out:
        #         _org_name = d.get("name")
        #         _org_id = d.get("id")
        #         _org_descr = d.get("description")
        #
        #         if _org_name == o:
        #             print(d)
        #             #if _org_descr != self.organizations[_org_name].get("description", None):
        #             #    rc, out, err = self._org_update(args, _existing_org_name, _existing_org_id, v)
        #             break

        """
          create new organisation
        """
        self.module.log(msg=" - create new organisation")
        for organization, v in self.organizations.items():

            if v.get("state") == "create":
                self.module.log(msg=f"   org: '{organization}'")
                self.module.log(msg=f"     values: '{v}'")

                rc, out, err = self._org_create(organization, v)

        """
          delete existing organisation
        """
        self.module.log(msg=" - delete organisation")
        for organization, v in self.organizations.items():
            a = []
            if v.get("state") == "delete":
                self.module.log(msg=f"   org: '{organization}'")
                self.module.log(msg=f"     values: '{v}'")

                rc, out, err = self._org_delete(organization)

        return result

    def _orgs_list(self, org=None):
        """
        """
        args = []
        args.append(self._influx)
        args.append("org")
        args.append("list")
        args.append("--json")

        # args.append("--host")
        # args.append(self.host)
        # args.append("--json")
        # args.append("--hide-headers")
        #
        # if self.token:
        #     args.append("--token")
        #     args.append(self.token)
        #
        # if self.skip_verify:
        #     args.append("--skip-verify")
        #
        # if self.http_debug:
        #     args.append("--http-debug")
        #
        # if self.configs_path:
        #     args.append("--configs-path")
        #     args.append(self.configs_path)
        #
        # if len(self.active_config) > 0:
        #     for a in self.active_config:
        #         args.append("--active-config")
        #         args.append(a)

        args += self._args_list(org)

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def _org_delete(self, org_name):
        """
        """
        self.module.log(msg=f"remove organization {org_name}")

        rc, out, err = self._orgs_list(org_name)

        if rc == 0:
            """
            """
            _out = json.loads(
                out
            )

            self.module.log(msg=f"  out: '{_out}'")

            org_id = _out[0].get("id")

            args = []
            args.append(self._influx)
            args.append("org")
            args.append("delete")
            args.append("--json")

            args += self._args_delete(org_id)

            self.module.log(msg=f"  args: '{args}'")

            rc, out, err = self._exec(args, False)

            return rc, out, err
        else:
            return 0, f"organisation {org_name} not found", ""

    def _org_create(self, organization, v):
        """
        """
        self.module.log(msg=f"create organization {organization}")

        args = []
        args.append(self._influx)
        args.append("org")
        args.append("create")
        args.append("--json")

        self.module.log(msg=f"  args: '{args}'")

        args += self._args_create(organization)

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    def _org_update(self, org_name, org_id, values):
        """
        """
        self.module.log(msg=f"update organization {org_name} / {org_id}")

        args = []
        args.append(self._influx)
        args.append("org")
        args.append("update")
        args.append("--json")

        args += self._args_update(org_id, org_name, values.get("description"))

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        return rc, out, err

    """
        argument extensions
    """

    def _args_create(self, organization, description=None):
        """
            # influx org create --help
            NAME:
               influx org create - Create organization

            USAGE:
               influx org create [command options] [arguments...]

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
               --name value, -n value         Name to set on the new organization
               --description value, -d value  Description to set on the new organization
        """
        args = []

        args.append("--name")
        args.append(organization)

        if description:
            args.append("--description")
            args.append(description)

        return args

    def _args_delete(self, org_id):
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
        args = []

        args.append("--id")
        args.append(org_id)

        return args

    def _args_list(self, org_name=None, org_id=None):
        """
            # influx org list --help
            NAME:
               influx org list - List organizations

            USAGE:
               influx org list [command options] [arguments...]

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
        """
        args = []

        if org_name:
            args.append("--name")
            args.append(org_name)

        if org_id:
            args.append("--id")
            args.append(self.org_id)

        return args

    def _args_members(self):
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

    def _args_update(self, org_id, org_name=None, description=None):
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
        args = []

        args.append("--id")
        args.append(org_id)

        if org_name:
            args.append("--name")
            args.append(org_name)

        if description:
            args.append("--description")
            args.append(description)

        return args

    def _flatten(self, args):
        """
          split and flatten parameter list

          input:  ['--validate', '--log-level debug']
          output: ['--validate', '--log-level', 'debug']
        """
        self.module.log(msg=f"  args : '{args}'")

        parameters = []

        for _parameter in args:
            if ' ' in _parameter:
                _list = _parameter.split(' ')
                for _element in _list:
                    parameters.append(_element)
            else:
                parameters.append(_parameter)

        return parameters

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
