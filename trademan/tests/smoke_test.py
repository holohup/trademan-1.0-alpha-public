from rest_framework import status


def test_root_not_found(client):
    response = client.get('/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_api_root(client):
    response = client.get('/api/v1/')
    assert response.status_code == status.HTTP_200_OK
