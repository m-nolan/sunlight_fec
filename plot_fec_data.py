import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from glob import glob

from project_params import DEFAULT_CANDIDATE_DATA, SCHEDULE_KEY_DICT

N_PARTIES = 20
MAX_NAME_LEN = 20
EXCLUDE_LIST = ['WINRED']

def find_data_file(search_str):
    data_file_candidates = glob(os.path.join('data',search_str))
    if data_file_candidates:
        return data_file_candidates[0] # there should only be one

def get_schedule_data(candidate_id, committee_id, schedule_key):
    sch_prefix = {'a':'receipt','b':'disbursement','e':'ind-exp'}[schedule_key]
    campaign_key = candidate_id if schedule_key == 'e' else committee_id
    sch_data_file = find_data_file(f'{sch_prefix}_{campaign_key}_*.csv')
    sch_df = pd.read_csv(sch_data_file,index_col=0,low_memory=False)
    if len(sch_df) > 0:
        sch_df[SCHEDULE_KEY_DICT[schedule_key]['date_key']] = pd.to_datetime(sch_df[SCHEDULE_KEY_DICT[schedule_key]['date_key']],format='ISO8601')
        sch_df = clean_df(sch_df,SCHEDULE_KEY_DICT[schedule_key]['party_key'],EXCLUDE_LIST)
    return sch_df

def plot_top_schedule_data(df,schedule_key,candidate_name):
    top_party_df = get_top_parties(df,schedule_key,**SCHEDULE_KEY_DICT[schedule_key])
    fig, ax = timeline_bubbleplot(df,top_party_df,schedule_key,n_parties=N_PARTIES,**SCHEDULE_KEY_DICT[schedule_key])
    fig.show()
    try:
        fig.savefig(os.path.join('figures',f'top_{N_PARTIES}_sch_{schedule_key}_{candidate_name}.png'))
    except:
        breakpoint()

def get_top_parties(df,schedule_key,party_key,payment_key,date_key):
    if schedule_key == 'a':
        df = df[df.is_individual]
    if schedule_key == 'b':
        df = df[~df.payee_last_name.isna()]
    top_party_df = df.groupby([party_key])[payment_key].sum().sort_values(ascending=False)
    return top_party_df[top_party_df.values > 0]

def clean_df(df,party_key,exclude_list):
    return df[~df[party_key].isin(exclude_list)]

def timeline_bubbleplot(df,top_party_df,schedule_key,n_parties,party_key,payment_key,date_key):
    n_parties = len(top_party_df) if len(top_party_df) < n_parties else n_parties
    fig_size = (8.5,np.max((4.6*n_parties/10,6)))
    fig, ax = plt.subplots(1,1,dpi=100,figsize=fig_size,constrained_layout=True)
    marker_scale = 0.05
    ylabel_list = []
    for idx in range(n_parties):
        party_name = top_party_df.index[idx]
        print_party_name = party_name if len(party_name) < MAX_NAME_LEN else party_name[:MAX_NAME_LEN] + '...'
        ylabel_list.append(f"{print_party_name} (${top_party_df.values[idx]:.0f})")
        payment_series = df[df[party_key] == party_name].groupby(date_key)[payment_key].sum()
        ax.scatter(
            x=payment_series.index,
            y=-idx*np.ones(len(payment_series)),
            s=marker_scale*payment_series.values,
            alpha=0.5
        )
    fig.show()
    ax.set_yticks(np.arange(0,-n_parties,-1))
    ax.set_yticklabels(ylabel_list)
    ax.tick_params(axis='x', labelrotation=90)
    ax.set_xlabel('Date')
    ax.set_ylabel('Donor')
    ax.set_title(f'Campaign Payments v. Time: Schedule {schedule_key.upper()}')
    return fig, ax

def main():
    for candidate_name, candidate_id, committee_id in DEFAULT_CANDIDATE_DATA:
        sch_a_df = get_schedule_data(candidate_id,committee_id,'a')
        sch_b_df = get_schedule_data(candidate_id,committee_id,'b')
        sch_e_df = get_schedule_data(candidate_id,committee_id,'e')
        if len(sch_a_df) > 0: plot_top_schedule_data(sch_a_df,'a',candidate_name)
        if len(sch_b_df) > 0: plot_top_schedule_data(sch_b_df,'b',candidate_name)
        if len(sch_e_df) > 0: plot_top_schedule_data(sch_e_df,'e',candidate_name)

if __name__ == "__main__":
    main()