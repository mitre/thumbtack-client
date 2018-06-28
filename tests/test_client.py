import pytest
import responses

import thumbtack_client
import thumbtack_client.MountedDiskImage


@pytest.fixture
def client():
    return thumbtack_client.ThumbtackClient()


def test_smoke():
    assert thumbtack_client.MountedDiskImage.MountedDiskImage is not None


@responses.activate
def test_list_mounts_empty(client):
    responses.add(responses.GET, 'http://127.0.0.1:8208/mounts/', '[]')

    response = client.list_mounted_images()
    assert response == []


@responses.activate
def test_list_mounts_populated(client):
    responses.add(responses.GET, 'http://127.0.0.1:8208/mounts/', '[1, 2, 3]')

    response = client.list_mounted_images()
    assert len(response) > 0
