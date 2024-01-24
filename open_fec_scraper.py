import os
import pandas as pd
import requests as req

from argparse import ArgumentParser
from dotenv import load_dotenv
from glob import glob
from json.decoder import JSONDecodeError
from tqdm import tqdm

from open_fec_api import api_get

DEFAULT_COMMITTEES = [
    'C00848168',    # M. Wilkinson
    'C00655613',    # S. Lee
    'C00806307',    # B. Williams
    'C00765719',    # M. De La Cruz
    'C00801985',    # K. Kiley
    'C00726687',    # P. Junge
] #default committees

def parse_inputs():
    parser = ArgumentParser()
    parser.add_argument('-c','--committee_ids',nargs='*')
    return parser.parse_args()

def load_api_key(file='.env'):
    load_dotenv(file)

def configure_data_directory():
    if not os.path.exists('./data'):
        os.makedirs('./data')

def get_new_receipt_data(committee_ids):
    for committee_id in committee_ids:
        print(f'committee_id:\t{committee_id}')
        existing_df_file_list = glob(f'./data/receipt_{committee_id}_*.csv')
        if existing_df_file_list:
            existing_df = pd.read_csv(existing_df_file_list[0],low_memory=False)
            min_date = existing_df['contribution_receipt_date'][0]
            _committee_name = os.path.basename(existing_df_file_list[0]).split('_')[-1][:-4]
        else:
            existing_df = None
            min_date = None
        committee_receipt_df, committee_name = get_committee_recipt_df(committee_id,min_date)
        if committee_name is None:
            committee_name = _committee_name
        committee_receipt_df = pd.concat([committee_receipt_df,existing_df],ignore_index=True)
        save_receipt_df(committee_receipt_df,committee_id,committee_name)

def api_return_to_df(receipt_r):
    try:
        if receipt_r.json()['results']:
            receipt_df = pd.DataFrame.from_records(
                receipt_r.json()['results'],
                exclude=['committee','contributor','contributor_name']
            )
            contributor_name = [r['contributor_name'].replace(',',';') for r in receipt_r.json()['results']]
            receipt_df['contributor_name'] = contributor_name
        return receipt_df
    except:
        breakpoint()

def get_committee_recipt_df(committee_id,min_date):
    receipt_api_call_url = create_receipt_api_call_url(
        committee_id,
        pagination_dict={},
        min_date=min_date
    )
    receipt_r = api_get(receipt_api_call_url)
    if receipt_r.json()['results']:
        committee_name = receipt_r.json()['results'][0]['committee']['name'].replace(' ','-')
        print(committee_name)
        receipt_df = api_return_to_df(receipt_r)
        for _ in tqdm(range(1,receipt_r.json()['pagination']['pages'])):
            receipt_api_call_url = create_receipt_api_call_url(
                committee_id,
                pagination_dict=receipt_r.json()['pagination']['last_indexes'],
                min_date=min_date
            )
            receipt_r = api_get(receipt_api_call_url)
            receipt_df = pd.concat(
                [
                    receipt_df,
                    api_return_to_df(receipt_r)
                ],
                ignore_index=True
            )
    else:
        receipt_df = pd.DataFrame([])
        committee_name = None
    return receipt_df, committee_name

def save_receipt_df(receipt_df,committee_id,committee_name):
    csv_file_name = f'./data/receipt_{committee_id}_{committee_name}.csv'
    print(f'saving recipt data to:\t{csv_file_name}')
    receipt_df.to_csv(csv_file_name)

def create_receipt_api_call_url(committee_id,pagination_dict={},min_date=None,per_page=100):
    api_url_root = 'https://api.open.fec.gov/v1/schedules/schedule_a/?'
    request_dict = {
        'committee_id': committee_id, #input
        'per_page': per_page, #input
        'api_key': os.getenv("OPENFEC_API_KEY"),
        **pagination_dict,
    }
    if min_date:
        request_dict['min_date'] = min_date
    return api_url_root + '&'.join([f'{k}={v}' for k, v in request_dict.items()])

def main(committee_ids):
    if committee_ids:
        pass
    else:
        committee_ids = DEFAULT_COMMITTEES
    load_dotenv()
    configure_data_directory()
    get_new_receipt_data(committee_ids)

if __name__ == "__main__":
    args = parse_inputs()
    main(args.committee_ids)