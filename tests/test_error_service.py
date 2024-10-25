import sys
import os
from unittest import mock

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

validation_out_error = {
    "citation": {
        "author": {
            "0": {
                "message": "Author 'Kraus, Hamzeh' is missing an identifier. The name has been used to retrieve from ORCID and is attached in",
                "proposed-changes": [
                    {
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


def test_error_service(client, pub, credentials, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail', return_value={"message": "Mail sent."})

    # mocker.patch('pubworkflowApi.Publication.sendErrorMail', return_value={"message": "Error notification sent"},
    #              status_code=200)

    mocker.patch('pubworkflowApi.Validation.validate_dataset', return_value=validation_out_error,
                 status_code=504)

    testInvocId = "189b02d5-9469-4167-82e7-3c7a0e1d9241"
    url = "/pubWorkflow/" + testInvocId + "/" + "cdL5k1jGz00ZDm2IUe20"

    noError, res, response = pub.validate_and_format(tplDict=tplDict, invocationId=testInvocId)

    assert res["message"] == "Error notification sent"

