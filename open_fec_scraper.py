import os
import pandas as pd
import requests as req

from argparse import ArgumentParser
from dotenv import load_dotenv
from tqdm import tqdm

DEFAULT_COMMITTEES = [
    'C00848168',    # M. Wilkinson
    'C00655613',    # S. Lee
    'C00806307',    # B. Williams
    'C00765719',    # M. De La Cruz
    'C00801985',    # K. Kiley
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

def get_receipt_data(committee_ids):
    for committee_id in committee_ids:
        print(f'committee_id:\t{committee_id}')
        committee_receipt_df = get_committee_recipt_df(committee_id)
        save_receipt_df(committee_receipt_df,committee_id)

def api_return_to_df(receipt_r):
    try:
        receipt_df = pd.DataFrame.from_records(
            receipt_r.json()['results'],
            exclude=['committee','contributor','contributor_name']
        )
    except:
        breakpoint()
    contributor_name = [r['contributor_name'].replace(',',';') for r in receipt_r.json()['results']]
    receipt_df['contributor_name'] = contributor_name
    return receipt_df

def get_committee_recipt_df(committee_id):
    receipt_api_call_url = create_receipt_api_call_url(committee_id)
    receipt_r = req.get(receipt_api_call_url)
    if receipt_r.status_code == 200:
        receipt_df = api_return_to_df(receipt_r)
        for _ in tqdm(range(1,receipt_r.json()['pagination']['pages'])):
            receipt_api_call_url = create_receipt_api_call_url(
                committee_id,
                pagination_dict=receipt_r.json()['pagination']['last_indexes']
            )
            receipt_r = req.get(receipt_api_call_url)
            receipt_df = pd.concat(
                [
                    receipt_df,
                    api_return_to_df(receipt_r)
                ],
                ignore_index=True
            )
        return receipt_df
    else:
        raise(req.HTTPError(receipt_api_call_url,receipt_r))

def save_receipt_df(receipt_df,committee_id):
    csv_file_name = f'./data/receipt_{committee_id}.csv'
    print(f'saving recipt data to:\t{csv_file_name}')
    receipt_df.to_csv(csv_file_name)

def create_receipt_api_call_url(committee_id,pagination_dict={},per_page=100):
    api_url_root = 'https://api.open.fec.gov/v1/schedules/schedule_a/?'
    request_dict = {
        'committee_id': committee_id, #input
        'per_page': per_page, #input
        'api_key': os.getenv("OPENFEC_API_KEY"),
        **pagination_dict,
    }
    return api_url_root + '&'.join([f'{k}={v}' for k, v in request_dict.items()])

def main(committee_ids):
    if committee_ids:
        pass
    else:
        committee_ids = DEFAULT_COMMITTEES
    load_dotenv()
    configure_data_directory()
    get_receipt_data(committee_ids)

if __name__ == "__main__":
    args = parse_inputs()
    main(args.committee_ids)