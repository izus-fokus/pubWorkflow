import sys

sys.path.append('..')


def test_hello(client, pub, credentials):
    url = '/pubWorkflow/running/super'
    res = client.get(url)
    data = res.get_json()
    assert data["input"] == "super"


def test_db(client, pub, credentials):
    status = pub.getStatus("ffszFopBe")
    assert status == "finished"
