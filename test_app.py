import json
import pytest
from detection import app

@pytest.fixture
def client(request):
    test_client = app.test_client()

    def teardown():
        pass # databases and resourses have to be freed at the end. But so far we don't have anything

    request.addfinalizer(teardown)
    return test_client

def test_main(client):
    response = client.get('/')
    # ищем 'Количество'
    assert b'\xd0\x9a\xd0\xbe\xd0\xbb\xd0\xb8\xd1\x87\xd0\xb5\xd1\x81\xd1\x82\xd0\xb2\xd0\xbe' in response.data

def test_about(client):
    response = client.get('/about')
    #ищем 'Проект'
    assert b'\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb5\xd0\xba\xd1\x82' in response.data

def test_upload(client):
    response = client.get('/upload')
    #ищем форму для загрузки файла'
    assert b'input type="file" name="file_img"' in response.data

