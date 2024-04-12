import os
import pandas as pd

from glob import glob
from tqdm import tqdm

from clean_fec_csv_columns import get_csv_file_list

def remove_dup_entries(csv_file):
    df = pd.read_csv(csv_file,low_memory=False,index_col=0)
    print(f'Original length: {len(df)}')
    df = df.drop_duplicates()
    print(f'New length: {len(df)}')
    df.to_csv(csv_file)

def main():
    csv_file_list = get_csv_file_list('./data')
    for csv_file in tqdm(csv_file_list):
        print(csv_file)
        remove_dup_entries(csv_file)

if __name__ == "__main__":
    main()