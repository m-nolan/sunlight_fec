import gspread
import json
import os

from glob import glob

DATA_DIR = './data'

def get_gsa_key():
    return json.loads(os.getenv('GSA_KEY_DICT').replace('\n','').replace('/',''))

def get_csv_files(data_dir = './data'):
    return glob(os.path.join(data_dir,'*.csv'))

def get_md_files(data_dir = './data'):
    return glob(os.path.join(data_dir,'*.md'))

def update_gdrive_sheet_from_csv(csv_file):
    pass

def update_gdrive_file(md_file):
    pass

def main():
    csv_file_list = get_csv_files()
    md_file_list = get_md_files()
    for csv_file in csv_file_list:
        update_gdrive_sheet_from_csv(csv_file)
    for md_file in md_file_list:
        update_gdrive_file(md_file)

if __name__ == "__main__":
    main()