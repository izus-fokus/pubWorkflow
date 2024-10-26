import sys
import json

sys.path.append("..")

workflow_json = {"authKey": "cdL5k1jGz00ZDm2IUe20", "datasetId": "9191", "invocationId": "02ccd385-9fed-419d-9916-37d97dcee8f0",
                 "datasetIdentifier": "${dataset.identifier}", "datasetGlobalId": "doi:10.80827/darus-2113",
                 "datasetDisplayName": "Showcase new features $\Gamma=\oint_C \mathbf{V}\cdot\mathrm{d}\mathbf{l} $", "minorVersion": "${minorVersion}", "majorVersion": "${majorVersion}",
                 "releaseStatus": "${releaseStatus}"}

validation_out = {"citation": {"author": {
    "0": {"message": "Author 'Kraus, Hamzeh' is missing an identifier. The name has been used to retrieve from ORCID and is attached in",
          "proposed-changes": [{"name": "Hamzeh Kraus", "identifier": "0000-0001-9643-4839", "identifier_scheme": "ORCID"}]}},
    "grant_information": {"0": [{"loc": "GrantInformation/DFG", "message": "Grant agency DFG without grant number.", "proposed-change": None}],
                          "1": [{"loc": "GrantInformation/MWK", "message": "Grant agency MWK without grant number.", "proposed-change": None}]},
    "keyword": {"0": [{"message": "Keyword 'Physics' is missing a controlled vocabulary", "proposed-changes": [
        {"term": "Physics", "vocabulary": "Wikidata", "vocabulary_url": "http://www.wikidata.org/entity/Q1219728"}]}]}}}

tplDict = {'datasetDisplayName': 'Testdatensatz für EU-Projekte', 'datasetId': 'doi:10.80827/darus-2113', 'datasetUrl': 'https'
                                                                                                                        '://nfldevdataverse3'
                                                                                                                        '.rus.uni-stuttgart.de'
                                                                                                                        '/dataset.xhtml'
                                                                                                                        '?persistentId=doi:10'
                                                                                                                        '.80827/darus-2113',
           'testrailUrl': 'http://no.testrail.de',
           'releaseUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/02ccd385-9fed-419d-9916-37d97dcee8f0/cdL5k1jGz00ZDm2IUe20'
                         '/ok',
           'lockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/02ccd385-9fed-419d-9916-37d97dcee8f0/cdL5k1jGz00ZDm2IUe20'
                      '/addLock', 'cancelUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/02ccd385-9fed-419d-9916-37d97dcee8f0'
                                               '/cdL5k1jGz00ZDm2IUe20/cancel',
           'removeLockUrl': 'https://nfldevdataverse3.rus.uni-stuttgart.de/pubWorkflow/02ccd385-9fed-419d-9916-37d97dcee8f0'
                            '/cdL5k1jGz00ZDm2IUe20/removeLock'
                            '', 'errors': '',
           'description': "Datensatz 'Testdatensatz für EU-Projekte' mit ID: doi:10.80827/darus-2113\n                "
                          "URL: https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827"
                          "/darus-1812\n                langfristiger Kontakt: Finch, Fiona <>\n                Autoren: "
                          "Iglezakis, Dorothea, Fritze, Florian\n                Depositoren: \n                "
                          "Veröffentlichungsworkflow gestartet am 08.12.2023, 09:36:24",
           'descriptionHtml': '<p>Datensatz \'<a href="https://nfldevdataverse3.rus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.80827'
                              '/darus-1812'
                              '">Testdatensatz für EU-Projekte</a>\' mit ID: doi:10.80827/darus-2113<br/>langfristiger Kontakt: Finch, '
                              'Fiona <><br/>Autoren: '
                              'Iglezakis, Dorothea, Fritze, Florian<br/>Depositoren: <br/>Veröffentlichungsworkflow gestartet am 08.12.2023, '
                              '09:36:24', 'validationOutput': validation_out, 'validationOutputHtml': validation_out}


# https://stackoverflow.com/questions/11294535/verify-if-a-string-is-json-in-python
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def test_startWorkflow(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "02ccd385-9fed-419d-9916-37d97dcee8f0"
    url = "/pubWorkflow/" + testInvocId + "/" + "cdL5k1jGz00ZDm2IUe20"
    res = client.post(url, json=workflow_json)
    assert res.status_code == 200  # assert res.get_data(as_text=True) == "OK: Workflow has started"


def test_removeLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "02ccd385-9fed-419d-9916-37d97dcee8f0"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "removeLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockRemoved"


def test_addLock(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "02ccd385-9fed-419d-9916-37d97dcee8f0"
    url = "/pubWorkflow/" + testInvocId + "/" + "z0OEguWRYRw1PwGZUbYE"

    res = client.put(url + "/" + "addLock")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    data = res.get_json()
    assert data["status"] == "lockAdded"


def test_validate(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail')

    testInvocId = "02ccd385-9fed-419d-9916-37d97dcee8f0"

    noError, validation_out_html, validation_output = pub.validate_and_format(tplDict, testInvocId)

    assert is_json(validation_output) == True