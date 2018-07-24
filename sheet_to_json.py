"""
Converts a google sheet to a JSON object and writes it to a file 
"""
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sys, json
import pprint

pp = pprint.PrettyPrinter(indent=2)

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SPREADSHEET_ID = '1H7SdrzSY2PbW6n4bIs2ZjctXwZnN2kvU7hD7x64d1Pw'

TEST_MODULE = 'test'
DEFAULT_RANGE = 'C2:H'
TEST_RANGE = '%s!%s' % (TEST_MODULE, DEFAULT_RANGE)

SHEET_HEADERS = ["type", "label", "condition", "title", "answers", "datalabel"]

def get_sheet_from_google(sheet=TEST_RANGE):
    store = file.Storage('credentials.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)

    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=sheet).execute()

    return result

def main():

    if len(sys.argv[1:]):
        module = sys.argv[1:][0]
    else:
        module = TEST_MODULE 

    sheet = '%s!%s' % (module, DEFAULT_RANGE)
    google_data = get_sheet_from_google(sheet)

    values = google_data.get('values', [])

    survey = []
    page = []

    for idx, row in enumerate(values):

        ## page means new list
        if len(row) == 1 and row[0] == 'page':
            survey.append(page)
            page = []
            continue

        ## no question label means answer values belong to previous row
        if not row[1]:
            question["answers"].append({
                "text": row[4],
                "label": row[5] 
            })
            continue


        question = dict(zip(SHEET_HEADERS, row))

        question["answers"] = [{
            "text": row[4],
            "label": row[5] 
        }]

        del question['datalabel']

        page.append(question)

    # write to file
    file = open("surveys/%s.json" % module, "w")
    file.write(json.dumps(survey))

if __name__ == "__main__":
    main()
