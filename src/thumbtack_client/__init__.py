# Copyright 2021 The MITRE CORPORATION
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import requests
import json

from thumbtack_client import ThumbtackClientException
from thumbtack_client.ThumbtackClientException import ThumbtackClientException
from thumbtack_client.DuplicateMountAttemptException import DuplicateMountAttemptException

logger = logging.getLogger(__name__)


class ThumbtackClient(object):
    """
    Creates the ThumbtackClient object using the `requests.Session class <http://docs.python-requests.org/en/master/api/?highlight=session#request-sessions>`_
    so that its 'delete', 'get', and 'put' methods can be used to send requests.
    """

    def __init__(self, url="http://127.0.0.1:8208"):
        """
        Initializes the ThumbtackClient object with the `requests.Session class <http://docs.python-requests.org/en/master/api/?highlight=session#request-sessions>`_

        Parameters
        ----------
        url : str
            default url is http://127.0.0.1:8208
        """
        self.session = requests.Session()
        self._url = url

    def list_mounted_images(self):
        """
        Returns
        -------
        list
            A list of JSON serialized dictionaries of all mounted images in: 'http://127.0.0.1:8208/mounts/'
        """
        url = f"{self._url}/mounts/"
        response = self._get(url, expected_status=200)
        return response.json()

    def list_images(self):
        """
        Returns
        -------
        list
            A list of JSON serialized dictionaries of all images in: 'http://127.0.0.1:8208/images'
        """
        url = f"{self._url}/images"
        response = self._get(url, expected_status=200)
        return response.json()

    def mount_image(self, image_path, creds=None):
        """
        Parameters
        ----------
        image_path : str
            file path of the image to be mounted

        Returns
        -------
        dict
            requests.Response object : the result of the request.response object with the 'put' method applied
        """
        url = f"{self._url}/mounts/{image_path.lstrip('/')}"
        creds_mapping = self.create_key(creds)
        if creds_mapping:
            response = self._put(url, expected_status=200, params=creds_mapping)
        else:
            response = self._put(url, expected_status=200)
        return response.json()

    def add_mountpoint(self, image_path=None, mountpoint_path=None):
        """
        Parameters
        ----------
        image_path : str
            file path of the disk image
        mountpoint_path : str
            absolute path of the mountpoint

        Returns
        -------
        dict
            requests.Response object : the result of the request.response object with the 'put' method applied
        """
        url = f"{self._url}/add_mountpoint"
        params = {
            "image_path": image_path,
            "mountpoint_path": mountpoint_path,
        }
        response = self._put(url, expected_status=200, params=params)
        return response.json()

    def unmount_image(self, image_path):
        """Deletes supplied image from list of mounted images

        Parameters
        ----------
        image_path : str
            file path of the image to be deleted

        Returns
        -------
        dict
            requests.Response object : the result of the request.response object with the 'delete' method applied
        """
        url = f"{self._url}/mounts/{image_path.lstrip('/')}"
        response = self._delete(url, expected_status=200)
        return response.json()

    def update_image_dir(self, image_dir):
        """
        Parameters
        ----------
        image_dir : str
            the new directory to monitor

        Returns
        -------
        dict
            requests.Response object : the result of the request.response object with the 'put' method applied
        """
        url = f"{self._url}/image_dir"
        image_dir_dict = {"image_dir": image_dir}
        response = self._put(url, expected_status=200, params=image_dir_dict)
        return response.json()

    def get_image_dir(self):
        """
        Returns
        -------
        string
            A string of the current directory being monitored.
        """
        url = f"{self._url}/image_dir"
        response = self._get(url, expected_status=200)
        return response.json()

    def create_key(self, creds):
        method = None
        key = None
        key_full = None

        if not creds:
            return None

        if creds["type"] == "bitlocker":
            method = creds["authentication_method"]
            if method == "password":
                method_short = "p"
                key = creds["authentication_value"]
            elif method == "recovery_key":
                method_short = "r"
                key = creds["bitlocker_recovery_key"]
            elif method == "startup_key_filepath":
                method_short = "s"
                key = creds["bitlocker_startup_key_filepath"]
            elif method == "fvek":
                method_short = "k"
                key = creds["bitlocker_fvek"]

        if creds["type"] == "luks":
            method = creds["authentication_method"]
            if method == "password":
                method_short = "p"
                key = creds["authentication_value"]
            elif method == "key_file":
                method_short = "f"
                key = creds["luks_key_file"]
            elif method == "master_key_file":
                method_short = "m"
                key = creds["luks_master_key_file"]

        key_full = {"key": f"{method_short}:{key}"}
        return key_full

    def _put(self, url, expected_status=None, **kwargs):
        return self._do_method_checked("put", url, expected_status, **kwargs)

    def _get(self, url, expected_status=None, **kwargs):
        return self._do_method_checked("get", url, expected_status, **kwargs)

    def _delete(self, url, expected_status=None, **kwargs):
        return self._do_method_checked("delete", url, expected_status, **kwargs)

    def _do_method_checked(self, method, url, expected_status, **kwargs):
        """This checks that the received response to the requested method was successful, otherwise
        raises exception and displays the status code received.

        Parameters
        ----------
        method : str
            'put', 'get', or 'delete'
        url : str
            same url used to mount or unmount the image
        expected_status: int, list of int, or None
            HTTP response codes that are expected
        kwargs : optional
            optional arguments that `request <http://docs.python-requests.org/en/master/api/?highlight=session#requests.request>`_ takes

        Returns
        -------
        requests.Response
            The value returned when the specified method is requested of the ThumbtackClient
        session
        """
        response = None
        try:
            response = getattr(self.session, method)(url, **kwargs)
        except requests.ConnectionError as e:
            raise ThumbtackClientException(str(e))
        if expected_status is not None:
            if not hasattr(expected_status, "__iter__"):
                expected_status = [expected_status]

            if response.status_code not in expected_status:
                msg = f"Unexpected status {response.status_code} from {response.url} ({response.request.method}); expected {expected_status}"
                if response.text:
                    msg_text = json.loads(response.text)['message']
                    msg += f" - response text: {msg_text}" 
                if "Mount attempt is already in progress for this image." in msg_text:
                    raise DuplicateMountAttemptException(msg)
                else:
                    raise ThumbtackClientException(msg)
        return response
