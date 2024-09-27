import numpy as np
import os
import pandas as pd

from datetime import datetime
from glob import glob

from project_params import DEFAULT_CANDIDATE_DATA

N_CONTRIB = 100

def get_candidate_df(candidate_data=DEFAULT_CANDIDATE_DATA):
    columns=['candidate_name','candidate_id','committee_id']
    return pd.DataFrame(candidate_data,columns=columns)

def get_schedule_params(schedule_key):
    search_key = {'a': 'receipt', 'b': 'disbursement', 'e': 'ind-exp'}[schedule_key]
    committee_key = {'a': 'committee_id', 'b': 'committee_id', 'e': 'candidate_id'}[schedule_key]
    party_key = 'candidate_name'
    group_key = {'a': 'contributor_name', 'b': 'recipient_name', 'e': 'payee_name'}[schedule_key]
    amount_key = {'a': 'contribution_receipt_amount', 'b': 'disbursement_amount', 'e': 'expenditure_amount'}[schedule_key]
    return search_key, committee_key, party_key, group_key, amount_key

def get_schedule_data(schedule_key, candidate_df, search_key, committee_key, party_key):
    sch_file_list = glob(os.path.join('data',f'{search_key}*.csv'))
    sch_df = pd.concat([pd.read_csv(sch_file,index_col=0,low_memory=False) for sch_file in sch_file_list],ignore_index=True)
    for idx, row in candidate_df.iterrows():
        sch_df.loc[sch_df[committee_key]==row[committee_key],party_key] = row.candidate_name
    if schedule_key == 'a':
        sch_df = sch_df[sch_df.is_individual]
    elif schedule_key in ['b']:
        sch_df = sch_df[~sch_df.payee_first_name.isna()]
    return sch_df

def get_overlap_df(sch_df,party_key,group_key,amount_key):
    party_unique_candidates = sch_df.groupby(group_key)[party_key].unique().to_frame()
    party_unique_candidates['count'] = [len(p) for p in party_unique_candidates[party_key]]
    party_total = sch_df.groupby(group_key)[amount_key].sum().to_frame()
    party_overlap_df = pd.merge(party_unique_candidates,party_total,on=group_key)
    party_overlap_df.sort_values(by='count',ascending=False,inplace=True)
    return party_overlap_df

def write_overlap_report_file(party_overlap_df,schedule_key,party_key,amount_key,n_contrib=N_CONTRIB):
    date_str = datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S')
    report_file_name = os.path.join('reports',f'sch_{schedule_key}_party_overlap_{date_str}.md')
    with open(report_file_name,'w') as rf:
        print(f'# FEC Schedule {schedule_key.upper()} Overlap Report\n',file=rf)
        print(date_str,file=rf)
        print('\n')
        idx = 0
        for party_name, row in party_overlap_df[:n_contrib].iterrows():
            print(f'{idx}. {party_name}',file=rf)
            print(f'\t- total: ${row[amount_key]:0.2f}',file=rf)
            print(f'\t- {", ".join([s for s in row[party_key] if isinstance(s,str)])}\n',file=rf)   # TODO: These nan values should not be here. This is a bucket fix.
            idx += 1

def write_overlap_report(schedule_key, candidate_df):
    search_key, committee_key, party_key, group_key, amount_key = get_schedule_params(schedule_key)
    sch_df = get_schedule_data(schedule_key,candidate_df,search_key,committee_key,party_key)
    party_overlap_df = get_overlap_df(sch_df,party_key,group_key,amount_key)
    write_overlap_report_file(party_overlap_df,schedule_key,party_key,amount_key)

def main():
    candidate_df = get_candidate_df()
    write_overlap_report('a',candidate_df)
    write_overlap_report('b',candidate_df)
    write_overlap_report('e',candidate_df)

if __name__ == "__main__":
    main()