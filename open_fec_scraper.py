import os
import pandas as pd
import requests as req
import time

from argparse import ArgumentParser
from dotenv import load_dotenv
from glob import glob
from json.decoder import JSONDecodeError
from tqdm import tqdm

from open_fec_api import api_get
from project_params import DEFAULT_CANDIDATE_DATA, OPEN_FEC_API_URL_ROOT, RECEIPT_API_URL_ROOT, DISBURSEMENT_API_URL_ROOT, IND_EXP_API_URL_ROOT

def parse_inputs():
    parser = ArgumentParser()
    parser.add_argument('-c','--committee_ids',nargs='*')
    return parser.parse_args()

def load_api_key(file='.env'):
    if os.path.exists(file):
        load_dotenv(file)

def configure_data_directory():
    if not os.path.exists('./data'):
        os.makedirs('./data')

def get_new_schedule_data(id,schedule):
    schedule_name, date_key = {
        'a': ('receipt','contribution_receipt_date'),
        'b': ('disbursement','disbursement_date'),
        'e': ('ind-exp','expenditure_date'),
    }.get(schedule)
    existing_df_file_list = glob(f'./data/{schedule_name}_{id}_*.csv')
    if existing_df_file_list:
        existing_df = pd.read_csv(existing_df_file_list[0],low_memory=False,index_col=0)
        if date_key in existing_df.keys():
            existing_df[date_key] = pd.to_datetime(existing_df[date_key],format='ISO8601')
            min_date_ts = existing_df[date_key][0]# + pd.Timedelta(1, unit="d")  # Bumps to the next day to avoid repeats on limited calls
            min_date = None if existing_df.empty else min_date_ts.strftime('%Y-%m-%d')
        else:
            min_date = None
    else:
        existing_df = None
        min_date = None
    name = get_entity_name(id,schedule)
    data_df = get_findisc_df(id,min_date,schedule)
    if len(data_df) > 0:
        data_df = pd.concat([data_df,existing_df],ignore_index=True)
        # setting min-date to the most recent filing will get duplicate downloads, 
        # but I don't want to miss anything.
        data_df = data_df.drop_duplicates()
        save_findisc_df(data_df,id,name,schedule_name)

def api_return_to_df(r):
    exclude_list = list(set.intersection(
        set(r.json()['results'][0]),
        {'candidate','committee','contributor','contributor_name','recipient_committee'}
    ))
    if r.json()['results']:
        df = pd.DataFrame.from_records(
            r.json()['results'],
            exclude=exclude_list
        )
        if 'contributor_name' in exclude_list:
            contributor_name = [_r['contributor_name'].replace(',',';') for _r in r.json()['results']]
            df['contributor_name'] = contributor_name
        if 'committee' in exclude_list:
            committee_name = [_r['committee']['name'] for _r in r.json()['results']]
            df['committee'] = committee_name
        if 'recipient_committee' in exclude_list:
            recipient_committee_id = []
            for _r in r.json()['results']:
                recipient_committee_id.append(_r['recipient_committee']['committee_id'] if isinstance(_r['recipient_committee'],dict) else None)
            df['recipient_committee_id'] = recipient_committee_id
        #TODO: add other edge case formatting lines here
    return df

def get_entity_name(id, schedule):
    param_dict, str_sep = {
        'a': ({'api_url_root': OPEN_FEC_API_URL_ROOT+f'committee/{id}/?'}, ' '),
        'b': ({'api_url_root': OPEN_FEC_API_URL_ROOT+f'committee/{id}/?'}, ' '),
        'e': ({'api_url_root': OPEN_FEC_API_URL_ROOT+f'candidate/{id}/?'}, ', '),
    }.get(schedule)
    api_url = api_request_str_from_params(**param_dict)
    r = api_get(api_url)
    return r.json()['results'][0]['name'].replace(str_sep,'-')

def get_findisc_df(id,min_date,schedule):
    api_call_url = create_api_call_url(id,schedule,pagination_dict={},min_date=min_date)
    r = api_get(api_call_url)
    if r.json()['results']:
        df = api_return_to_df(r)
        for _ in tqdm(range(1,r.json()['pagination']['pages'])):
            api_call_url = create_api_call_url(
                id,
                schedule,
                pagination_dict=r.json()['pagination']['last_indexes'],
                min_date=min_date
            )
            r = api_get(api_call_url)
            df = pd.concat([df,api_return_to_df(r)],ignore_index=True)
    else:
        df = pd.DataFrame([])
    return df

def save_findisc_df(df,id,name,schedule_name):
    csv_file_name = f'./data/{schedule_name}_{id}_{name}.csv'
    print(f'saving data to:\t{csv_file_name}')
    df.to_csv(csv_file_name)

def api_request_str_from_params(api_url_root='',pagination_dict={},min_date=None,**kwargs):
    request_dict = {
        **kwargs,
        'api_key': os.getenv("OPENFEC_API_KEY"),
        **pagination_dict,
    }
    if min_date:
        request_dict['min_date'] = min_date
    return api_url_root + '&'.join([f'{k}={v}' for k, v in request_dict.items()])

def create_api_call_url(id,schedule,pagination_dict={},min_date=None,per_page=100):
    param_dict = {
        'a': {'api_url_root': RECEIPT_API_URL_ROOT,'committee_id': id},
        'b': {'api_url_root': DISBURSEMENT_API_URL_ROOT,'committee_id': id},
        'e': {'api_url_root': IND_EXP_API_URL_ROOT,'candidate_id': id,'support_oppose_indicator': 'S'},
    }.get(schedule)
    return api_request_str_from_params(pagination_dict=pagination_dict,min_date=min_date,per_page=per_page,**param_dict)

def main():
    candidate_data_list = DEFAULT_CANDIDATE_DATA
    load_dotenv()
    configure_data_directory()
    for _, candidate_id, committee_id in candidate_data_list:
        print(f'committee id:\t{committee_id}\tcandidate id:\t{candidate_id}')
        get_new_schedule_data(committee_id,'a')
        time.sleep(1)   # when nothing is added, it moves too quickly. This is to avoid 429 errors.
        get_new_schedule_data(committee_id,'b')
        time.sleep(1)
        get_new_schedule_data(candidate_id,'e')
        time.sleep(5)

if __name__ == "__main__":
    args = parse_inputs()
    main()