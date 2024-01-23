import numpy as np
import pandas as pd

from argparse import ArgumentParser
from itertools import chain, combinations

def parser_inputs():
    parser = ArgumentParser()
    parser.add_argument('-c','--committee_ids',nargs='*')
    return parser.parse_args()

def powerset(iterable):
    "powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3) ..."
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def load_committee_data(committee_id):
    file_path = f'./data/receipt_{committee_id}.csv'
    return pd.read_csv(file_path,index_col=0)

def find_contributor_overlap(receipt_data_list,committee_ids):
    for subset_idx in powerset(np.arange(len(receipt_data_list))):
        _receipt_data_list = receipt_data_list[subset_idx]
        _committee_ids = committee_ids[subset_idx]
        shared_contributors = list(
            set.intersection(
                *[set(r_d['contributor_name']) for r_d in _receipt_data_list]
            )
        )
        print(_committee_ids)
        print(_receipt_data_list)
    # return shared_contributors

def main(committee_ids):
    if committee_ids:
        pass
    else:
        committee_ids = [
            'C00848168',    # M. Wilkinson
            'C00655613',    # S. Lee
            'C00806307',    # B. Williams
            'C00765719',    # M. De La Cruz
            'C00801985',    # K. Kiley
        ] #default committees
    receipt_data_list = [load_committee_data(c_id) for c_id in committee_ids]
    find_contributor_overlap(receipt_data_list)

