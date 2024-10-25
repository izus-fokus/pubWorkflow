import sys
import requests

sys.path.append('..')

admin_json_response = {"status": "OK", "data": {"userCount": 275, "selectedPage": 1,
                                                "pagination": {"isNecessary": "true", "numResults": 275, "numResultsString": "275",
                                                               "docsPerPage": 25, "selectedPageNumber": 1, "pageCount": 11,
                                                               "hasPreviousPageNumber": "false", "previousPageNumber": 1,
                                                               "hasNextPageNumber": "true", "nextPageNumber": 2, "startResultNumber": 1,
                                                               "endResultNumber": 25, "startResultNumberString": "1",
                                                               "endResultNumberString": "25", "remainingResults": 250, "numberNextResults": 25,
                                                               "pageNumberList": [1, 2, 3, 4, 5]},
                                                "bundleStrings": {"userId": "ID", "userIdentifier": "Username", "lastName": "Last Name",
                                                                  "firstName": "First Name", "email": "Email", "affiliation": "Affiliation",
                                                                  "position": "Position", "isSuperuser": "Superuser",
                                                                  "authenticationProvider": "Authentication", "roles": "Roles",
                                                                  "createdTime": "Created Time", "lastLoginTime": "Last Login Time",
                                                                  "lastApiUseTime": "Last API Use Time"}, "users": [
        {"id": 219, "userIdentifier": "aamir.ahmad", "lastName": "Ahmad", "firstName": "Aamir", "email": "aamir.ahmad@ifr.uni-stuttgart.de",
         "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib",
         "roles": "Admin, Contributor", "createdTime": "2021-11-19 08:51:06.961", "lastLoginTime": "2021-11-19 08:51:06.961",
         "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 22, "userIdentifier": "ac102583", "lastName": "Hörner", "firstName": "Jörg Marcus",
         "email": "joerg-marcus.hoerner@f08.uni-stuttgart.de", "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false",
         "authenticationProvider": "shib", "roles": "Admin", "createdTime": "2018-11-14 08:49:27.507",
         "lastLoginTime": "2018-11-14 08:49:27.507", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 25, "userIdentifier": "ac103914", "lastName": "Müller", "firstName": "Christoph",
         "email": "christoph.mueller@visus.uni-stuttgart.de", "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false",
         "authenticationProvider": "shib", "roles": "Admin, Contributor, Curator", "createdTime": "2018-11-26 18:09:27.452",
         "lastLoginTime": "2018-11-26 18:09:27.452", "lastApiUseTime": "2021-12-27 16:41:45.057", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 24, "userIdentifier": "ac104337", "lastName": "Schön", "firstName": "Alexander", "email": "alexander.schoen@ifb.uni-stuttgart.de",
         "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin",
         "createdTime": "2018-11-26 12:02:43.414", "lastLoginTime": "2018-11-26 12:02:43.414", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 6, "userIdentifier": "ac104649", "lastName": "Selent", "firstName": "Björn", "email": "bjoern.selent@tik.uni-stuttgart.de",
         "affiliation": "University of Stuttgart (Test)", "isSuperuser": "true", "authenticationProvider": "shib", "roles": "Admin, Contributor",
         "createdTime": "2018-09-19 10:01:45.573", "lastLoginTime": "2018-09-19 10:01:45.573", "lastApiUseTime": "2023-08-09 15:21:08.463",
         "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 52, "userIdentifier": "ac106424", "lastName": "Martens", "firstName": "Sabine", "email": "sabine.martens@mpa.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "",
         "createdTime": "2019-02-12 11:36:40.854", "lastLoginTime": "2019-02-12 11:36:40.854", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 7, "userIdentifier": "ac106592", "lastName": "Flemisch", "firstName": "Bernd", "email": "bernd.flemisch@iws.uni-stuttgart.de",
         "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib",
         "roles": "Admin, Contributor, Member", "createdTime": "2018-09-24 10:23:50.654", "lastLoginTime": "2018-09-24 10:23:50.654",
         "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 14, "userIdentifier": "ac107399", "lastName": "Puckert", "firstName": "Dominik", "email": "dominik.puckert@iag.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib",
         "roles": "Contributor, Curator", "createdTime": "2018-10-15 16:36:43.319", "lastLoginTime": "2018-10-15 16:36:43.319",
         "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 59, "userIdentifier": "ac107436", "lastName": "Lemmer", "firstName": "Frank", "email": "frank.lemmer@ifb.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart", "isSuperuser": "false", "authenticationProvider": "shib",
         "roles": "Contributor, Dataverse + Dataset Creator, Member", "createdTime": "2019-03-14 08:44:00.161",
         "lastLoginTime": "2019-03-14 08:44:00.161", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 11, "userIdentifier": "ac108829", "lastName": "Schembera", "firstName": "Björn",
         "email": "bjoern.schembera@ians.uni-stuttgart.de", "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false",
         "authenticationProvider": "shib", "roles": "Admin, Contributor, Member", "createdTime": "2018-10-09 15:44:32.669",
         "lastLoginTime": "2018-10-09 15:44:32.669", "lastApiUseTime": "2020-10-21 11:53:39.733", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 78, "userIdentifier": "ac109435", "lastName": "Röhrle", "firstName": "Oliver", "email": "roehrle@simtech.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Member",
         "createdTime": "2019-03-22 09:39:22.243", "lastLoginTime": "2019-03-22 09:39:22.243", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 2, "userIdentifier": "ac112994", "lastName": "Seeland", "firstName": "Per Pascal", "email": "pascal.seeland@tik.uni-stuttgart.de",
         "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "",
         "createdTime": "2018-09-13 13:32:38.629", "lastLoginTime": "2018-09-13 13:32:38.629", "lastApiUseTime": "2022-12-18 17:01:44.797",
         "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 19, "userIdentifier": "ac115659", "lastName": "Staudenmeyer", "firstName": "Jennifer",
         "email": "jennifer.staudenmeyer@iag.uni-stuttgart.de", "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false",
         "authenticationProvider": "shib", "roles": "Admin, Contributor, Curator", "createdTime": "2018-10-18 14:30:27.434",
         "lastLoginTime": "2018-10-18 14:30:27.434", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 23, "userIdentifier": "ac116241", "lastName": "Heine", "firstName": "Claus-Justus",
         "email": "claus-justus.heine@ians.uni-stuttgart.de", "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false",
         "authenticationProvider": "shib", "roles": "Admin", "createdTime": "2018-11-14 11:56:57.695",
         "lastLoginTime": "2018-11-14 11:56:57.695", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 79, "userIdentifier": "ac118864", "lastName": "Lipp", "firstName": "Melanie", "email": "melanie.lipp@iws.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin, Contributor, Member",
         "createdTime": "2019-03-25 18:24:48.921", "lastLoginTime": "2019-03-25 18:24:48.921", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 70, "userIdentifier": "ac119259", "lastName": "Gärtner", "firstName": "Markus", "email": "markus.gaertner@ims.uni-stuttgart.de",
         "affiliation": "University of Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib",
         "roles": "Admin, Contributor", "createdTime": "2019-03-19 08:58:17.512", "lastLoginTime": "2019-03-19 08:58:17.512",
         "lastApiUseTime": "2021-02-01 14:35:45.477", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 8, "userIdentifier": "ac120257", "lastName": "Schneider", "firstName": "Martin", "email": "martin.schneider@iws.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin, Contributor",
         "createdTime": "2018-10-04 11:54:33.179", "lastLoginTime": "2018-10-04 11:54:33.179", "lastApiUseTime": "2018-11-09 08:56:23.587",
         "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 65, "userIdentifier": "ac121045", "lastName": "Brencher", "firstName": "Lukas", "email": "lukas.brencher@ians.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin, Contributor",
         "createdTime": "2019-03-18 09:13:45.449", "lastLoginTime": "2019-03-18 09:13:45.449", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 12, "userIdentifier": "ac121490", "lastName": "Kraus", "firstName": "Hamzeh", "email": "hamzeh.kraus@itt.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart", "isSuperuser": "false", "authenticationProvider": "shib",
         "roles": "Admin, Contributor, Dataset Creator", "createdTime": "2018-10-10 08:32:29.795", "lastLoginTime": "2018-10-10 08:32:29.795",
         "lastApiUseTime": "2019-07-19 13:41:41.509", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 61, "userIdentifier": "ac122137", "lastName": "Buchfink", "firstName": "Patrick",
         "email": "patrick.buchfink@ians.uni-stuttgart.de", "affiliation": "University of Stuttgart (Test v3.4)", "isSuperuser": "false",
         "authenticationProvider": "shib", "roles": "Admin, Contributor", "createdTime": "2019-03-15 10:52:55.415",
         "lastLoginTime": "2019-03-15 10:52:55.415", "deactivated": "false", "mutedEmails": [], "mutedNotifications": []},
        {"id": 53, "userIdentifier": "ac122264", "lastName": "Bross", "firstName": "Fabian", "email": "fabian.bross@ling.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "",
         "createdTime": "2019-02-13 10:09:28.842", "lastLoginTime": "2019-02-13 10:09:28.842", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 17, "userIdentifier": "ac122381", "lastName": "Scholz", "firstName": "Simon", "email": "simon.scholz@iws.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test, Alt!)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin, Member",
         "createdTime": "2018-10-18 11:29:00.12", "lastLoginTime": "2018-10-18 11:29:00.12", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []},
        {"id": 71, "userIdentifier": "ac122448", "lastName": "Kern", "firstName": "Michal", "email": "michal.kern@ipc.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin, Contributor",
         "createdTime": "2019-03-19 10:33:08.977", "lastLoginTime": "2019-03-19 10:33:08.977", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []}, {"id": 10, "userIdentifier": "ac122675", "lastName": "Reuschen", "firstName": "Sebastian",
                                     "email": "sebastian.reuschen@iws.uni-stuttgart.de", "affiliation": "Universität Stuttgart (Test)",
                                     "isSuperuser": "false", "authenticationProvider": "shib", "roles": "Admin, Contributor",
                                     "createdTime": "2018-10-08 14:36:16.19", "lastLoginTime": "2018-10-08 14:36:16.19", "deactivated": "false",
                                     "mutedEmails": [], "mutedNotifications": []},
        {"id": 58, "userIdentifier": "ac123721", "lastName": "Fürst", "firstName": "Holger", "email": "holger.fuerst@ifb.uni-stuttgart.de",
         "affiliation": "Universität Stuttgart (Test)", "isSuperuser": "false", "authenticationProvider": "shib", "roles": "",
         "createdTime": "2019-02-20 10:42:05.073", "lastLoginTime": "2019-02-20 10:42:05.073", "deactivated": "false", "mutedEmails": [],
         "mutedNotifications": []}]}}


def test_get(client, credentials, mocker):
    url = credentials["darus"]["baseUrl"] + "api/admin/list-users/"
    mocker.patch("requests.get", return_value=admin_json_response, status_code=200)
    try:
        tr = requests.get(url)
        assert tr["status"] == "OK"
    except Exception as e:
        print(e)
