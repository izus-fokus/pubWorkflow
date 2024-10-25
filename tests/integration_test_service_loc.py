import sys
import json

sys.path.append("..")

workflow_json = {"authKey": "cdL5k1jGz00ZDm2IUe20", "datasetId": "9214", "invocationId": "2c80dba5-fdba-4f0d-a060-286a792030a4",
                 "datasetIdentifier": "${dataset.identifier}", "datasetGlobalId": "doi:10.80827"
                                                                                  "/darus-1847", "datasetDisplayName": "${dataset.displayName}",
                 "minorVersion": "${minorVersion}", "majorVersion": "${majorVersion}", "releaseStatus": "${releaseStatus}"}

tplDict = {'datasetDisplayName': 'Testdatensatz für EU-Projekte', 'datasetId': 'doi:10.80827/darus-1819', 'datasetUrl': 'https'
                                                                                                                        '://nfldevdataverse3'
                                                                                                                        '.rus.uni-stuttgart.de'
                                                                                                                        '/dataset.xhtml'
                                                                                                                        '?persistentId=doi:10'
                                                                                                                        '.80827/darus-1819',
           'testrailUrl': 'http://no.testrail.de',
           'releaseUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/2c80dba5-fdba-4f0d-a060-286a792030a4/cdL5k1jGz00ZDm2IUe20'
                         '/ok',
           'lockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/2c80dba5-fdba-4f0d-a060-286a792030a4/cdL5k1jGz00ZDm2IUe20'
                      '/addLock', 'cancelUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/2c80dba5-fdba-4f0d-a060-286a792030a4'
                                               '/cdL5k1jGz00ZDm2IUe20/cancel',
           'removeLockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/2c80dba5-fdba-4f0d-a060-286a792030a4'
                            '/cdL5k1jGz00ZDm2IUe20/removeLock'
                            '', 'errors': '',
           'description': "Datensatz 'Testdatensatz für EU-Projekte' mit ID: doi:10.80827/darus-1847\n                "
                          "URL: https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827"
                          "/darus-1847\n                langfristiger Kontakt: Finch, Fiona <>\n                Autoren: "
                          "Iglezakis, Dorothea, Seeland, Anett, Fritze, Florian\n                Depositoren: \n         "
                          "       Veröffentlichungsworkflow gestartet am 08.12.2023, 12:19:12",
           'descriptionHtml': '<p>Datensatz \'<a href="https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827'
                              '/darus-1847'
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

    testInvocId = "2c80dba5-fdba-4f0d-a060-286a792030a4"
    url = "/pubWorkflow/" + testInvocId + "/" + "cdL5k1jGz00ZDm2IUe20"
    res = client.post(url, json=workflow_json)
    assert res.status_code == 200  # assert res.get_data(as_text=True) == "OK: Workflow has started"


def test_removeLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "2c80dba5-fdba-4f0d-a060-286a792030a4"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "removeLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockRemoved"


def test_addLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "2c80dba5-fdba-4f0d-a060-286a792030a4"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "addLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockAdded"


def test_validate(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "2c80dba5-fdba-4f0d-a060-286a792030a4"

    noError, validation_out_html, validation_output = pub.validate_and_format(tplDict, testInvocId)

    assert is_json(validation_output) == True

# def test_cancel(client, pub, credentials, mocker):
#     mocker.patch('pubworkflowApi.Publication.sendMail')
#
#     testInvocId = "2c80dba5-fdba-4f0d-a060-286a792030a4"
#     url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"
#
#     res = client.put(url + "/" + "cancel")
#     assert res.status_code == 200
#     assert res.mimetype == "application/json"
#     data = res.get_json()
#     assert data["status"] == "cancelled"
