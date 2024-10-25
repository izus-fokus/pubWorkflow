import sys

sys.path.append("..")

callDarus_return_value_jsonObject = {"persistentUrl": "https://doi.org/10.5072/darus-447", "protocol": "doi", "authority": "10.5072",
                                     "identifier": "darus-447", "latestVersion": {"metadataBlocks": {"citation": {
        "fields": [{"typeName": "title", "value": "Testtitel"}, {"typeName": "dsDescription", "multiple": "True", "typeClass": "compound",
                                                                 "value": [{"dsDescriptionValue": {"typeName": "dsDescriptionValue",
                                                                                                   "multiple": "False", "typeClass": "primitive",
                                                                                                   "value": "some description"}}]},
                   {"typeName": "author", "multiple": "True", "typeClass": "compound", "value": [
                       {"authorName": {"typeName": "authorName", "multiple": "False", "typeClass": "primitive", "value": "Testor, Testine"},
                        "authorAffiliation": {"typeName": "authorAffiliation", "multiple": "False", "typeClass": "primitive",
                                              "value": "Universität Stuttgart"},
                        "authorIdentifierScheme": {"typeName": "authorIdentifierScheme", "multiple": "False",
                                                   "typeClass": "controlledVocabulary", "value": "ORCID"},
                        "authorIdentifier": {"typeName": "authorIdentifier", "multiple": "False", "typeClass": "primitive",
                                             "value": "0000-0000-0000-0000"}}]},
                   {"typeName": "publication", "multiple": "True", "typeClass": "compound", "value": [{
                       "publicationCitation": {"typeName": "publicationCitation", "multiple": "False", "typeClass": "primitive",
                                               "value": "author1, author2. title (year)."}}]}]}}}}
validation_out = {
    "citation": {
        "author": {
            "0": {
                "message": "Author 'Kraus, Hamzeh' is missing an identifier. The name has been used to retrieve from ORCID and is attached in",
                "proposed-changes": [
                    {
                        "name": "Hamzeh Kraus",
                        "identifier": "0000-0001-9643-4839",
                        "identifier_scheme": "ORCID"
                    }
                ]
            }
        },
        "grant_information": {
            "0": [{
                "loc": "GrantInformation/DFG",
                "message": "Grant agency DFG without grant number.",
                "proposed-change": None
            }],
            "1": [{
                "loc": "GrantInformation/MWK",
                "message": "Grant agency MWK without grant number.",
                "proposed-change": None
            }]
        },
        "keyword": {
          "0": [{
            "message": "Keyword 'Physics' is missing a controlled vocabulary",
            "proposed-changes": [
              {
                "term": "Physics",
                "vocabulary": "Wikidata",
                "vocabulary_url": "http://www.wikidata.org/entity/Q1219728"
              }
            ]
          }]
        }
    }
}


def test_create_get_delete(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail', return_value="Mail sent.")

    mocker.patch('pubworkflowApi.Publication.getRoleAssignments',
                 return_value={"editors": ["Testine Test <testine.test@test.de>", "Testor Test <testor.test@test.de"],
                               "curators": ["Testine Test <testine.test@test.de>", "Testor Test <testor.test@test.de"]})

    mocker.patch('pubworkflowApi.Publication.callDarusAPI', return_value=callDarus_return_value_jsonObject)

    # testInvocId = pub.randomString(9)
    url = "/pubWorkflow/" + "2df88060-74aa-47f3-8123-953a6deb2d91"

    res = client.post(url + "/abc", json={"authKey": "abc", "datasetGlobalId": "doi:10.5072/darus-447", "datasetId": "2043"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["message"] == "Please provide correct URL parameters"
    mocker.patch('pubworkflowApi.Publication.getStatus', return_value="2df88060-74aa-47f3-8123-953a6deb2d91")
    res = client.post(url, json={"datasetGlobalId": "doi:10.5072.darus-9", "datasetId": "2043"})
    assert res.status_code == 404
    # data = res.get_json()
    # assert data["message"] == "Please provide correct URL parameters"
    mocker.patch('pubworkflowApi.Publication.checkAuth', return_value=True)
    res = client.post(url + "/" + credentials["darus"]["authKey"], json={"authKey": credentials["darus"]["authKey"], "datasetId": "2043"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["message"] == "No datasetGlobalId provided"
    res = client.post(url + "/" + credentials["darus"]["authKey"],
                      json={"authKey": credentials["darus"]["authKey"], "datasetGlobalId": "doi:10.5072/darus-447"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["message"] == "No datasetId provided"
    mocker.patch("pubworkflowApi.Validation.validate_dataset", return_value=validation_out)
    mocker.patch("pubworkflowApi.Publication.getStatus", return_value=None)
    res = client.post(url + "/" + credentials["darus"]["authKey"],
                      json={"authKey": credentials["darus"]["authKey"], "datasetGlobalId": "doi:10.5072/darus-447", "datasetId": "2043"})
    assert res.status_code == 200
    # data = res.get_json()
    # assert data["status"] == "new"

    mocker.patch('pubworkflowApi.Publication.getStatus', return_value="new")
    res = client.get(url + "/" + credentials["darus"]["authKey"], json={})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "new"

    # res = client.get(url + "/" + credentials["darus"]["authKey"] + "/" + "okCurator", json={"authKey": credentials["curatorInst"]["authKey"]})
    # assert res.status_code == 200
    # data = res.get_json()
    # assert data["status"] == "gotInformationFromCurator"

    # res = client.get(url + "/" + credentials["darus"]["authKey"] + "/" + "userOk", json={"authKey": credentials["user"]["authKey"]})
    # assert res.status_code == 200
    # assert res.mimetype == "text/html"

    res = client.delete(url + "/" + credentials["darus"]["authKey"], json={"authKey": credentials["darus"]["authKey"]})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "aborted"

    mocker.patch('pubworkflowApi.Publication.callDarusAPI',
                 return_value=[{"lockType": "EditInProgress", "date": "Fri Aug 17 14:05:12 EDT 2018", "user": "ac129993"},
                               {"lockType": "Workflow", "date": "Fri Aug 18 14:05:12 EDT 2018", "user": "ac129993"}])

    res = client.get(url + "/" + credentials["darus"]["authKey"] + "/" + "removeLock")
    assert res.status_code == 200
    assert res.mimetype == "text/html"

    res = client.put(url + "/" + credentials["darus"]["authKey"] + "/" + "addLock")
    assert res.status_code == 200
    data = res.get_json()
    assert res.mimetype == "application/json"
    assert data["status"] == "lockAdded"

    res = client.put(url + "/" + credentials["darus"]["authKey"] + "/" + "removeLock")
    assert res.status_code == 200
    data = res.get_json()
    assert res.mimetype == "application/json"
    assert data["status"] == "lockRemoved"

    mocker.patch('pubworkflowApi.Publication.callDarusAPI',
                 return_value={"latestVersion": {"metadataBlocks": {"citation": {"fields": [{"typeName": "title", "value": "Testtitel"}]}}}})

    res = client.get(url + "/" + credentials["darus"]["authKey"] + "/" + "addLock")
    assert res.status_code == 200
    assert res.mimetype == "text/html"

    res = client.get(url + "/" + credentials["darus"]["authKey"] + "/" + "cancel")
    assert res.status_code == 200
    assert res.mimetype == "text/html"

    res = client.get(url + "/" + credentials["darus"]["authKey"] + "/" + "ok")
    assert res.status_code == 200
    assert res.mimetype == "text/html"  # data = res.get_json()  # assert data["status"] == "finished"
