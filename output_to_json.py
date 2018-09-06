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
DEFAULT_RANGE = 'F2:O'
TEST_RANGE = '%s!%s' % (TEST_MODULE, DEFAULT_RANGE)

OUTPUT_HEADERS = ["question", "ans", "datalabel", "notes", "rating", "short", "long", "action", "metrics", "weight"]

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

    questions = {}
    output = {}

    for idx, row in enumerate(values):


        if row:
            row_data = dict(zip(OUTPUT_HEADERS, row))

            q_label = row_data['datalabel'].split('.')[0]

            if row_data['question']:
                questions[q_label] = row_data['question']

            if not row_data['question']:
                row_data['question'] = questions[q_label]

            output[row_data['datalabel']] = row_data

    # import pdb;pdb.set_trace()
    # write to output to file
    file = open("surveys/%s_output.json" % module, "w")
    file.write(json.dumps(output, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
