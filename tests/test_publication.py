import socket
import string
import sys
from datetime import datetime
import pubworkflowApi

sys.path.append('..')
callDarus_return_value_jsonObject = {
            "id": 5,
            "identifier": "@ac129993",
            "displayName": "Dorothea Iglezakis",
            "firstName": "Dorothea",
            "lastName": "Iglezakis",
            "email": "dorothea.iglezakis@ub.uni-stuttgart.de",
            "superuser": "true",
            "deactivated": "false",
            "affiliation": "University of Stuttgart (Test)",
            "persistentUserId": "https://idp-test.tik.uni-stuttgart.de/idp/shibboleth|ac129993@uni-stuttgart.de",
            "emailLastConfirmed": "2023-08-16T07:33:59Z",
            "createdTime": "2018-09-19T07:24:19Z",
            "lastLoginTime": "2018-09-19T07:24:19Z",
            "lastApiUseTime": "2023-05-22T10:24:15Z",
            "authenticationProviderId": "shib"
}


def test_randomString(pub):
    for i in [1, 3, 6, 9, 11]:
        res = pub.randomString(i)
        for c in res:
            assert c in string.ascii_letters
        assert len(res) == i


def test_getDatasetUrl(pub, credentials):
    datasetId = pub.randomString(5)
    url = "{}/dataset.xhtml?persistentId={}".format(credentials["darus"]["baseUrl"], datasetId)
    assert pub.getDatasetUrl(datasetId) == url


def test_checkAuth(credentials, pub):
    for audience in ["darus", "curator"]:
        assert pub.checkAuth(credentials[audience]["authKey"], audience)


def test_sendMail(pub, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail', return_value="Mail sent.")
    now = datetime.now()
    subject = "Testmail vom DarUS"
    fromAdr = "DaRUS Test <test@darus.de>"
    toAdr = "dorothea@iglezakis.net"
    toAdrList = [toAdr, "dorothea.iglezakis@ub.uni-stuttgart.de"]
    template = 'tpl_testMail.txt'
    values = {'server': socket.gethostname(), 'date': now.strftime("%d.%m.%Y %H:%M:%S")}

    pub.sendMail(fromAdr, toAdr, subject, template, values, True)
    pub.sendMail(fromAdr, toAdrList, subject, template, values, False, "test@reply.to")


def test_addRun(pub, mocker):
    invocationId = pub.randomString(9)
    datasetId = "doi:10.5072/darus-12"
    databaseId = "13"
    runId = "7"
    assert pub.addRun(invocationId, runId, datasetId, databaseId) == True
    assert databaseId == pub.getDatabaseId(invocationId)
    assert datasetId == pub.getDatasetId(invocationId)

    assert "undefined" == pub.getStatus(invocationId)
    pub.setStatus(invocationId, "finished")
    assert "finished" == pub.getStatus(invocationId)

    postInvocationId = pub.randomString(9)
    pub.setPostInvocationId(postInvocationId, invocationId)
    assert pub.getPostInvocationId(invocationId) == postInvocationId

    mocker.patch("pubworkflowApi.Publication.setDate", return_value="2023")
    assert pub.setDate(invocationId, 'fehlertyp') is not None

    assert invocationId == pub.getInvocationIdByDatasetId(datasetId)


def test_html(pub):
    data = {'status': 'test', 'message': 'Das ist eine Testnachricht', 'invocationId': pub.randomString(9)}
    htmlRes = pubworkflowApi.output_html(data)
    assert htmlRes.mimetype == 'text/html'
    assert htmlRes.status_code == 200

    htmlRes2 = pubworkflowApi.output_html(data, 301)
    assert htmlRes2.mimetype == 'text/html'
    assert htmlRes2.status_code == 301


def test_getEmailFromUser(pub, mocker):
    mocker.patch('pubworkflowApi.Publication.sendMail', return_value="Mail sent.")
    users = [{"username": "ac129993", "name": "Dorothea Iglezakis", "mail": "dorothea.iglezakis@ub.uni-stuttgart.de"}]
    mocker.patch('pubworkflowApi.Publication.callDarusAPI', return_value=callDarus_return_value_jsonObject)
    for u in users:
        assert pub.getEmailFromUser(u["username"]), "{} <{}>".format(u["name"], u["mail"])
