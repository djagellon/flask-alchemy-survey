# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START sheets_quickstart]
"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
import pprint

pp = pprint.PrettyPrinter(indent=2)
# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# Call the Sheets API
SPREADSHEET_ID = '1H7SdrzSY2PbW6n4bIs2ZjctXwZnN2kvU7hD7x64d1Pw'
RANGE_NAME = 'Sheet1!C2:H'
result = service.spreadsheets().values().get(
	spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME).execute()

values = result.get('values', [])

KEYS = ["type", "label", "condition", "title", "answers", "datalabel"]
survey = []

if not values:
    print('No data found.')
else:
    page = []

    for idx, row in enumerate(values):

        ## page means new list
        if len(row) == 1 and row[0] == 'page':
            print " ===== Page Break ====="
            survey.append(page)
            page = []
            continue

        ## no question label means answer values belong to previous row
        if not row[1]:
            print "===== PREV OBJ ====="
            question["answers"].append({
                "text": row[4],
                "label": row[5] 
            })
            continue


        question = dict(zip(KEYS, row))

        question["answers"] = [{
            "text": row[4],
            "label": row[5] 
        }]

        del question['datalabel']

        print "APPENDING: %s" % question
        page.append(question)

    # write to file
    file = open("surveys/test.json", "w")
    file.write(json.dumps(survey))

    pp.pprint(json.dumps(survey))