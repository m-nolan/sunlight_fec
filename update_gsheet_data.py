import csv
import gspread
import json
import os
import platform

from glob import glob

from project_params import DEFAULT_CANDIDATE_DATA, GDRIVE_SCH_A_SHEET_NAME, GDRIVE_SCH_B_SHEET_NAME, GDRIVE_SCH_E_SHEET_NAME

SCH_DICT = {
    'schedule_a': 'receipt',
    'schedule_b': 'disbursement',
    'schedule_e': 'ind-exp'
}

def get_google_client():
    os_name = platform.system()
    if os_name == 'Windows':
        with open('google_auth_secret.json','r') as gskf:
            credentials = gskf.read()
    else:
        credentials = os.environ.get("GOOGLE_SECRET_KEY")
    return gspread.service_account_from_dict(json.loads(credentials))

def open_gsheet(client,schedule_key,candidate_key):
    sheet = client.open(schedule_key)
    if candidate_key in [ws.title for ws in sheet.worksheets()]:
        worksheet = sheet.worksheet(candidate_key)
    else:
        worksheet = sheet.add_worksheet(title=candidate_key,rows=1,cols=1)
    return worksheet

def get_candidate_schedule_file(candidate_id,committee_id,schedule_key):
    name_key = candidate_id if schedule_key == 'schedule_e' else committee_id
    file_list = glob(os.path.join('data',f'{SCH_DICT[schedule_key]}_{name_key}*.csv'))
    filename = file_list[0] if len(file_list) > 0 else None
    return filename

def update_gsheet(sheet,filename):
    data_out = []
    with open(filename,'r') as csvfile:
        csv_data = csv.reader(csvfile)
        for row in csv_data:
            data_out.append(row)    # TODO: move error handling down to this level, out of main()
    sheet.update(data_out,'A1')

def main():
    client = get_google_client()
    for schedule_key in [GDRIVE_SCH_A_SHEET_NAME, GDRIVE_SCH_B_SHEET_NAME, GDRIVE_SCH_E_SHEET_NAME]:
        print(f"Updating filings for: {schedule_key}")
        for candidate_name, candidate_id, committee_id in DEFAULT_CANDIDATE_DATA:
            print(f"Moving data for: {candidate_name}")
            try:
                sheet = open_gsheet(client,schedule_key,candidate_name)
            except:
                print(f'could not open google sheet for {candidate_name} - proceeding to next candidate')
                continue
            schedule_filename = get_candidate_schedule_file(candidate_id, committee_id, schedule_key)
            if schedule_filename:
                print(f"File found: {schedule_filename}")
                try:
                    update_gsheet(sheet,schedule_filename)
                except gspread.exceptions.APIError:
                    print('ERROR: Google sheet at maximum size. Cannot append data.')
                else:
                    print('Unknown error occurred - proceeding to next candidate dataset.')

if __name__ == "__main__":
    main()