import sys
import json

sys.path.append("..")

workflow_json = {"authKey": "cdL5k1jGz00ZDm2IUe20", "datasetId": "9191",
                 "invocationId": "617be99d-7cc4-4a6a-af11-e6ceccba9de2", "datasetIdentifier": "${dataset.identifier}",
                 "datasetGlobalId": "doi:10.80827"
                                    "/darus-1958", "datasetDisplayName": "${dataset.displayName}",
                 "minorVersion": "${minorVersion}", "majorVersion": "${majorVersion}", "releaseStatus": "${releaseStatus}"}

tplDict = {'datasetDisplayName': 'Testdatensatz für EU-Projekte', 'datasetId': 'doi:10.80827/darus-1958',
           'datasetUrl': 'https'
                         '://nfldevdataverse3'
                         '.rus.uni-stuttgart.de'
                         '/dataset.xhtml'
                         '?persistentId=doi:10'
                         '.80827/darus-1958', 'testrailUrl': 'http://no.testrail.de',
           'releaseUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/617be99d-7cc4-4a6a-af11-e6ceccba9de2/cdL5k1jGz00ZDm2IUe20'
                         '/ok',
           'lockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/617be99d-7cc4-4a6a-af11-e6ceccba9de2/cdL5k1jGz00ZDm2IUe20'
                      '/addLock',
           'cancelUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/617be99d-7cc4-4a6a-af11-e6ceccba9de2'
                        '/cdL5k1jGz00ZDm2IUe20/cancel',
           'removeLockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/617be99d-7cc4-4a6a-af11-e6ceccba9de2'
                            '/cdL5k1jGz00ZDm2IUe20/removeLock'
                            '', 'errors': '',
           'description': "Datensatz 'Testdatensatz für EU-Projekte' mit ID: doi:10.80827/darus-1958\n                "
                          "URL: https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827"
                          "/darus-1958\n                langfristiger Kontakt: Finch, Fiona <>\n                Autoren: "
                          "Iglezakis, Dorothea, Seeland, Anett, Fritze, Florian\n                Depositoren: \n         "
                          "       Veröffentlichungsworkflow gestartet am 08.12.2023, 12:19:12",
           'descriptionHtml': '<p>Datensatz \'<a href="https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827'
                              '/darus-1958'
                              '">Testdatensatz für EU-Projekte</a>\' mit ID: doi:10.80827/darus-1958<br/>langfristiger Kontakt: Finch, '
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


def test_validate(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "617be99d-7cc4-4a6a-af11-e6ceccba9de2"

    noError, validation_out_html, validation_output = pub.validate_and_format(tplDict, testInvocId)

    assert is_json(validation_output) == True


def test_html_validate(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')
    mocker.patch('pubworkflowApi.Publication.getDatasetId', return_value='doi:10.80827/darus-1958')

    testInvocId = "617be99d-7cc4-4a6a-af11-e6ceccba9de2"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "validate")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "Revalidating ..."


def test_html_validate_counter(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')
    mocker.patch('pubworkflowApi.Publication.getDatasetId', return_value='doi:10.80827/darus-1819')

    testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "validate")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "Revalidating ..."
