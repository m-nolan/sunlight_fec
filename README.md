# Sunlight FEC Analysis - Committee Receipt Merge
Michael Nolan
Sunlight Search
2024-01-12

## Overview
Script and tooling to access and compare contributions to and payouts from different U.S. political campaigns. Data accessed from the Federal Election Commission's openFEC data access API: https://api.open.fec.gov/developers/

## Dependencies
- pandas
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
To run the data download script, navigate to the directory of your local clone of the repository and run the following from the command line:
```
python ./open_fec_scraper.py
```
This will run the script to download and save as a local CSV file all campaign receipts filed by a default set of candidate election committees.

To get receipt data from a different set of committees, run the following:
```
python ./open_fec_scraper.py -c <COMMITTEE_ID_1> <COMMITTEE_ID_2> <COMMITTEE_ID_3> ...
```
Candidate committees can be found using the OpenFEC portal here: https://www.fec.gov/data/

## License
TK TK
