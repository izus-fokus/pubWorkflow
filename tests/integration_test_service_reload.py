import sys

sys.path.append("..")

workflow_json = {
    "authKey": "cdL5k1jGz00ZDm2IUe20",
    "datasetId": "9192",
    "invocationId": "50b2deef-dfb7-4b37-a7b0-823ae58fe188",
    "datasetIdentifier": "${dataset.identifier}",
    "datasetGlobalId": "doi:10.80827/darus-1816",
    "datasetDisplayName": "${dataset.displayName}",
    "minorVersion": "${minorVersion}",
    "majorVersion": "${majorVersion}",
    "releaseStatus": "${releaseStatus}"
}


def test_startWorkflow(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "50b2deef-dfb7-4b37-a7b0-823ae58fe181"
    url = "/pubWorkflow/" + testInvocId + "/" + "cdL5k1jGz00ZDm2IUe20"
    res = client.post(url, json=workflow_json)
    assert res.status_code == 200
    # assert res.get_data(as_text=True) == "OK: Workflow has started"


def test_removeLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "50b2deef-dfb7-4b37-a7b0-823ae58fe188"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "removeLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockRemoved"


def test_addLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "50b2deef-dfb7-4b37-a7b0-823ae58fe188"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "addLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockAdded"


def test_cancel(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')
    mocker.patch('pubworkflowApi.Publication.callDarusAPI', return_value=True)

    testInvocId = "50b2deef-dfb7-4b37-a7b0-823ae58fe188"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "cancel")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "cancelled"
