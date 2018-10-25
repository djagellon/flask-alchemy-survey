"""
Converts a google sheet to a JSON object and writes it to a file 
"""
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import itertools
import sys, json, ast
import pprint

pp = pprint.PrettyPrinter(indent=2)

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SPREADSHEET_ID = '14qDT52ycqNx-XHp0x_IzSMwTRg81v2ED0Ae0wgwBlYI'

DEFAULT_RANGE = 'A2:O'

# Columns A-F
SHEET_HEADERS = ["type", "label", "condition", "title", "answers", "datalabel"]

# Columns B-E
OUTPUT_RANGE = 'B2:E'
OUTPUT_HEADERS = ["datalabel", "notes", "short", "long"]

# Columns C-G
WEIGHT_HEADERS = ["datalabel", "score", "weight", "balance"]
WEIGHT_RANGE = 'D2:G'

def get_sheet_from_google(sheet):
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
        raise ValueError("You must specify a module.")


    if module == 'outputs':
        generate_outputs()
    else:
        generate_module(module)    

def generate_outputs():

    weight_sheet = 'Weight_Score!%s' % (WEIGHT_RANGE)
    weight_data = get_sheet_from_google(weight_sheet)
    weight_values = weight_data.get('values', [])
    weight_object = values_to_objects(weight_values, WEIGHT_HEADERS)

    output_sheet = 'output!%s' % (OUTPUT_RANGE)
    output_data = get_sheet_from_google(output_sheet)
    output_values = output_data.get('values', [])
    output_object = values_to_objects(output_values, OUTPUT_HEADERS)

    howto_sheet = 'HowTo!%s' % (OUTPUT_RANGE)
    howto_data = get_sheet_from_google(howto_sheet)
    howto_values = howto_data.get('values', [])

    action_sheet = 'ActionPlan!%s' % (OUTPUT_RANGE)
    action_data = get_sheet_from_google(action_sheet)
    action_values = action_data.get('values', [])
    action_object, action_lookup = action_to_objects(action_values, howto_values)

    for k, v in output_object.iteritems():
        weight = weight_object.get(k, None)
        v['actions'] = action_lookup.get(k, None)

        if weight:
            v.update(weight)

    output_file = open("surveys/outputs.json", "w")
    output_file.write(json.dumps(output_object, indent=2, sort_keys=True))

def generate_module(module):
    survey = []
    page = []

    survey_sheet = '%s!%s' % (module, DEFAULT_RANGE)
    survey_data = get_sheet_from_google(survey_sheet)
    survey_values = survey_data.get('values', [])

    for idx, row in enumerate(survey_values):

        ## page means new list
        if row[0] == 'page':
            survey.append(page)
            page = []
            continue

        answers = expand_answers(row)

        ## no question label means answer values belong to previous row
        if not row[1]:
            question["answers"] = question["answers"] + answers
            continue

        question = dict(zip(SHEET_HEADERS, row[:6]))

        question["answers"] = answers 

        del question['datalabel']

        page.append(question)

    survey_file = open("surveys/%s.json" % module, "w")
    survey_file.write(json.dumps(survey, indent=2, sort_keys=True))

def action_to_objects(actions, howto):
    ''' return list of actions by datalabel and
    write action.json lookup file
    TODO: probably weights
    '''

    datalabel = ''
    actions_per_datalabel = {}
    action_object = {}
    howto_object = {}

    # for how in howto:
    #     #build the how to object
    #     import pdb;pdb.set_trace()
    #     if len(how) > 1:
    #         label, text = (how[1:])
    #         howto_object[label] = text

    for action in actions:
        if action and action[0]:
            datalabel = action[0]
            actions_per_datalabel[datalabel] = []
        else:
            datalabel = datalabel

        action_object[datalabel] = action_object.get(datalabel, {})

        if len(action) < 2:
            actions_per_datalabel[datalabel] = []
        else: 
            actionlabel = action[1]
            actions_per_datalabel[datalabel].append(actionlabel)
            action_object[datalabel][actionlabel] = {
                'plan': action[2],
                'how': howto_object.get(actionlabel, None)
            }

    return actions_per_datalabel, action_object


def values_to_objects(values, header):
    data = {}

    for value in values:
        if not value:
            continue

        data[value[0]] = {} 

        for i in itertools.izip_longest(header[1:], value[1:], ''):
            data[value[0]][i[0]] = i[1]

    # import pdb;pdb.set_trace()
    return data

def expand_answers(row):
    answer = []

    try:
        row_text = ast.literal_eval(row[4])
    except (ValueError, SyntaxError):
        row_text = row[4]

    if isinstance(row_text, list):
        for r in row_text:
            answer.append({
                "text": str(r),
                "label": row[5]
            })
    else:
        ans_obj = {
            "text": row[4],
            "label": row[5]
        }

        if '.other' in ans_obj['label']:
            ans_obj['open'] = True

        answer.append(ans_obj)

    return answer


if __name__ == "__main__":
    main()