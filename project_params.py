DEFAULT_CANDIDATE_DATA = [
    # ('M-WILKINSON','H4CA49164','C00848168'),    # M. Wilkinson
    ('S-LEE','H6NV04020','C00655613'),    # S. Lee
    ('B-WILLIAMS','H2NY22212','C00806307'),    # B. Williams
    ('M-DE-LA-CRUZ','H0TX15124','C00765719'),    # M. De La Cruz
    ('K-KILEY','H2CA03157','C00801985'),    # K. Kiley
    ('P-JUNGE','H0MI08141','C00726687'),    # P. Junge
] #default (candidate, committee) ids

SCHEDULE_KEY_DICT = {
    'a': {
        'party_key':'contributor_name', 
        'payment_key':'contribution_receipt_amount', 
        'date_key':'contribution_receipt_date',
    },
    'b': {
        'party_key':'recipient_name',
        'payment_key':'disbursement_amount',
        'date_key':'disbursement_date',
    },
    'e': {
        'party_key':'committee', 
        'payment_key':'expenditure_amount', 
        'date_key':'expenditure_date',
    },
}

OPEN_FEC_API_URL_ROOT = 'https://api.open.fec.gov/v1/'
RECEIPT_API_URL_ROOT = OPEN_FEC_API_URL_ROOT + 'schedules/schedule_a/?'
DISBURSEMENT_API_URL_ROOT = OPEN_FEC_API_URL_ROOT + 'schedules/schedule_b/?'
IND_EXP_API_URL_ROOT = OPEN_FEC_API_URL_ROOT + 'schedules/schedule_e/?'

GDRIVE_SCH_A_SHEET_NAME = 'schedule_a'
GDRIVE_SCH_B_SHEET_NAME = 'schedule_b'
GDRIVE_SCH_E_SHEET_NAME = 'schedule_e'