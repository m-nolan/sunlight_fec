import numpy as np
import pandas as pd

from argparse import ArgumentParser, BooleanOptionalAction
from datetime import datetime
from itertools import chain, combinations

from open_fec_scraper import DEFAULT_COMMITTEES

def parse_inputs():
    parser = ArgumentParser()
    parser.add_argument('-c','--committee_ids',nargs='*')
    parser.add_argument('-l','--log_results',action=BooleanOptionalAction)
    return parser.parse_args()

def powerset(iterable,min_size=0):
    "powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3) ..."
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(min_size,len(s)+1))

def load_committee_data(committee_id):
    file_path = f'./data/receipt_{committee_id}.csv'
    return pd.read_csv(file_path,index_col=0,low_memory=False)

def init_log_file():
    log_file_path = f"./data/receipt_overlap_ \
        {datetime.strftime(datetime.now(),'%d-%m-%y_%H-%M-%S')}.md"
    # Path(log_file_path).touch()
    return log_file_path

def log_contributor_overlap(log_file,committee_ids,shared_contributors):
    with open(log_file,mode='a') as log_f:
        print(f"# {', '.join(committee_ids)}:",file=log_f)
        print(f'shared contributors found:\t{len(shared_contributors)}',file=log_f)
        [print(f'- {s_c}',file=log_f) for s_c in shared_contributors]
        print('\n',file=log_f)

def find_contributor_overlap(receipt_data_list,committee_ids,log_file=None,min_size=2):
    for subset_idx in powerset(np.arange(len(receipt_data_list)),min_size=2):
        subset_idx = list(subset_idx)
        _receipt_data_list = list(np.array(receipt_data_list,dtype=object)[subset_idx])
        _committee_ids = list(np.array(committee_ids)[subset_idx])
        print(_committee_ids)
        shared_contributors = list(
            set.intersection(
                *[set(r_d['contributor_name']) for r_d in _receipt_data_list]
            )
        )
        print(f'shared contributors found:\t{len(shared_contributors)}')
        if log_file:
            log_contributor_overlap(log_file,_committee_ids,shared_contributors)

def main(committee_ids,log_results):
    if committee_ids:
        pass
    else:
        committee_ids = DEFAULT_COMMITTEES
    receipt_data_list = [load_committee_data(c_id) for c_id in committee_ids]
    log_file = init_log_file() if log_results else None
    find_contributor_overlap(receipt_data_list,committee_ids,log_file)

if __name__ == "__main__":
    args = parse_inputs()
    main(args.committee_ids,args.log_results)