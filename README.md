# Sunlight FEC Analysis - Committee Receipt Merge
Michael Nolan, Sunlight Search

Created: 2024-01-12

Updated: 2024-02-03

## Overview
Script and tooling to access and compare contributions to and payouts from different U.S. political campaigns. Data accessed from the Federal Election Commission's openFEC data access API: https://api.open.fec.gov/developers/

## Dependencies
- python >= 3.6
- numpy
- pandas
- python-dotenv
- ratelimit
- requests
- tqdm

## Installation
1. Clone the repository to a local directory
2. Get an OpenFEC API key: https://api.open.fec.gov/developers/
3. Create an `.env` file at the base directory of the repository. Add the following lines:
```
# OpenFEC API key
OPENFEC_API_KEY = <your_api_key_from_step_2>
```

## Operation

### `open_fec_scraper.py` --- Download Committee Financial Disclosure Data
**Supports schedule a (receipts), b (disbursements), and e (independent expeditures) FEC data.**

To run the data download script, navigate to the directory of your local clone of the repository and run the following from the command line:
```
python ./open_fec_scraper.py
```
This will run the script to download and save as local CSV files all schedule receipts and disbursements filed by a default set of candidate election committees. You can change this default set in `project_params.py`.

Candidate committees can be found using the OpenFEC portal here: https://www.fec.gov/data/

### `fec_data_merge.py` --- Find Donor Overlap
**Supports schedule a (receipts), b (disbursements), and e (independent expeditures) FEC data.**
To run the analysis script, run the following from the command line:
```
python ./fec_data_merge.py
```
This takes each combination of the default committee data files in your `./data` directory and finds shared names between the different files.

To log data output to a markdown file (saved w/current timestamp to `./data`), run with the `-l` flag:
```
python ./fec_data_merge.py -l
```
Currenly built to print the powerset of all candidates/committees listed in `project_params.py`.

## License
Apache 2.0 http://www.apache.org/licenses/
