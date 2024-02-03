import os
import pandas as pd
import requests as req

from argparse import ArgumentParser
from dotenv import load_dotenv
from glob import glob
from json.decoder import JSONDecodeError
from tqdm import tqdm

from open_fec_api import api_get
from project_params import DEFAULT_CANDIDATE_DATA, RECEIPT_API_URL_ROOT, DISBURSEMENT_API_URL_ROOT, IND_EXP_API_URL_ROOT

def parse_inputs():
    parser = ArgumentParser()
    parser.add_argument('-c','--committee_ids',nargs='*')
    return parser.parse_args()

def load_api_key(file='.env'):
    load_dotenv(file)

def configure_data_directory():
    if not os.path.exists('./data'):
        os.makedirs('./data')

def get_new_receipt_data(committee_id):
    schedule = 'a'
    existing_df_file_list = glob(f'./data/receipt_{committee_id}_*.csv')
    if existing_df_file_list:
        existing_df = pd.read_csv(existing_df_file_list[0],low_memory=False)
        min_date = existing_df['contribution_receipt_date'][0]
        _committee_name = os.path.basename(existing_df_file_list[0]).split('_')[-1][:-4]
    else:
        existing_df = None
        min_date = None
    committee_receipt_df, committee_name = get_findisc_df(committee_id,min_date,schedule)
    if committee_name is None:
        committee_name = _committee_name
    committee_receipt_df = pd.concat([committee_receipt_df,existing_df],ignore_index=True)
    save_findisc_df(committee_receipt_df,committee_id,committee_name,schedule)

def get_new_disbursement_data(committee_id):
    schedule = 'b'
    existing_df_file_list = glob(f'./data/disbursement_{committee_id}_*.csv')
    if existing_df_file_list:
        existing_df = pd.read_csv(existing_df_file_list[0],low_memory=False)
        min_date = existing_df['disbursement_date'][0]
        _committee_name = os.path.basename(existing_df_file_list[0]).split('_')[-1][:-4]
    else:
        existing_df = None
        min_date = None
    committee_disbursement_df, committee_name = get_findisc_df(committee_id,min_date,schedule)
    if committee_name is None:
        committee_name = _committee_name
    committee_disbursement_df = pd.concat([committee_disbursement_df,existing_df],ignore_index=True)
    save_findisc_df(committee_disbursement_df,committee_id,committee_name,schedule)

def get_new_ind_exp_data(candidate_id):
    pass

def api_return_to_df(r):
    exclude_list = list(set.intersection(
        set(r.json()['results'][0]),
        {'committee','contributor','contributor_name'}
    ))
    if r.json()['results']:
        df = pd.DataFrame.from_records(
            r.json()['results'],
            exclude=exclude_list
        )
        if 'contributor_name' in exclude_list:
            contributor_name = [_r['contributor_name'].replace(',',';') for _r in r.json()['results']]
            df['contributor_name'] = contributor_name
        #TODO: add other edge case formatting lines here
    return df

def get_findisc_df(id,min_date,schedule):
    create_api_call = {
        'a': create_receipt_api_call_url,
        'b': create_disbursement_api_call_url,
        'e': create_ind_exp_api_call_url,
    }.get(schedule)
    api_call_url = create_api_call(id,pagination_dict={},min_date=min_date)
    r = api_get(api_call_url)
    if r.json()['results']:
        name = r.json()['results'][0]['committee']['name'].replace(' ','-')
        print(name)
        df = api_return_to_df(r)
        for _ in tqdm(range(1,r.json()['pagination']['pages'])):
            api_call_url = create_api_call(
                id,
                pagination_dict=r.json()['pagination']['last_indexes'],
                min_date=min_date
            )
            r = api_get(api_call_url)
            df = pd.concat([df,api_return_to_df(r)],ignore_index=True)
    else:
        df = pd.DataFrame([])
        name = None
    return df, name

def save_findisc_df(df,id,name,schedule):
    schedule_name = {
        'a': 'receipt',
        'b': 'disbursement',
        'e': 'ind-exp',
    }.get(schedule)
    csv_file_name = f'./data/{schedule_name}_{id}_{name}.csv'
    print(f'saving data to:\t{csv_file_name}')
    df.to_csv(csv_file_name)

def api_request_dict(pagination_dict,min_date,**kwargs):
    request_dict = {
        **kwargs,
        'api_key': os.getenv("OPENFEC_API_KEY"),
        **pagination_dict,
    }
    if min_date:
        request_dict['min_date'] = min_date
    return request_dict

def api_str_from_dict(api_url_root,request_dict):
    return api_url_root + '&'.join([f'{k}={v}' for k, v in request_dict.items()])

#TODO: these functions should be one function? the candidate_id/committee_id in kwargs gums up the works
def create_receipt_api_call_url(committee_id,pagination_dict={},min_date=None,per_page=100):
    api_url_root = RECEIPT_API_URL_ROOT
    request_dict = api_request_dict(pagination_dict,min_date,committee_id=committee_id,per_page=per_page)
    return api_str_from_dict(api_url_root,request_dict)

def create_disbursement_api_call_url(committee_id,pagination_dict={},min_date=None,per_page=100):
    api_url_root = DISBURSEMENT_API_URL_ROOT
    request_dict = api_request_dict(pagination_dict,min_date,committee_id=committee_id,per_page=per_page)
    return api_str_from_dict(api_url_root,request_dict)

def create_ind_exp_api_call_url(candidate_id,pagination_dict={},min_date=None,per_page=100):
    api_url_root = IND_EXP_API_URL_ROOT
    request_dict = api_request_dict(pagination_dict,min_date,candidate_id=candidate_id,per_page=per_page)
    return api_str_from_dict(api_url_root,request_dict)

def main():
    candidate_data_list = DEFAULT_CANDIDATE_DATA
    load_dotenv()
    configure_data_directory()
    for candidate_id, committee_id in candidate_data_list:
        print(f'committee_id:\t{committee_id}')
        get_new_receipt_data(committee_id)
        get_new_disbursement_data(committee_id)
        get_new_ind_exp_data(candidate_id)

if __name__ == "__main__":
    args = parse_inputs()
    main()