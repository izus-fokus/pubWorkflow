import json
import logging
import os.path
import random
import smtplib
import sqlite3
import string
import sys
import re
import asyncio
from datetime import datetime
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from string import Template

import requests
from flask import Response, request, Flask, jsonify
# from pyDaRUS.functions.validate import Validation
from requests.auth import HTTPBasicAuth

from pubWorkflowExceptions import ApiCallFailedException

app = Flask(__name__)

# @api.representation('text/html')
def output_html(data, code=200, headers=None):
    template = "tpl_message.html"
    if not os.path.isfile(template):
        newData = '<html><head></head><body><div class="message">{}</div></body></html>'.format(data["message"])
    else:
        fh = open(template)
        newData = Template(fh.read()).safe_substitute(data)
        fh.close()
    resp = Response(newData, mimetype="text/html")
    resp.status_code = code
    if headers is not None:
        if resp.headers is not None:
            resp.headers.extend(headers)
        else:
            resp.headers = headers
    return resp


def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
        if c == "<" and not quote:
            tag = True
        elif c == ">" and not quote:
            tag = False
        elif (c == '"' or c == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + c

    return out


def cleanString(toBeCleaned):
    return remove_html_markup(str(toBeCleaned).replace("\r", "").replace("\n", " ").replace('"', "'"))

# https://stackoverflow.com/questions/11384589/what-is-the-correct-regex-for-matching-values-generated-by-uuid-uuid4-hex
def valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
    match = regex.match(uuid)
    return bool(match)

def valid_action(action):
    regex = re.compile('removeLock|addLock|cancel|ok|validate')
    match = regex.match(action)
    return bool(match)

def dummy_apiurl(apiurl):
    if apiurl == "http://localhost:8080":
        return True

with open("bootstrap.min.css", "r") as css_file:
    bootstrapcss = css_file.read()

logging.basicConfig(filename="logs/pubWorkflow.log", level=logging.DEBUG)


class Publication:
    def __init__(self):
        self.errors = []
        self.datasetId = None
        self.databaseId = None
        self.conn = None
        self.appStatus = "undefined"
        self.connOpen = False
        self.calledMethod = None
        # self.validation = Validation(credentials["darus"]["baseUrl"], credentials["darus"]["apiKey"])

        self.args = {}
        self.connectToDb("db/pubworkflow.db")

    def __del__(self):
        self.conn.close()

    def setCalledMethod(self, method):
        self.calledMethod = method

    def connectToDb(self, dbname):
        if self.connOpen:
            self.conn.close()

        self.conn = sqlite3.connect(dbname)
        self.connOpen = True

    # adapted from https://pynative.com/python-generate-random-string/
    def randomString(self, stringLength=6):
        return "".join([random.choice(string.ascii_letters) for _ in range(stringLength)])

    def checkAuth(self, authKey, audience="darus"):
        logging.debug("'{}' sollte sein '{}'".format(authKey.strip(), credentials[audience]["authKey"]))
        if (authKey.strip() == "" or not audience in credentials or authKey.strip() != credentials[audience]["authKey"]):
            return {"message": "incorrect authentification"}, 401
        else:
            return True

    # sending emails
    def sendMail(self, fromAdr, toAdr, subject, template, values, fileName, html=False, replyTo=None):
        msg = MIMEMultipart("alternative") if html else EmailMessage()
        fh = open(template)
        mailText = Template(fh.read()).safe_substitute(values)
        fh.close()
        msg["Subject"] = subject
        msg["From"] = fromAdr
        msg["To"] = ",".join(toAdr) if isinstance(toAdr, list) else toAdr

        if replyTo is not None:
            if isinstance(replyTo, list):
                msg.add_header("reply-to", replyTo[0])
            else:
                msg.add_header("reply-to", replyTo)

        s = smtplib.SMTP(credentials["curator"]["mailHost"])

        if html:
            fh = open(template.replace(".txt", ".html"))
            htmlText = Template(fh.read()).safe_substitute(values)
            fh.close()
            msg.attach(MIMEText(mailText, "plain"))
            msg.attach(MIMEText(htmlText, "html"))
        else:
            msg.set_content(mailText)

        if not fileName is None:
            # Copied from https://www.tutorialspoint.com/send-mail-with-attachment-from-your-gmail-account-using-python
            attach_file_name = fileName
            attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attach_file).read())
            encoders.encode_base64(payload)  # encode the attachment
            # add payload header with filename
            payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
            msg.attach(payload)

        s.sendmail(fromAdr, toAdr, msg.as_string())
        # logging.debug("Sending Email from " + fromAdr + " to " + (
        #     ", ".join(toAdr) if isinstance(toAdr, list) else toAdr) + " with Text: " + msg.as_string())
        if not fileName is None:
            os.remove(fileName)
        s.quit()

    def addRun(self, invocationId, runId, datasetId, databaseId, appStatus=""):
        if appStatus == "":
            appStatus = self.appStatus
        logging.debug("Saving run {} to db with status {} ".format(invocationId, appStatus))
        t = (invocationId, runId, appStatus, datasetId, databaseId)
        try:
            self.conn.execute("INSERT INTO run (invocationId, runId, status, datasetId, databaseId) VALUES (?,?,?,?,?)", t)
            self.conn.commit()
            return True
        except:
            return {"message": "Database Error"}, 409

    def getStatus(self, invocationId):
        t = (invocationId,)
        try:
            res = self.conn.execute("SELECT status FROM run WHERE invocationId = ?", t)
            r = res.fetchone()
            if r:
                return r[0]
            else:
                return None
        except:
            return None


    def setStatus(self, invocationId, appStatus=""):
        if appStatus == "":
            appStatus = self.appStatus
        t = (appStatus, invocationId)
        try:
            self.conn.execute("UPDATE run SET status = ? WHERE invocationId =?", t)
            self.conn.commit()
        except:
            return {"message": "Database Error"}, 409

    def setDate(self, invocationId, dateType):
        dateTypes = ["workflowStarted", "okFromAuthor", "published", "exportedToBibliography", ]
        if dateType in dateTypes:
            t = (invocationId,)
            sql = "UPDATE run SET {} = datetime('now') WHERE invocationId = ?".format(dateType)
            try:
                self.conn.execute(sql, t)
                self.conn.commit()
                return self.getDate(invocationId, dateType)
            except:
                return {"message": "Database Error"}, 409

    def getDate(self, invocationId, dateType):
        dateTypes = ["workflowStarted", "okFromAuthor", "published", "exportedToBibliography", ]
        if dateType in dateTypes:
            t = (dateType, invocationId)
            try:
                res = self.conn.execute("SELECT ? FROM run WHERE invocationId = ?", t)
                r = res.fetchone()
                if r:
                    return r[0]
                else:
                    return None
            except:
                return None

    def setDatasetId(self, dsid):
        self.datasetId = dsid

    def setDatabaseId(self, dbid):
        self.databaseId = dbid

    def getDatabaseId(self, invocationId):
        try:
            res = self.conn.execute("SELECT databaseId FROM run WHERE invocationId=?", (invocationId,))
            r = res.fetchone()
            if r:
                return r[0]
            else:
                return None
        except:
            return None

    def getDatasetId(self, invocationId):
        try:
            res = self.conn.execute("SELECT datasetID FROM run WHERE invocationId=?", (invocationId,))
            r = res.fetchone()
            if r:
                return r[0]
            else:
                return None
        except:
            None

    def getDatasetIdByPostInvoc(self, postInvocationId):
        try:
            res = self.conn.execute("SELECT datasetID FROM run WHERE postInvocationId=?", (postInvocationId,))
            r = res.fetchone()
            if r:
                return r[0]
            else:
                return None
        except:
            None

    def getInvocationIdByDatasetId(self, datasetId):
        t = (datasetId,)
        try:
            res = self.conn.execute('SELECT invocationId FROM run WHERE datasetId = ? AND status = "finished" ORDER BY published DESC', t)
            r = res.fetchone()

            if r:
                return r[0]
            else:
                return None
        except:
            None

    def getPostInvocationId(self, invocationId):
        t = (invocationId,)
        try:
            res = self.conn.execute("SELECT postInvocationId FROM run WHERE invocationId = ?", t)
            r = res.fetchone()
            if r:
                return r[0]
            else:
                return None
        except:
            return None

    def setPostInvocationId(self, postInvocationId, invocationId):
        t = (postInvocationId, invocationId)
        try:
            self.conn.execute("UPDATE run SET postInvocationId = ? WHERE invocationId =?", t)
            self.conn.commit()
        except:
            return {"message": "Database Error"}, 409

    # from
    # https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

    def getDatasetUrl(self, datasetId):
        datasetUrl = "{}/dataset.xhtml?persistentId={}".format(credentials["darus"]["baseUrl"], datasetId)
        return datasetUrl

    def callDarusAPI(self, url, method="get", data=None, expectedCode=200, nodata=False, contentType="application/json"):
        headers = {"content-type": contentType, "X-Dataverse-key": credentials["darus"]["apiKey"], }
        dsReq = None
        if method == "get":
            dsReq = requests.get(url, headers=headers)
        elif method == "post":
            if data is not None:
                dsReq = requests.post(url, headers=headers, data=json.dumps(data))
            else:
                dsReq = requests.post(url, headers=headers)
        elif method == "put":
            if data is not None:
                dsReq = requests.put(url, headers=headers, data=json.dumps(data))
            else:
                dsReq = requests.put(url, headers=headers)
        elif method == "delete":
            dsReq = requests.delete(url, headers=headers)
        # get authors

        if nodata:
            if dsReq.status_code == expectedCode:
                return True
            else:
                raise ApiCallFailedException("DaRUS-Call of {} failed: {} {}".format(url, dsReq.reason, dsReq.text))

        resDapi = dsReq.json()
        if dsReq.status_code == expectedCode and resDapi["status"] == "OK":
            return resDapi["data"]
        elif resDapi["status"] == "ERROR":
            return "ERROR"
        else:
            raise ApiCallFailedException("DaRUS-Call of {} failed: {} {}".format(url, dsReq.reason, dsReq.text))

    def getEmailFromUser(self, uid):
        url = "{}/api/admin/authenticatedUsers/{}".format(credentials["darus"]["apiBaseUrl"], uid)
        uDat = self.callDarusAPI(url)
        return "{} <{}>".format(uDat["displayName"], uDat["email"])

    def getFileCount(self, datasetId, version=":latest"):
        countFile = 0
        url = "{}/api/datasets/:persistentId/versions/{}/files?persistentId={}".format(credentials["darus"]["baseUrl"], version, datasetId)
        try:
            data = self.callDarusAPI(url)
            if data == "ERROR":
                countFile = 0
            else:
                countFile = len(data)
        except ApiCallFailedException as e:
            logging.error(str(e))
            self.errors.append(str(e))
        return countFile

    def switchFileDOIs(self, on=True):
        url = "{}/api/admin/settings/:FilePIDsEnabled".format(credentials["darus"]["apiBaseUrl"]);
        data = 'true' if on else 'false';
        try:
            self.callDarusAPI(url, method="put", data=data, nodata=False)
        except ApiCallFailedException as e:
            logging.error(str(e))
            self.errors.append(str(e))

    def getRoleAssignments(self):
        editors = []
        curators = []
        edMails = []
        cuMails = []

        url = "{}/api/datasets/:persistentId/assignments?persistentId={}".format(credentials["darus"]["apiBaseUrl"], self.datasetId)
        roles = self.callDarusAPI(url)

        for r in roles:
            if r["_roleAlias"] == "editor":
                editors.append(r["assignee"].lstrip("@"))
            if r["_roleAlias"] == "curator":
                curators.append(r["assignee"].lstrip("@"))

        for e in editors:
            # logging.debug(e)
            self.callDarusAPI("{}/api/admin/authenticatedUsers/{}".format(credentials["darus"]["apiBaseUrl"], e))
            edMails.append(self.getEmailFromUser(e))  # "{} <{}>".format(res['displayName'],res['email']))
        for c in curators:
            # logging.debug(c)
            self.callDarusAPI("{}/api/admin/authenticatedUsers/{}".format(credentials["darus"]["apiBaseUrl"], c))
            cuMails.append(self.getEmailFromUser(c))  # "{} <{}>".format(res['displayName'],res['email']))

        roleMails = {"editors": edMails, "curators": cuMails}
        return roleMails
    def getValidationStyle(self):
        validationStyle = (""
        + "<style type='text/css'>"
        + bootstrapcss
        + ".tablesize {"
        +   "width: fit-content;"
        +   "block-size: fit-content;"
        +   "}"
        +   ".highlight {"
        +   "color: red;"
        +   "}"
        + "</style>")
        return validationStyle

    def getValidationStyleNoValidation(self):
        validationStyle = (""
        + "<style type='text/css'>"
        + bootstrapcss
        + ".tablesize {"
        +   "width: fit-content;"
        +   "block-size: fit-content;"
        +   "}"
        +   ".highlight {"
        +   "color: red;"
        +   "}"
        +   "#close {"
        +   "display: none;"
        +   "visibility: hidden;"
        +   "}"
        + "</style>")
        return validationStyle

    def sendErrorMail(self, tplDict, jsonData=None):
        try:
            if not jsonData is None:
                requests.post(credentials["darus"]["apiErrorMail"] + "/" + urlPathErrorMail + "/error/" + tplDict["datasetId"]
                              + "/" + authKeyErrorMail, data=json.dumps(jsonData))
            else:
                requests.get(
                    credentials["darus"]["apiErrorMail"] + "/" + urlPathErrorMail + "/error/" + tplDict["datasetId"] + "/" + authKeyErrorMail)
        except BaseException as e:
            errorMessage = e.__str__()
            if not type(errorMessage) == str:
                 errorMessage = "Es ist ein Fehler bei Erstellen des Validierungsoutputs aufgetreten"
            logging.debug("Fehler beim Versenden der Error-Mail: " + errorMessage)
        if credentials["darus"]["mailer"] == "True":
            self.sendMail("darus-workflow@izus.uni-stuttgart.de",  # from
                          credentials["curator"]["email"],  # to
                          "Neue Veröffentlichung in DaRUS - {}".format(tplDict["datasetId"]),  # subject
                          credentials["curator"]["mailTpl"],  # template
                          tplDict,  # values
                          None, html=True)

        logging.debug("Validation undone")

    def set_validation_output_no(self):
        validation_output = "<!DOCTYPE html><html><head>" + self.getValidationStyleNoValidation() + "</head>"
        validation_output = validation_output + "<p>No validation configured</p></html>"
        return validation_output

    def set_validation_output(self, validation_json, tplDict):
        try:
            validation_output = "<!DOCTYPE html><html><head>"+self.getValidationStyle()+"</head>"
            if not validation_json["citation"].get("author") == None:
                if not validation_json["citation"]["author"].get("0") == None:
                    for authors in validation_json["citation"]["author"]:
                        validate_four = validation_json["citation"]["author"][authors]["proposed-changes"]
                        validate_message = validation_json["citation"]["author"][authors]["message"]
                        counter = 0
                        if type(validate_four) == list:
                            validation_output = (
                                            validation_output
                                            + "<p><div class='highlight'>"
                                            + validate_message
                                            + "</div><table class='table table-striped tablesize table-bordered'>"
                                            + "<thead><tr>"
                                            + "<th>Author</th>"
                                            + "<th>ORCID</th></tr></thead><tbody>")
                            for author in validate_four:
                                if counter == 5:
                                    break
                                counter += 1
                                validation_output = \
                                    (validation_output
                                         + "<tr><td>"
                                         +  "<a href='https://orcid.org/"
                                         + author["identifier"] + "'><span "
                                         + "class ='d-inline-block' tabindex='0' data-toggle='tooltip'"
                                         +  "title='Affiliation: " + author["affiliation"]
                                         + " hat folgende Treffer-Validierung: "
                                         + author["affiliation_match"] + "'>"
                                         + author["name"] + " hat eine "
                                         + author["identifier_scheme"]
                                         + "</span></a></td><td>"
                                         + author["identifier"] + "</td></tr>")
                            validation_output = validation_output + "</tbody></table></p>"
                        elif not type(validate_four) == str:
                            validation_output = (
                                        validation_output
                                            + "<p><div class='highlight'>"
                                            + validate_message
                                            + " mit Nachricht: "
                                            + validate_four.get("name") + "</div></p>")
                        else:
                            validation_output = (
                                        validation_output + "<p><div class='highlight'>"
                                        + validate_message + " mit Nachricht: "
                                        + validate_four
                                        + "</div></p>")
                else:
                    validate_message = validation_json["citation"]["author"][authors]["message"]
                    counter = 0
                    validation_output = validation_output + ("<p><div class='highlight'>" + validate_message + "</div></p>")

            if not validation_json["citation"].get("keyword") == None:
                if not validation_json["citation"]["keyword"].get("0") == None:
                    for keywords in validation_json["citation"]["keyword"]:
                        for vocabulary in validation_json["citation"]["keyword"][keywords]:
                            if not vocabulary.get("message") == "Keyword not found" and not vocabulary.get("message") == "API down":
                                validate_four = vocabulary["proposed-changes"]
                                validate_message = vocabulary["message"]
                                counter = 0
                                validation_output = \
                                    (validation_output
                                     + ("<p><div class='highlight'>"
                                        + validate_message
                                        + "</div><table class='table table-striped tablesize table-bordered'><thead><tr>"
                                          "<th>Keyword</th>"
                                          "<th>Vocabulary</th>"
                                          "<th>URI</th></tr></thead><tbody>"))
                                for keyword in validate_four:
                                    if counter == 8:
                                        break
                                    counter += 1
                                    validation_output = \
                                        ((validation_output
                                          + "<tr><td><span class='d-inline-block' tabindex='0' data-toggle='tooltip' "
                                          +  "title='" + keyword["description"] + "'>"
                                          +  "<a href='" + keyword["vocabulary_url"] + "'>"
                                          + keyword["term"]
                                          + "</a>"
                                          + "</span>"
                                          + "</td><td>"
                                          + keyword["vocabulary"]
                                          + "</td><td>"
                                          + keyword["vocabulary_url"]) + "</td></tr>")
                                validation_output = validation_output + "</tbody></table></p>"
                            elif vocabulary.get("message") == "API down":
                                validate_message = vocabulary.get("proposed-changes")
                                validation_output = (validation_output + ("<p><div class='highlight'>" + validate_message + "</div></p>"))
                            elif vocabulary.get("message") == "Keyword not found":
                                validate_message = vocabulary.get("proposed-changes")
                                validation_output = (validation_output + ("<p><div class='highlight'>" + validate_message + "</div></p>"))

            if not validation_json["citation"].get("grant_number") == None:
                if not validation_json["citation"]["grant_number"].get("0") == None:
                    for grants in validation_json["citation"]["grant_number"]:
                        for grantinfo in validation_json["citation"]["grant_number"][grants]:
                            grant_information_loc = grantinfo["loc"]
                            grant_information_message = grantinfo["message"]
                            if not grantinfo.get("proposed-change") == None:
                                grant_information_proposedchange = grantinfo["proposed-change"]
                                validation_output = validation_output + ("<p><table class='table table-striped tablesize table-bordered'><thead><tr>"
                                                                         "<th>Metadata field</th>"
                                                                         "<th>Current Value</th>"
                                                                         "<th>Suggestion</th></tr></thead><tbody>"
                                                                         "<tr><td>" +
                                                                         grant_information_loc
                                                                         + "</td><td class='highlight'>" +
                                                                         grant_information_message
                                                                         + "</td><td>" +
                                                                         grant_information_proposedchange
                                                                         + "</td></tr></tbody></table></p>")
                            elif grant_information_message == "OpenAire-API down":
                                grant_information_proposedchange = grantinfo["proposed-change"]
                                validation_output = validation_output + (
                                        "<p>" + grant_information_message + " mit Nachricht: <div class='highlight'>"
                                        + grant_information_proposedchange + "</div></p>")

            if not validation_json["citation"].get("ds_description") == None:
                if not validation_json["citation"]["ds_description"].get("0") == None:
                    description = validation_json["citation"]["ds_description"]["0"]
                    description_message = description["message"]
                    if not description.get("proposed-changes") == None:
                        validate_four = description["proposed-changes"]
                        validation_output = validation_output + ("<p><div class='highlight'>"
                                                                 + description_message +
                                                                 "</div><table class='table table-striped tablesize table-bordered'>"
                                                                 "<thead><tr>"
                                                                 "<th>URL</th>"
                                                                 "<th>Link name</th>"
                                                                 "<th>Status Code</th>"
                                                                 "</tr></thead><tbody>")
                        for desc in validate_four:
                            validation_output = (validation_output +
                                                                    "<tr><td>" +
                                                                    desc["url"]
                                                                    + "</td><td>" +
                                                                    desc["linkName"]
                                                                    + "</td>"
                                                                      "<td class='highlight'>" +
                                                                    desc["status_code"]
                                                                    + "</td></tr>")
                        validation_output = validation_output + "</tbody></table></p>"

            if not validation_json["citation"].get("publication") == None:
                if not validation_json["citation"]["publication"].get("0") == None:
                    for relatedpublication in validation_json["citation"]["publication"]:
                        proposed_changes = validation_json["citation"]["publication"][relatedpublication]["proposed-changes"]
                        message = validation_json["citation"]["publication"][relatedpublication]["message"]
                        validation_output = (validation_output
                                                 + ("<p><table class='table table-striped tablesize table-bordered'><thead><tr>"
                                                    "<th>Metadata field</th>"
                                                    "<th>Message</th>"
                                                    "<th>Return Value</th></tr></thead><tbody>"
                                                    "<tr>"
                                                    "<td>Related Publication</td>"
                                                    "<td class='highlight'>" + message + "</td>"
                                                    "<td>"+ proposed_changes + "</td>"
                                                    "</tr></tbody></table></p>"))
            validation_output = validation_output + "</html>"
            return validation_output
        except BaseException as e:
            errorMessage = e.__str__()
            if not type(errorMessage) == str:
                 errorMessage = "Es ist ein Fehler bei Erstellen des Validierungsoutputs aufgetreten"
            logging.debug("set_validation_output error thrown: " + errorMessage)
            self.sendErrorMail(tplDict, {"ERRORTHROWN": errorMessage})
            return {"message": "Error notification sent"}
    # https://stackoverflow.com/questions/37278647/fire-and-forget-python-async-await
    def fire_and_forget(f):
        def wrapped(*args, **kwargs):
            return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)

        return wrapped

    def validate_and_format(self, tplDict, invocationId):
        # validation_out = self.validation.validate_dataset(tplDict["datasetId"])

        if type(validation_out) == str:
            validation_json = json.loads(validation_out)
        else:
            validation_json = validation_out

        validation_out_html = validation_json
        errorMessage = ""
        noError = True
        if validation_json.get("ERRORTHROWN") == None:
            validation_out_html = self.set_validation_output(validation_json, tplDict)
        else:
            noError = False
            errorMessage = validation_json.get("ERRORTHROWN")
            logging.debug("validate_and_format error thrown: " + errorMessage)
            self.sendErrorMail(tplDict, {"ERRORTHROWN": errorMessage})

        return noError, validation_out_html, validation_out

    def get_metadata(self, authors, editorMails, contactMails, datasetTitle, datasetUrl, datasetId):
        try:
            resFields = self.callDarusAPI(
                "{}/api/datasets/:persistentId/?persistentId={}".format(credentials["darus"]["apiBaseUrl"], datasetId))
            fields = resFields["latestVersion"]["metadataBlocks"]["citation"]["fields"]
            for f in fields:
                if f["typeName"] == "datasetContact":
                    for c in f["value"]:
                        contactMails.append("{name} <{value}>".format(name=c.get("datasetContactName", {}).get("value", ""),
                                                                      value=c.get("datasetContactEmail", {}).get("value",
                                                                                                                 ""), ))
                if f["typeName"] == "author":
                    for a in f["value"]:
                        authors.append(a["authorName"]["value"])
                if f["typeName"] == "title":
                    datasetTitle = f["value"]
        except ApiCallFailedException as e:
            logging.error(str(e))
            self.errors.append(str(e))
            requests.get(credentials["darus"]["apiErrorMail"] + "/" + urlPathErrorMail + "/error/" + datasetId + "/" + authKeyErrorMail)

        # TODO: integrate to templates
        description = """Datensatz '{}' mit ID: {}
            URL: {}
            langfristiger Kontakt: {}
            Autoren: {}
            Depositoren: {}
            Veröffentlichungsworkflow gestartet am {}""".format(datasetTitle, datasetId, datasetUrl,
            ", ".join(contactMails), ", ".join(authors), ", ".join(editorMails),
            datetime.now().strftime("%d.%m.%Y, %H:%M:%S"))

        descriptionHtml = (
            "<p>Datensatz '<a href=\"{url}\">{title}</a>' mit ID: {id}<br/>langfristiger Kontakt: {contact}<br/>Autoren: {"
            "authors}<br/>Depositoren: {depositors}<br/>Veröffentlichungsworkflow gestartet am {date}").format(
            title=datasetTitle, id=datasetId, url=datasetUrl, contact=", ".join(contactMails),
            authors=", ".join(authors), depositors=", ".join(editorMails),
            date=datetime.now().strftime("%d.%m.%Y, %H:%M:%S"))

        return authors, editorMails, contactMails, datasetTitle, datasetUrl, description, descriptionHtml

    @fire_and_forget
    def prepare_mail(self, tplDict, invocationId, titleMessage):
        if (stringToBool(credentials["darus"]["validation"])):
            logging.debug("Now starting the validation process")

            noError, validation_out_html, validation_out = self.validate_and_format(tplDict, invocationId)

            if noError == True:
                try:
                    ct = datetime.now().__str__().replace(" ", "_")
                    ct = ct.replace(":", "_")

                    fileName = None
                    if credentials["darus"]["validationJSON"] == "True":
                        fileName = "attachments/" + ct + "_validation.json"
                        f = open(fileName, "w")
                        f.write(validation_out.__str__())
                        f.close()

                    # if "\\n" in validation_output:
                    #     validation_out_html = validation_output.replace("\n", "<br>")
                    # else:
                    logging.debug("Beginning to count files ...")
                    numberOfFiles = self.getFileCount(datasetId=tplDict["datasetId"])
                    numberOfFilesMessage = ""

                    if numberOfFiles > 95:
                        numberOfFilesMessage = "Die Anzahl der Dateien beträgt: " + str(numberOfFiles) + ". Bitte schalten Sie die filePids aus."
                    else:
                        numberOfFilesMessage = "Die Anzahl der Dateien beträgt: " + str(numberOfFiles) + "."

                    tplDict["validationOutputHtml"] = validation_out_html
                    tplDict["numberOfFiles"] = numberOfFilesMessage

                    logging.debug("datasetId: {}".format(tplDict["datasetId"]))

                    if credentials["darus"]["mailer"] == "True":
                        self.sendMail("darus-workflow@izus.uni-stuttgart.de",  # from
                                      credentials["curator"]["email"],  # to
                                      titleMessage.format(tplDict["datasetId"]),
                                      credentials["curator"]["mailTpl"],  # template
                                      tplDict,  # values
                                      fileName, html=True)

                    logging.debug("Validation done")
                except BaseException as e:
                    errorMessage = e.__str__()
                    if not type(errorMessage) == str:
                        errorMessage = "Es ist ein Fehler beim Vorbereiten der Mail aufgetreten"
                    logging.debug("prepare_mail error thrown: " + errorMessage)
                    self.sendErrorMail(tplDict, {"ERRORTHROWN": errorMessage})
                    return {"message": "Error notification sent"}
        else:
            logging.debug("No validation process was set up")
            try:
                validation_out_html = self.set_validation_output_no()

                logging.debug("Beginning to count files ...")
                numberOfFiles = self.getFileCount(datasetId=tplDict["datasetId"])
                numberOfFilesMessage = ""

                if numberOfFiles > 95:
                    numberOfFilesMessage = "Die Anzahl der Dateien beträgt: " + str(
                        numberOfFiles) + ". Bitte schalten Sie die filePids aus."
                else:
                    numberOfFilesMessage = "Die Anzahl der Dateien beträgt: " + str(numberOfFiles) + "."

                tplDict["validationOutputHtml"] = validation_out_html
                tplDict["numberOfFiles"] = numberOfFilesMessage

                logging.debug("datasetId: {}".format(tplDict["datasetId"]))

                if credentials["darus"]["mailer"] == "True":
                    self.sendMail("darus-workflow@izus.uni-stuttgart.de",  # from
                                  credentials["curator"]["email"],  # to
                                  titleMessage.format(tplDict["datasetId"]), credentials["curator"]["mailTpl"],  # template
                                  tplDict,  # values
                                  None, html=True)

            except BaseException as e:
                errorMessage = e.__str__()
                if not type(errorMessage) == str:
                    errorMessage = "Es ist ein Fehler beim Vorbereiten der Mail aufgetreten"
                logging.debug("Error thrown: " + errorMessage)
                return {"message": "Error notification logged"}

    def running(self, inputVar):
        if self.calledMethod is None:
            self.calledMethod = "GET"
        # Status des Workflows zurueckmelden
        logging.debug("get with id {}".format(inputVar))
        if inputVar == "super":
            return {"input": inputVar, "status": "running"}
        else:
            return {"message": "empty"}, 204

    def get(self, invocationId):
        if self.calledMethod is None:
            self.calledMethod = "GET"
        # Status des Workflows zurueckmelden
        try:
            if request.is_json:
                jsonData = request.get_json()
            logging.debug("get with id {}".format(invocationId))

            self.appStatus = self.getStatus(invocationId)
            if self.args["authKey"] is None:
                return {"message": "No authKey provided"}, 401
            responseObject = self.checkAuth(self.args["authKey"])  # credentials file
            if responseObject != True:
                return responseObject

            if self.appStatus is None:
                return {"message": "Invocation ID {} is not existing".format(invocationId)}, 404

            return {"invocationId": invocationId, "status": self.appStatus}
        except BaseException:
            return {"invocationId": invocationId, "status": self.appStatus}, 400

    def post(self, invocationId):
        if self.calledMethod is None:
            self.calledMethod = "POST"
        self.appStatus = "new"
        # Workflow starten
        logging.debug("post {}  with status {} ".format(invocationId, self.appStatus))
        try:
            jsonData = request.get_json()
            # jsonData=json.loads(args)
            if self.args["authKey"] is None:
                return {"message": "No authKey provided"}, 401
            responseObject = self.checkAuth(self.args["authKey"])  # credentials file
            if responseObject != True:
                return responseObject
            if not "datasetGlobalId" in jsonData:
                return {"message": "No datasetGlobalId provided"}, 400
            self.setDatasetId(jsonData["datasetGlobalId"])  # doi
            if not "datasetId" in jsonData:
                return {"message": "No datasetId provided"}, 400
            self.setDatabaseId(jsonData["datasetId"])  # database id
            # t = (invocationId,)
            with open("bypass_ids.txt", "r") as bypass_file:
                bypass_ids = bypass_file.read().splitlines()
            if jsonData["datasetGlobalId"] in bypass_ids:
                self.appStatus = "bypassed"
                with open("bypassed.txt", "a") as bypass_f:
                    startUrl = ("{baseUrl}/" + urlPath + "/{id}?authKey={auth}").format(baseUrl=credentials["darus"]["baseUrl"], id=invocationId,
                                                                                  auth=credentials["curator"]["authKey"])

                    bypass_f.write("{}&action=ok\n".format(startUrl))
                return {"invocationId": invocationId, "status": self.appStatus, "datasetId": self.datasetId }

            alreadyExisting = self.getStatus(invocationId)
            if alreadyExisting is not None:
                return {"message": "Invocation Id already exists with status {}".format(alreadyExisting)}, 409
            datasetUrl = self.getDatasetUrl(self.datasetId)
            authors = []
            editorMails = []
            contactMails = []
            datasetTitle = ""

            authors, editorMails, contactMails, datasetTitle, datasetUrl ,description, descriptionHtml = (
                self.get_metadata(authors, editorMails, contactMails, datasetTitle, datasetUrl, jsonData["datasetGlobalId"]))

            runId = 0
            runUrl = ""

            try:
                self.addRun(invocationId, runId, self.datasetId, self.databaseId)
                self.setDate(invocationId, "workflowStarted")
            except Exception as e:
                self.errors.append("Fehler beim Speichern des Runs in der Datenbank: " + str(e))

            if (credentials["curator"]["email"] is None or credentials["curator"]["mailTpl"] is None or not os.path.isfile(
                    credentials["curator"]["mailTpl"])):
                self.setStatus(invocationId, "mailCredentialsError")
                return {"message": "Mail-Configuration is missing, check credentials.txt"}, 502

            # E-Mail an Team 3 mit Link zu Testrail?
            errorStr = ("Die folgenden Fehler sind aufgetreten: {}".format(", ".join(self.errors)) if len(self.errors) > 0 else "")

            logging.debug(errorStr)

            validation_out = ""
            validation_out_html = ""

            startUrl = ("{baseUrl}/" + urlPath + "/{id}/{auth}/").format(baseUrl=credentials["darus"]["baseUrl"], id=invocationId,
                                                                   auth=credentials["curator"]["authKey"])

            tplDict = {"datasetDisplayName": datasetTitle, "datasetId": self.datasetId, "datasetUrl": datasetUrl, "testrailUrl": runUrl,
                       "releaseUrl": "{}ok".format(startUrl), "lockUrl": "{}addLock".format(startUrl), "cancelUrl": "{}cancel".format(startUrl),
                       "removeLockUrl": "{}removeLock".format(startUrl), "fileDoisOnUrl": "{}fileDoisOn".format(startUrl),
                   "fileDoisOffUrl": "{}fileDoisOff".format(startUrl), "numberOfFiles": "numberOfFilesMessage", "errors": errorStr, "description":
                           description, "validateUrl": "{}validate".format(startUrl),
                       "descriptionHtml": descriptionHtml, "validationOutput": validation_out, "validationOutputHtml": validation_out_html, }

            self.prepare_mail(tplDict, invocationId, "Neue Veröffentlichung in DaRUS - {}")
            logging.debug(
                "Response is: {json}".format(json={'invocationId': invocationId, 'status': self.appStatus, 'datasetId': self.datasetId}))
            return jsonify({'invocationId': invocationId, 'status': self.appStatus, 'datasetId': self.datasetId})
        except BaseException:
            return {"invocationId": invocationId, "status": self.appStatus, "datasetId": self.datasetId}, 400

    def put(self, invocationId):
        # jsonRes = {}
        if self.calledMethod is None:
            self.calledMethod = "PUT"
        logging.debug("in PUT")
        try:
            jsonData = {};
            if request.is_json:
                jsonData = request.get_json()
            # jsonData = json.loads(args)
            logging.debug("action: {}".format(self.args["action"]))
            # je nach input -> zurueck an Autor mit Kommentar oder publish
            #        headers = {'content-type': 'application/json', 'X-Dataverse-key':credentials["darus"]["apiKey"]}

            if self.args["action"] == "ok":
                responseObject = self.checkAuth(self.args["authKey"], "curator")
                if responseObject != True:
                    return responseObject
                url = "{baseUrl}/api/workflows/{id}".format(baseUrl=credentials["darus"]["apiBaseUrl"], id=invocationId)
                # hier PUMA-POST der Veröffentlichung
                try:
                    self.callDarusAPI(url, "post", expectedCode=202, data="OK", nodata=True)
                except ApiCallFailedException as e:
                    ret = json.loads(str(e)[str(e).index('{"status"'):])
                    if self.calledMethod == "GET":
                        return output_html(ret)
                    else:
                        return ret, 401

                self.appStatus = "finished"
                self.setStatus(invocationId)
                self.setDate(invocationId, "published")
                # Workflow abschliessen
                if self.calledMethod == "GET":
                    return output_html({"status": self.appStatus,
                                        "message": "Publication process is started for dataset {}.".format(self.getDatasetId(invocationId)), })
                else:
                    return {"invocationId": invocationId, "status": self.appStatus}

            if self.args["action"] == "removeLock":
                responseObject = self.checkAuth(self.args["authKey"], "curator")
                if responseObject != True:
                    return responseObject
                databaseId = self.getDatabaseId(invocationId)
                if databaseId is None:
                    return {"message": "Invocation ID {} is not existing".format(invocationId)}, 404
                url = "{baseUrl}/api/datasets/{databaseId}/locks".format(baseUrl=credentials["darus"]["apiBaseUrl"], databaseId=databaseId)
                locks = []
                try:
                    response = self.callDarusAPI(url)
                    for lock in response:
                        locks.append("{ltype} by {luser} on {ldate}".format(ltype=lock["lockType"], luser=lock["user"], ldate=lock["date"], ))
                except ApiCallFailedException as e:
                    ret = json.loads(str(e)[str(e).index('{"status"'):])
                    if self.calledMethod == "GET":
                        return output_html(ret)
                    else:
                        return ret, 502

                if len(locks) == 0:
                    ret = {"invocationId": invocationId, "status": "noLocks",
                           "message": "No Locks to remove for datasetid {}".format(self.getDatasetId(invocationId)), }
                    if self.calledMethod == "GET":
                        return output_html(ret)
                    else:
                        return ret

                try:
                    self.callDarusAPI(url, "delete")
                    self.appStatus = "lockRemoved"
                    self.setStatus(invocationId)
                except ApiCallFailedException as e:
                    self.setStatus(invocationId, "errorRemovingLocks")
                    return {"message": "Removing locks failed.{}".format(str(e))}, 502

                ret = {
                    "invocationId": invocationId,
                    "status": self.appStatus,
                    "message": "The following locks were removed for dataset {}: {}".format(
                        self.getDatasetId(invocationId),
                        ", ".join(locks)),
                }

                if self.calledMethod == "GET":
                    return output_html(ret)
                else:
                    return ret

            if self.args["action"] == "addLock":
                self.appStatus = "lockAdded"
                self.setStatus(invocationId)
                responseObject = self.checkAuth(self.args["authKey"], "curator")
                if responseObject != True:
                    return responseObject
                databaseId = self.getDatabaseId(invocationId)
                if databaseId is None:
                    return {"message": "Invocation ID {} is not existing".format(invocationId)}, 404
                url = "{baseUrl}/api/datasets/{databaseId}/lock/Workflow".format(
                    baseUrl=credentials["darus"]["apiBaseUrl"], databaseId=databaseId)
                try:
                    self.callDarusAPI(url, "post")
                except ApiCallFailedException as e:
                    ret = json.loads(str(e)[str(e).index('{"status"'):])
                    if self.calledMethod == "GET":
                        return output_html(ret)
                    else:
                        return ret, 502

                ret = {"invocationId": invocationId, "status": self.appStatus,
                       "message": "Publication workflow lock is added to dataset {}".format(self.getDatasetId(invocationId)), }
                if self.calledMethod == "GET":
                    return output_html(ret)
                else:
                    return ret

            if self.args["action"] == "cancel":
                responseObject = self.checkAuth(self.args["authKey"], "curator")
                if responseObject != True:
                    return responseObject
                # Prozess abbrechen
                self.appStatus = self.getStatus(invocationId)
                if self.appStatus is None:
                    return {"message": "Invocation ID {} is not existing".format(invocationId)}, 404
                if self.appStatus == "finished":
                    return {"message": "Invocation ID is already finished".format(invocationId)}, 409
                url = "{baseUrl}/api/workflows/{id}".format(baseUrl=credentials["darus"]["apiBaseUrl"], id=invocationId)
                try:
                    self.callDarusAPI(url, "post", expectedCode=202, nodata=True)
                except ApiCallFailedException as e:
                    ret = json.loads(str(e)[str(e).index('{"status"'):])
                    if self.calledMethod == "GET":
                        return output_html(ret)
                    else:
                        return ret, 401
                self.appStatus = "cancelled"
                self.setStatus(invocationId, self.appStatus)
                ret = {"invocationId": invocationId, "status": self.appStatus,
                       "message": "Publication workflow for dataset {} is cancelled ".format(self.getDatasetId(invocationId)), }
                if self.calledMethod == "GET":
                    return output_html(ret)
                else:
                    return ret

            if self.args["action"] == "validate":
                responseObject = self.checkAuth(self.args["authKey"], "curator")
                if responseObject != True:
                    return responseObject

                datasetId = self.getDatasetId(invocationId)

                datasetUrl = self.getDatasetUrl(datasetId)
                authors = []
                editorMails = []
                contactMails = []
                datasetTitle = ""

                authors, editorMails, contactMails, datasetTitle, datasetUrl, description, descriptionHtml = (
                    self.get_metadata(authors, editorMails, contactMails, datasetTitle, datasetUrl, datasetId))

                validation_out = ""
                validation_out_html = ""

                startUrl = ("{baseUrl}/" + urlPath + "/{id}/{auth}/").format(baseUrl=credentials["darus"]["baseUrl"],
                                                                             id=invocationId,
                                                                             auth=credentials["curator"]["authKey"])

                runUrl = ""

                errorStr = ("")

                tplDict = {"datasetDisplayName": datasetTitle, "datasetId": datasetId, "datasetUrl": datasetUrl,
                           "testrailUrl": runUrl, "releaseUrl": "{}ok".format(startUrl),
                           "lockUrl": "{}addLock".format(startUrl), "cancelUrl": "{}cancel".format(startUrl),
                           "removeLockUrl": "{}removeLock".format(startUrl),
                           "fileDoisOnUrl": "{}fileDoisOn".format(startUrl),
                           "fileDoisOffUrl": "{}fileDoisOff".format(startUrl), "numberOfFiles": "numberOfFilesMessage",
                           "errors": errorStr, "description": description, "validateUrl": "{}validate".format(startUrl),
                           "descriptionHtml": descriptionHtml, "validationOutput": validation_out,
                           "validationOutputHtml": validation_out_html, }

                self.prepare_mail(tplDict, invocationId, "Revalidierung in DaRUS - {}")
                logging.debug("Validation request already started...")

                ret = {"invocationId": invocationId, "status": "Revalidating ...",
                       "message": "Publication workflow will revalidate for dataset {}".format(datasetId), }

                if self.calledMethod == "GET":
                    return output_html(ret)
                else:
                    return ret

            if self.args["action"] == "fileDoisOff":
                message = "File DOIs are switched off"
                if self.switchFileDOIs(on=False):
                    message = "File DOIs are switched off"
                else:
                    message = ("Error while switching File DOIs off: {}"
                                                            .format(", ".join(errors)))
                ret = {"invocationId":invocationId, "status":self.appStatus, "message": message}
                if self.calledMethod == "GET":
                    return output_html(ret)
                else:
                    return jsonify(ret)

            if self.args["action"] == "fileDoisOn":
                message = "File DOIs are switched on"
                if self.switchFileDOIs(on=True):
                    message = "File DOIs are switched on"
                else:
                    message = ("Error while switching File DOIs on: {}"
                                                            .format(", ".join(errors)))
                ret = {"invocationId":invocationId, "status":self.appStatus, "message": message}
                if self.calledMethod == "GET":
                    return output_html(ret)
                else:
                    return jsonify(ret)

                # Nachricht an DaRUs mit Abbruch

        except BaseException:
            return {"invocationId": invocationId, "status": self.appStatus, "datasetId": self.datasetId}, 400

    def delete(self, invocationId):
        if self.calledMethod is None:  #
            self.calledMethod = "DELETE"  # #     args =  #  #  #
        jsonData = request.get_json()
        # jsonData = json.loads(args)  #
        responseObject = self.checkAuth(self.args["authKey"], "darus")  #
        if responseObject != True:
            return responseObject
        res = self.conn.execute("SELECT runId, datasetId, status FROM run WHERE invocationId=?", (invocationId,))  #
        try:

            r = res.fetchone()  #
            if r is None:  #
                return {"message": "Invocation ID {} is not existing".format(invocationId)}, 404
            else:
                runId = r[0]  #
                datasetId = r[1]
                self.appStatus = "aborted"
                if credentials["darus"]["mailer"] == "True":
                    self.sendMail("DaRUS Veröffentlichungsworkflow <darus-workflow@izus.uni-stuttgart.de>", credentials["curator"]["email"],
                                  "Veröffentlichungsworkflow abgebrochen", "tpl_mailAbbruch.txt",
                                  {"datasetId": datasetId, "runId": runId})  # #
                # E-Mail an Team3 mit Nachricht zum Abbruch  #     # Löschen? des Testrail-Laufes  #
                return {"invocationId": invocationId, "status": self.appStatus}, 200
        except:
            return {"invocationId": invocationId, "status": self.appStatus}, 409

# class checklist(Resource):
#   def get(self):
# api.add_resource(Publication, '/" + urlPath + "/<string:invocationId>')

urlPath = os.environ['URLPATH']
urlPathErrorMail = os.environ['URLPATHERRORMAIL']

with open("cred/credentials.json", "r") as cred_file:
    credentials = json.load(cred_file)
    if not valid_uuid(credentials["darus"]["apiKey"]):
        credentials["darus"]["apiKey"] = sys.argv[1][len("--apikey="):]
        if not valid_uuid(credentials["darus"]["apiKey"]):
            credentials["darus"]["apiKey"] = os.environ['APIKEY']
    if dummy_apiurl(credentials["darus"]["apiBaseUrl"]):
        credentials["darus"]["apiBaseUrl"] = sys.argv[2][len("--apiurl="):]

    if os.environ.get('authKeyDaRUS') is not None:
        credentials["darus"]["authKey"] = os.environ['authKeyDaRUS']
    if os.environ.get('authKeyCurator') is not None:
        credentials["curator"]["authKey"] = os.environ['authKeyCurator']
    if os.environ.get('validation') is not None:
        credentials["darus"]["validation"] = os.environ['validation']

mailCurator = credentials["curator"]["email"]

authKeyErrorMail = os.environ['authKeyErrorMail']

publication = Publication()

@app.route("/" + urlPath + "/running/<string:inputVar>", methods=["GET"])
def running(inputVar):
    return publication.running(inputVar)

@app.route("/" + urlPath + "/<string:invocationId>/<string:authKey>/<string:action>", methods=["GET", "PUT", "DELETE"])
def pubWorkflowAction(**kwargs):
    publication.args["invocationId"] = None
    publication.args["authKey"] = None
    publication.args["action"] = None
    if not kwargs.get("invocationId") is None:
        invocationId = kwargs.get("invocationId")
        if valid_uuid(invocationId):
            publication.args["invocationId"] = invocationId
    if not kwargs.get("authKey") is None:
        authKey = kwargs.get("authKey")
        if (credentials["darus"]["authKey"] == authKey or credentials["curator"]["authKey"] == authKey):
            publication.args["authKey"] = authKey
    if not kwargs.get("action") is None:
        action = kwargs.get("action")
        if valid_action(action):
            publication.args["action"] = action
    if publication.args["invocationId"] is not None and publication.args["authKey"] is not None:
        if publication.args["action"] is not None and request.method == 'GET':
            publication.setCalledMethod('GET')
            return publication.put(invocationId)
        elif publication.args["action"] is not None and request.method == 'PUT':
            publication.setCalledMethod('PUT')
            return publication.put(invocationId)
    else:
        return {"message": "Please provide correct URL parameters"}, 400
@app.route("/" + urlPath + "/<string:invocationId>/<string:authKey>", methods=["GET", "POST", "DELETE"])
def pubWorkflow(**kwargs):
    publication.args["invocationId"] = None
    publication.args["authKey"] = None
    if not kwargs.get("invocationId") is None:
        invocationId = kwargs.get("invocationId")
        if valid_uuid(invocationId):
            publication.args["invocationId"] = invocationId
    if not kwargs.get("authKey") is None:
        authKey = kwargs.get("authKey")
        if (credentials["darus"]["authKey"] == authKey or credentials["curator"]["authKey"] == authKey):
            publication.args["authKey"] = authKey
    if publication.args["invocationId"] is not None and publication.args["authKey"] is not None:
        if request.method == 'GET':
            publication.setCalledMethod('GET')
            return publication.get(invocationId)
        elif request.method == 'POST':
            publication.setCalledMethod('POST')
            return publication.post(invocationId)
        elif request.method == 'DELETE':
            publication.setCalledMethod('DELETE')
            return publication.delete(invocationId)
    else:
        return {"message": "Please provide correct URL parameters"}, 400

def stringToBool(boolValue):
    if boolValue == "True":
        return True
    elif boolValue == "False":
        return False

if __name__ == "__main__":
    app.run(stringToBool(debug=credentials["darus"]["debug"]))
