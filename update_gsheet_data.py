import gspread
import csv
import os
import json

from glob import glob

from project_params import DEFAULT_CANDIDATE_DATA, GDRIVE_SCH_A_SHEET_NAME, GDRIVE_SCH_B_SHEET_NAME, GDRIVE_SCH_E_SHEET_NAME

SCH_DICT = {
    'schedule_a': 'receipt',
    'schedule_b': 'disbursement',
    'schedule_e': 'ind_exp'
}

def get_google_client():
    credentials = os.environ.get("GOOGLE_SECRET_KEY")
    return gspread.service_account_from_dict(json.loads(credentials))

def open_gsheet(client,schedule_key,candidate_key):
    sheet = client.open(sheetname=schedule_key)
    if candidate_key in sheet.worksheets():
        worksheet = sheet.worksheet(candidate_key)
    else:
        worksheet = sheet.add_worksheet(title=candidate_key)
    return worksheet

def get_candidate_schedule_file(candidate_id,committee_id,schedule_key):
    name_key = candidate_id if schedule_key == 'schedule_e' else committee_id
    return glob(os.path.join('data',f'{SCH_DICT[schedule_key]}_{name_key}*.csv'))

def update_gsheet(sheet,filename):
    data_out = []
    with open(filename,'r') as csvfile:
        csv_data = csv.reader(csvfile)
        for row in csv_data:
            data_out.append(row)
    sheet.update('A1',data_out)

def main():
    client = get_google_client()
    for schedule_key in [GDRIVE_SCH_A_SHEET_NAME, GDRIVE_SCH_B_SHEET_NAME, GDRIVE_SCH_E_SHEET_NAME]:
        for candidate_name, candidate_id, committee_id in DEFAULT_CANDIDATE_DATA:
            sheet = open_gsheet(client,schedule_key,candidate_name)
            schedule_filename = get_candidate_schedule_file(candidate_id, committee_id, schedule_key)
            update_gsheet(sheet,schedule_filename)

if __name__ == "__main__":
    main()