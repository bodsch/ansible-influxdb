#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import urllib3
import requests
import json
import os
import datetime

from packaging.version import parse as parseVersion
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: urbanterror_api

short_description: ""

description: ""

version_added: "0.1.0"
author: "..."
options:

'''

EXAMPLES = r"""

"""

RETURN = r"""


"""


class GithubLatest(object):
    """
    Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self.project = module.params.get("project")
        self.repository = module.params.get("repository")
        self.github_username = module.params.get("user")
        self.github_password = module.params.get("password")
        self.major_version = module.params.get("major_version")
        self.without_beta = module.params.get("without_beta")
        self.only_version = module.params.get("only_version")
        self.cache_minutes = int(module.params.get("cache"))
        self.github_releases = module.params.get("github_releases")
        self.github_tags = module.params.get("github_tags")

        self.github_url = f"https://api.github.com/repos/{self.project}/{self.repository}"

        if self.github_tags:
            self.github_releases = False
            self.github_url = f"{self.github_url}/tags"

        if self.github_releases:
            self.github_url = f"{self.github_url}/releases"

        self.cache_directory = f"{Path.home()}/.ansible/cache/github/{self.project}"
        self.cache_file_name = os.path.join(self.cache_directory, f"{self.repository}_latest.json")
        # self.cache_minutes = 60

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def run(self):
        """
        """
        self.__create_directory(self.cache_directory)
        data = self.latest_information()

        if self.github_releases:
            releases = [v.get("tag_name") for v in data if v.get('tag_name', None)]
        else:
            releases = [v.get("name") for v in data if v.get('name', None)]

        # filter beta version
        if self.without_beta:
            releases = [x for x in releases if "beta" not in x]

        releases = self.version_sort(releases)
        latest_release = releases[-1:][0]

        if self.only_version:
            latest_release = latest_release.replace("v", "").replace("V", "")

        self.module.log(msg=f"latest_release: {latest_release}")

        return dict(
            failed = False,
            latest_release = latest_release
        )

    def latest_information(self):
        """
        """
        output = None

        if os.path.exists(self.cache_file_name):
            self.module.log(msg=f" - read cache file  {self.cache_file_name}")

            now           = datetime.datetime.now()
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(self.cache_file_name))
            diff          = now - creation_time
            # define the difference from now to the creation time in minutes
            cached_time   = diff.total_seconds() / 60
            out_of_cache  = cached_time > self.cache_minutes

            # self.module.log(msg=f" - now            {now}")
            # self.module.log(msg=f" - creation_time  {creation_time}")
            # self.module.log(msg=f" - cached since   {cached_time}")
            # self.module.log(msg=f" - out of cache   {out_of_cache}")

            if out_of_cache:
                os.remove(self.cache_file_name)
            else:
                with open(self.cache_file_name, "r") as f:
                    output = json.loads(f.read())

                    return output

        if not output:
            self.module.log(msg=f" - read from url  {self.github_url}")

            status_code, output = self.__call_url()

            if status_code == 200:
                self.save_latest_information(output)

                return output

    def save_latest_information(self, data):
        """
        """
        with open(self.cache_file_name, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def __create_directory(self, dir):
        """
        """
        try:
            os.makedirs(dir, exist_ok=True)
        except FileExistsError:
            pass

        if os.path.isdir(dir):
            return True
        else:
            return False

    def __call_url(self, method='GET', data=None):
        """
        """
        response = None

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json;charset=utf-8"
        }

        try:
            authentication = (self.github_username, self.github_password)

            if method == "GET":
                response = requests.get(
                    self.github_url,
                    headers=headers,
                    auth=authentication
                )

            else:
                print("unsupported")
                pass

            response.raise_for_status()

            # self.module.log(msg=f" text    : {response.text} / {type(response.text)}")
            # self.module.log(msg=f" json    : {response.json()} / {type(response.json())}")
            # self.module.log(msg=f" headers : {response.headers}")
            # self.module.log(msg=f" code    : {response.status_code}")
            # self.module.log(msg="------------------------------------------------------------------")

            return response.status_code, response.json()

        except requests.exceptions.HTTPError as e:
            self.module.log(msg=f"ERROR   : {e}")

            status_code = e.response.status_code
            status_message = e.response.json()
            # self.module.log(msg=f" status_message : {status_message} / {type(status_message)}")
            # self.module.log(msg=f" status_message : {e.response.json()}")

            return status_code, status_message

        except ConnectionError as e:
            error_text = f"{type(e).__name__} {(str(e) if len(e.args) == 0 else str(e.args[0]))}"
            self.module.log(msg=f"ERROR   : {error_text}")

            self.module.log(msg="------------------------------------------------------------------")
            return 500, error_text

        except Exception as e:
            self.module.log(msg=f"ERROR   : {e}")
            # self.module.log(msg=f" text    : {response.text} / {type(response.text)}")
            # self.module.log(msg=f" json    : {response.json()} / {type(response.json())}")
            # self.module.log(msg=f" headers : {response.headers}")
            # self.module.log(msg=f" code    : {response.status_code}")
            # self.module.log(msg="------------------------------------------------------------------")

            return response.status_code, response.json()

    def version_sort(self, version_list):
        """
        """
        version_list.sort(key = parseVersion)

        return version_list


def main():
    """
    """
    module = AnsibleModule(
        argument_spec=dict(
            project=dict(
                required=True,
                type=str
            ),
            repository=dict(
                required=True,
                type=str
            ),
            github_releases=dict(
                required=False,
                default=True,
            ),
            github_tags=dict(
                required=False,
                default=False,
            ),
            user=dict(
                required=False,
                type=str
            ),
            password=dict(
                required=False,
                type=str,
                no_log=True
            ),
            major_version=dict(
                required=False,
            ),
            without_beta=dict(
                required=False,
                type=bool,
                default=True
            ),
            only_version=dict(
                required=False,
                type=bool,
                default=True
            ),
            cache=dict(
                required=False,
                default=60
            )
        ),
        supports_check_mode=False,
    )

    api = GithubLatest(module)
    result = api.run()

    module.log(msg=f"= result : {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
