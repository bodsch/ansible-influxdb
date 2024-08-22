#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

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


class InfluxOrg(object):
    """
    """

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.host = module.params.get("host")
        self.state = module.params.get("state")
        self.host = module.params.get("host")
        self.skip_verify = module.params.get("skip_verify")
        self.http_debug = module.params.get("http_debug")
        self.configs_path = module.params.get("configs_path")
        self.active_config = module.params.get("active_config")
        self.token = module.params.get("token")
        self.name = module.params.get("name")
        self.id = module.params.get("id")
        self.description = module.params.get("description")
        self.members = module.params.get("members")

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
        args.append("org")
        args.append(self.state)

        if self.state == "create":
            args += self._org_create()

        if self.state == "delete":
            args += self._org_delete()

        if self.state == "list":
            args += self._org_list()

        if self.state == "members":
            args += self._org_members()

        if self.state == "update":
            args += self._org_update()

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

        self.module.log(msg=f"  args: '{args}'")

        rc, out, err = self._exec(args, False)

        if rc == 0:
            return dict(
                failed=False,
                changed=True,
                rc=rc,
                cmd=" ".join(args),
                stdout=out,
                stderr=err
            )
        else:
            failed = True

            if self.state == "create" and f"organization with name {self.name} already exists" in err:
                failed = False
                rc = 0

            return dict(
                failed=failed,
                changed=False,
                rc=rc,
                cmd=" ".join(args),
                stdout=out,
                stderr=err
            )

        return result

        # args = self._flatten(args)

        # self.module.log(msg=f"  args: '{args}'")

        # return result

    def _org_create(self):
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

        if self.name:
            args.append("--name")
            args.append(self.name)

        if self.description:
            args.append("--description")
            args.append(self.description)

        return args

    def _org_delete(self):
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

        if self.id:
            args.append("--id")
            args.append(self.id)

        return args

    def _org_list(self):
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

        if self.name:
            args.append("--name")
            args.append(self.name)

        if self.id:
            args.append("--id")
            args.append(self.id)

        return args

    def _org_members(self):
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

    def _org_update(self):
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

        if self.id:
            args.append("--id")
            args.append(self.id)

        if self.name:
            args.append("--name")
            args.append(self.name)

        if self.description:
            args.append("--description")
            args.append(self.description)

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
                choices=["create", "delete", "list", "members", "update"]
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

    o = InfluxOrg(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
