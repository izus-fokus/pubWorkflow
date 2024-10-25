import sys
import json

sys.path.append("..")

workflow_json = {"authKey": "cdL5k1jGz00ZDm2IUe20", "datasetId": "9191", "invocationId": "189b02d5-9469-4167-82e7-3c7a0e1d9241",
                 "datasetIdentifier": "${dataset.identifier}", "datasetGlobalId": "doi:10.80827"
                                                                                  "/darus-1819", "datasetDisplayName": "${dataset.displayName}",
                 "minorVersion": "${minorVersion}", "majorVersion": "${majorVersion}", "releaseStatus": "${releaseStatus}"}

tplDict = {'datasetDisplayName': 'Testdatensatz für EU-Projekte', 'datasetId': 'doi:10.80827/darus-1819', 'datasetUrl': 'https'
                                                                                                                        '://nfldevdataverse3'
                                                                                                                        '.rus.uni-stuttgart.de'
                                                                                                                        '/dataset.xhtml'
                                                                                                                        '?persistentId=doi:10'
                                                                                                                        '.80827/darus-1819',
           'testrailUrl': 'http://no.testrail.de',
           'releaseUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/189b02d5-9469-4167-82e7-3c7a0e1d9241/cdL5k1jGz00ZDm2IUe20'
                         '/ok',
           'lockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/189b02d5-9469-4167-82e7-3c7a0e1d9241/cdL5k1jGz00ZDm2IUe20'
                      '/addLock', 'cancelUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/189b02d5-9469-4167-82e7-3c7a0e1d9241'
                                               '/cdL5k1jGz00ZDm2IUe20/cancel',
           'removeLockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/189b02d5-9469-4167-82e7-3c7a0e1d9241'
                            '/cdL5k1jGz00ZDm2IUe20/removeLock'
                            '', 'errors': '',
           'description': "Datensatz 'Testdatensatz für EU-Projekte' mit ID: doi:10.80827/darus-1819\n                "
                          "URL: https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827"
                          "/darus-1819\n                langfristiger Kontakt: Finch, Fiona <>\n                Autoren: "
                          "Iglezakis, Dorothea, Seeland, Anett, Fritze, Florian\n                Depositoren: \n         "
                          "       Veröffentlichungsworkflow gestartet am 08.12.2023, 12:19:12",
           'descriptionHtml': '<p>Datensatz \'<a href="https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827'
                              '/darus-1819'
                              '">Testdatensatz für EU-Projekte</a>\' mit ID: doi:10.80827/darus-1819<br/>langfristiger Kontakt: Finch, '
                              'Fiona <><br/>Autoren: '
                              'Iglezakis, Dorothea, Seeland, Anett, Fritze, Florian<br/>Depositoren: <br/>Veröffentlichungsworkflow gestartet '
                              'am 08.12.2023, '
                              '12:19:12', 'validationOutput': '', 'validationOutputHtml': ''}


# https://stackoverflow.com/questions/11294535/verify-if-a-string-is-json-in-python
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def test_startWorkflow(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
    url = "/pubWorkflow/" + testInvocId + "/" + "cdL5k1jGz00ZDm2IUe20"
    res = client.post(url, json=workflow_json)
    assert res.status_code == 200  # assert res.get_data(as_text=True) == "OK: Workflow has started"


def test_removeLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "removeLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockRemoved"


def test_addLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "addLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockAdded"


def test_validate(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"

    noError, validation_out_html, validation_output = pub.validate_and_format(tplDict, testInvocId)

    assert is_json(validation_output) == True


def test_file_counter(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    numberOfFiles = pub.getFileCount(tplDict["datasetId"])

    assert numberOfFiles == 2


# def test_fileDOIsOff(client, pub, credentials, mocker):
#     mocker.patch('pubworkflowApi.Publication.sendMail')
#
#     testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
#     url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"
#
#     res = client.put(url + "/" + "fileDoisOff")
#     assert res.status_code == 200
#     assert res.mimetype == "application/json"
#     data = res.get_json()
#     assert data["message"] == "File DOIs are switched off"
#
#
# def test_fileDOIsOn(client, pub, credentials, mocker):
#     mocker.patch('pubworkflowApi.Publication.sendMail')
#
#     testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
#     url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"
#
#     res = client.put(url + "/" + "fileDoisOn")
#     assert res.status_code == 200
#     assert res.mimetype == "application/json"
#     data = res.get_json()
#     assert data["message"] == "File DOIs are switched on"

# def test_cancel(client, pub, credentials, mocker):
#     mocker.patch('pubworkflowApi.Publication.sendMail')
#
#     testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
#     url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"
#
#     res = client.put(url + "/" + "cancel")
#     assert res.status_code == 200
#     assert res.mimetype == "application/json"
#     data = res.get_json()
#     assert data["status"] == "cancelled"
