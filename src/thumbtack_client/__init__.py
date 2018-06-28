# Copyright 2019 The MITRE CORPORATION
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

from thumbtack_client import ThumbtackClientException
from thumbtack_client.ThumbtackClientException import ThumbtackClientException

logger = logging.getLogger(__name__)


class ThumbtackClient(object):
    """
    Creates the ThumbtackClient object using the `requests.Session class <http://docs.python-requests.org/en/master/api/?highlight=session#request-sessions>`_
    so that its 'delete', 'get', and 'put' methods can be used to send requests.
    """
    def __init__(self, host='127.0.0.1', port=8208):
        """
        Initializes the ThumbtackClient object with the `requests.Session class <http://docs.python-requests.org/en/master/api/?highlight=session#request-sessions>`_

        Parameters
        ----------
        host : str
            default host address is 127.0.0.1
        port: int
            default port is 8208
        """
        self.session = requests.Session()
        self._host = '{}:{}'.format(host, port)

    def list_mounted_images(self):
        """
        Returns
        -------
        dict
            A JSON serialized dictionary of all mounted images in: 'http://127.0.0.1:8208/mounts/'
        """
        url = 'http://{}/mounts/'.format(self._host)
        response = self._get(url, expected_status=200)
        return response.json()

    def mount_image(self, image_path):
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
        url = 'http://{}/mounts/{}'.format(self._host, image_path.lstrip('/'))
        response = self._put(url, expected_status=200)
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
        url = 'http://{}/mounts/{}'.format(self._host, image_path.lstrip('/'))
        response = self._delete(url, expected_status=200)
        return response.json()

    def _put(self, url, expected_status=None, **kwargs):
        return self._do_method_checked('put', url, expected_status, **kwargs)

    def _get(self, url, expected_status=None, **kwargs):
        return self._do_method_checked('get', url, expected_status, **kwargs)

    def _delete(self, url, expected_status=None, **kwargs):
        return self._do_method_checked('delete', url, expected_status, **kwargs)

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
            if not hasattr(expected_status, '__iter__'):
                expected_status = [expected_status]

            if response.status_code not in expected_status:
                msg = 'Unexpected status {} from {} ({}); expected {}' \
                    .format(response.status_code, response.url, response.request.method, expected_status)
                if response.text:
                    msg += ' - response text: {}'.format(response.text)
                raise ThumbtackClientException(msg)
        return response
