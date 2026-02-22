#!/usr/bin/python3
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
    """ """

    def __init__(self, module):
        """
        Initialize all needed Variables
        """
        self.module = module
        self.module.log("InfluxPing::__init__()")

        self.host = module.params.get("host")
        self.main_version = module.params.get("main_version")
        self.skip_verify = module.params.get("skip_verify")
        self.http_debug = module.params.get("http_debug")
        self.configs_path = module.params.get("configs_path")
        self.active_config = module.params.get("active_config")

    def run(self):
        """
        runner
        """
        self.module.log("InfluxPing::run()")

        self.module.log(f"  - main_version: {int(self.main_version)}")

        if int(self.main_version) == 2:
            """ """
            _influx_bin = self.module.get_bin_path("influx", required=False)

            self.module.log(f"  - _influx_bin: {_influx_bin}")

            if not _influx_bin:
                return dict(
                    failed=True,
                    rc=10,
                    msg=f"influx-cli is not installed.",
                    stderr=f"influx-cli is not installed.",
                )

            args = []
            args.append(_influx_bin)
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
                    stderr=err,
                )
            else:
                return dict(
                    failed=True,
                    changed=False,
                    rc=rc,
                    cmd=" ".join(args),
                    stdout=out,
                    stderr=err,
                )

        if int(self.main_version) == 3:
            """ """
            rc = 1
            status_code, result, err = self._request(url=f"{self.host}/ping")

            _version = result.get("version", None)

            if int(status_code) == 200:
                rc = 0

            return dict(
                failed=(rc == 1),
                changed=False,
                rc=rc,
                # stdout=result,
            )

    def _request(self, url):
        """ """
        import requests

        self.module.log(msg=f"InfluxPing::_request(url={url})")

        try:
            response = requests.get(url, timeout=15)

            self.module.log(msg=f"response: {response}")

            response.raise_for_status()

            self.module.log(msg=f" text    : {response.text} / {type(response.text)}")
            self.module.log(
                msg=f" json    : {response.json()} / {type(response.json())}"
            )
            self.module.log(msg=f" headers : {response.headers}")
            self.module.log(msg=f" code    : {response.status_code}")
            self.module.log(
                msg="------------------------------------------------------------------"
            )

            return (response.status_code, response.json(), None)

        except requests.exceptions.HTTPError as e:
            self.module.log(msg=f"ERROR   : {e}")

            status_code = e.response.status_code
            status_message = e.response.json()
            # self.module.log(msg=f" status_message : {status_message} / {type(status_message)}")
            # self.module.log(msg=f" status_message : {e.response.json()}")

            return (status_code, None, status_message)

        except ConnectionError as e:
            error_text = (
                f"{type(e).__name__} {(str(e) if len(e.args) == 0 else str(e.args[0]))}"
            )
            self.module.log(msg=f"ERROR   : {error_text}")

            self.module.log(
                msg="------------------------------------------------------------------"
            )
            return (500, None, error_text)

        except Exception as e:
            self.module.log(msg=f"ERROR   : {e}")
            # self.module.log(msg=f" text    : {response.text} / {type(response.text)}")
            # self.module.log(msg=f" json    : {response.json()} / {type(response.json())}")
            # self.module.log(msg=f" headers : {response.headers}")
            # self.module.log(msg=f" code    : {response.status_code}")
            # self.module.log(msg="------------------------------------------------------------------")

            return (response.status_code, None, response.json())

        except requests.exceptions.RequestException as e:
            error = f"Request failed: {e}"
            self.module.log(error)
            return (419, [], error)

        except ValueError as e:
            error = f"Error parsing the JSON: {e}"
            self.module.log(error)
            return (419, [], error)

        return (200, result, None)

    def _common_options(self):
        """ """
        self.module.log("InfluxPing::_common_options()")

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
        self.module.log(f"InfluxPing::_exec(commands: {commands}, check_rc: {check_rc})")

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
            host=dict(required=True, type="str"),
            skip_verify=dict(required=False, type="bool"),
            http_debug=dict(required=False, type="bool"),
            configs_path=dict(required=False, type="path"),
            active_config=dict(required=False, type="list", default=[]),
            main_version=dict(
                required=True,
                type="str",
            ),
        ),
        supports_check_mode=False,
    )

    i = InfluxPing(module)
    result = i.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == "__main__":
    main()
