#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2026, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from pathlib import Path
from dataclasses import dataclass
from typing import Any, Optional, Dict, Tuple, Union, List
# from urllib.error import HTTPError, URLError
# from urllib.request import Request, urlopen


from ansible.module_utils.basic import AnsibleModule
from packaging.version import Version

from ansible.module_utils.urls import fetch_url
# from ansible_collections.bodsch.core.plugins.module_utils.checksum import Checksum
from ansible_collections.bodsch.core.plugins.module_utils.directory import (
    create_directory,
)

class InfluxDb3Token:
    """ """

    def __init__(self, module: AnsibleModule) -> None:
        """
        Initialize all needed Variables
        """
        self.module = module
        self.module.log("InfluxDb3Token::__init__()")

        self.version: str = module.params.get("version")
        self.host: str = module.params.get("host")
        self.auth_enabled: bool = bool(module.params.get("auth_enabled"))

        self.timeout: int = int(module.params.get("timeout") or 15)
        self.validate_certs: bool = bool(
            module.params.get("validate_certs") if module.params.get("validate_certs") is not None else True
        )
        self.user_agent: str = str(module.params.get("user_agent") or "ansible-influxdb-token")

        self.cache_directory: Path = Path.home() / ".ansible" / "influxdb3"


    def run(self):
        """
        runner
        """
        self.module.log("InfluxDb3Token::run()")

        create_directory(str(self.cache_directory))

        result = dict(
            rc=0,
            failed=False,
            changed=False,
            ansible_module_results="inital state",
        )

        # Version("1.2.3").major
        if Version(self.version).major == 3:
            """ """
            if self.auth_enabled:
                return self.createToken()
            else:
                return dict(
                    failed=False,
                    changed=False,
                    msg="authentication is disabled."
                )

    def createToken(self):
        """ """
        self.module.log("InfluxDb3Token::createToken()")

        _url = f"{self.host}/api/v3/configure/token/admin"

        result = self._fetch(
            url=_url,
            method="POST"
        )

        self.module.log(f"result: {result}")


    # ------------------------------------------------------------------------------------------
    # private API

    def _fetch(self, url: str, method: str, headers: Optional[Dict[str, str]] = None) -> Tuple[Any, Dict[str, Any]]:
        """
        Wrapper around fetch_url for compatibility across ansible-core versions.

        Newer ansible-core versions accept validate_certs kwarg.
        Older versions read validate_certs from module.params and do not accept the kwarg.
        """
        self.module.log(f"InfluxDb3Token::_fetch(url: {url}, method: {method}, headers: {headers})")

        hdrs = headers or {}
        try:
            return fetch_url(
                self.module,
                url,
                method=method,
                timeout=self.timeout,
                headers=hdrs,
                validate_certs=self.validate_certs,
            )
        except TypeError:
            self.module.params.setdefault("validate_certs", self.validate_certs)
            return fetch_url(
                self.module,
                url,
                method=method,
                timeout=self.timeout,
                headers=hdrs,
            )

def main():
    """ """
    module = AnsibleModule(
        argument_spec=dict(
            version=dict(required=True, type="str"),
            host=dict(required=True, type="str"),
            auth_enabled=dict(required=True, type="bool"),
            force=dict(required=False, type="bool"),
        ),
        supports_check_mode=False,
    )

    o = InfluxDb3Token(module)
    result = o.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()


"""


1) Admin-Token erstellen
curl -sS -X POST "http://127.0.0.1:8181/api/v3/configure/token/admin"

2) (Optional) Named Admin-Token erstellen
curl -sS -X POST "http://127.0.0.1:8181/api/v3/configure/token/named_admin" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"token_name":"ci-admin","expiry_secs":31536000}'

3) Database erstellen (v3-nativ)
curl -sS -X POST "http://127.0.0.1:8181/api/v3/configure/database" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"db":"sensors","retention_period":"7d"}'

4) Schreiben über v2-kompatiblen Endpoint (Bucket == Database)
curl -sS -X POST "http://127.0.0.1:8181/api/v2/write?bucket=sensors&precision=s" \
  -H "Authorization: Token ${DB_OR_ADMIN_TOKEN}" \
  --data-binary 'cpu,host=instance usage=0.5 1710000000'

bucket ist hier ein Database-Name; DB wird bei Bedarf erstellt.


"""
