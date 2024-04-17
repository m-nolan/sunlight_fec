import numpy as np
import os
import pandas as pd

from argparse import ArgumentParser, BooleanOptionalAction
from datetime import datetime
from glob import glob
from itertools import chain, combinations

from project_params import DEFAULT_CANDIDATE_DATA

def parse_inputs():
    parser = ArgumentParser()
    parser.add_argument('-l','--log_results',action=BooleanOptionalAction)
    return parser.parse_args()

def powerset(iterable,min_size=0):
    "powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3) ..."
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(min_size,len(s)+1))

def load_findisc_data(id,schedule_name):
    committee_file_list = glob(f'./data/{schedule_name}_{id}_*.csv')
    if committee_file_list:
        file_path = committee_file_list[0]
        name = os.path.basename(file_path).split('_')[-1][:-4]
        return pd.read_csv(file_path,index_col=0,low_memory=False), name
    else:
        # no file for that committee/candidate id found. Skipping it this time
        return None, None

def init_log_file(schedule_name):
    log_file_path = f"./reports/{schedule_name}_overlap_{datetime.strftime(datetime.now(),'%Y-%m-%d_%H-%M-%S')}.md"
    return log_file_path

def log_findisc_overlap(log_file,ids,names,shared_values):
    with open(log_file,mode='a') as log_f:
        print(f"# {', '.join(ids)}\n",file=log_f) # added line breaks make github markdown happy
        print(f"{', '.join(names)}\n",file=log_f)
        print(f'overlaps found:\t{len(shared_values)}\n',file=log_f)
        [print(f'- {s_c}',file=log_f) for s_c in shared_values]
        print('\n',file=log_f)

def find_findisc_overlap(df_list,overlap_key,id_list,name_list,log_file=None,min_size=2):
    for subset_idx in powerset(np.arange(len(df_list)),min_size):
        subset_idx = list(subset_idx)
        _data_list = list(np.array(df_list,dtype=object)[subset_idx])
        _ids = list(np.array(id_list)[subset_idx])
        _names = list(np.array(name_list)[subset_idx])
        print(_ids)
        print(_names)
        shared_values = list(
            set.intersection(
                *[set(r_d.get(overlap_key,default=[])) for r_d in _data_list]
            )
        )
        shared_values.sort() # make the diffs make sense
        print(f'overlaps found:\t{len(shared_values)}')
        if log_file:
            log_findisc_overlap(log_file,_ids,_names,shared_values)

def main(log_results):
    candidate_data = DEFAULT_CANDIDATE_DATA
    _, candidate_ids, committee_ids = tuple(map(list, zip(*candidate_data)))
    receipt_data_list = []
    disbursement_data_list = []
    ind_exp_data_list = []
    committee_name_list = []
    candidate_name_list = []
    for _, can_id, com_id in candidate_data:
        _receipt_data, _committee_name = load_findisc_data(com_id,schedule_name='receipt')
        _disbursement_data, _ = load_findisc_data(com_id,schedule_name='disbursement')
        _ind_exp_data, _candidate_name = load_findisc_data(can_id,schedule_name='ind-exp')
        receipt_data_list.append(_receipt_data) if isinstance(_receipt_data,pd.DataFrame) else None
        disbursement_data_list.append(_disbursement_data) if isinstance(_disbursement_data,pd.DataFrame) else None
        ind_exp_data_list.append(_ind_exp_data) if isinstance(_ind_exp_data,pd.DataFrame) else None
        committee_name_list.append(_committee_name) if isinstance(_committee_name,str) else None
        candidate_name_list.append(_candidate_name) if isinstance(_candidate_name,str) else None
    # receipts (schedule a)
    print('SCHEDULE A - RECEIPTS\n')
    receipt_log_file = init_log_file('receipt') if log_results else None
    if len(receipt_data_list) > 1:
        find_findisc_overlap(receipt_data_list,'contributor_name',committee_ids,committee_name_list,receipt_log_file)
    # disbursements (schedule b)
    print('SCHEDULE B - DISBURSEMENTS\n')
    disbursement_log_file = init_log_file('disbursement') if log_results else None
    if len(disbursement_data_list) > 1:
        find_findisc_overlap(disbursement_data_list,'recipient_name',committee_ids,committee_name_list,disbursement_log_file)
    # independent expenditures (schedule e)
    print('SCHEDULE E - INDEPENDENT EXPENDITURES')
    ind_exp_log_file = init_log_file('ind-exp') if log_results else None
    if len(ind_exp_data_list) > 1:
        find_findisc_overlap(ind_exp_data_list,'committee',candidate_ids,candidate_name_list,ind_exp_log_file)

if __name__ == "__main__":
    args = parse_inputs()
    main(args.log_results)