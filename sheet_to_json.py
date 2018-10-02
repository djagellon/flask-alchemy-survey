"""
Converts a google sheet to a JSON object and writes it to a file 
"""
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sys, json, ast
import pprint

pp = pprint.PrettyPrinter(indent=2)

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
# DEV_SPREADSHEET_ID = '1H7SdrzSY2PbW6n4bIs2ZjctXwZnN2kvU7hD7x64d1Pw'
SPREADSHEET_ID = '14qDT52ycqNx-XHp0x_IzSMwTRg81v2ED0Ae0wgwBlYI'

TEST_MODULE = 'test'
DEFAULT_RANGE = 'A2:O'
TEST_RANGE = '%s!%s' % (TEST_MODULE, DEFAULT_RANGE)

# Columns A-F
SHEET_HEADERS = ["type", "label", "condition", "title", "answers", "datalabel"]

# Columns F-O
OUTPUT_HEADERS = ["datalabel", "notes", "rating", "short", "long", "action", "metrics", "weight"]

# Action Plan K
ACTION_INDEX = 10

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

    # import pdb;pdb.set_trace()
    survey = []
    page = []
    output = {}

    for idx, row in enumerate(values):

        # Process Action Plan
        try:
            action_labels, action_object = get_action_labels(row[ACTION_INDEX])
        except IndexError:
            pass

        ## page means new list
        if row[0] == 'page':
            survey.append(page)
            page = []
            continue
        else:
            # Reporting Output. This saves to [module]_output.json
            # only the relevant rows: exclude 0-4
            row_output = dict(zip(OUTPUT_HEADERS, row[5:])) 
            row_output['actions'] = action_object
            try:
                output[row_output['datalabel']] = row_output
            except KeyError:
                pass

        answers = expand_answers(row, action_labels)

        ## no question label means answer values belong to previous row
        if not row[1]:
            question["answers"] = question["answers"] + answers
            continue

        question = dict(zip(SHEET_HEADERS, row[:6]))

        question["answers"] = answers 

        del question['datalabel']

        page.append(question)

    # write to files
    output_file = open("surveys/%s_output.json" % module, "w")
    output_file.write(json.dumps(output, indent=2, sort_keys=True))

    survey_file = open("surveys/%s.json" % module, "w")
    survey_file.write(json.dumps(survey, indent=2, sort_keys=True))

def expand_answers(row, actions):
    answer = []

    try:
        row_text = ast.literal_eval(row[4])
    except (ValueError, SyntaxError):
        row_text = row[4]

    if isinstance(row_text, list):
        for r in row_text:
            answer.append({
                "text": str(r),
                "label": row[5],
                "actions": actions
            })
    else:

        ans_obj = {
            "text": row[4],
            "label": row[5],
            "actions": actions
        }

        if '.other' in ans_obj['label']:
            ans_obj['open'] = True

        answer.append(ans_obj)

    return answer

def get_action_labels(content):
    labels = []
    action = {}

    lines = content.split('\n')

    for l in lines:
        line = l.split('~')

        if len(line) > 1:
            label = line[0].strip()
            labels.append(label)
            action[label] = line[1].strip()

    return labels, action


if __name__ == "__main__":
    main()