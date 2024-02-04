DEFAULT_CANDIDATE_DATA = [
    ('H4CA49164','C00848168'),    # M. Wilkinson
    ('H6NV04020','C00655613'),    # S. Lee
    ('H2NY22212','C00806307'),    # B. Williams
    ('H0TX15124','C00765719'),    # M. De La Cruz
    ('H2CA03157','C00801985'),    # K. Kiley
    ('H0MI08141','C00726687'),    # P. Junge
] #default (candidate, committee) ids

OPEN_FEC_API_URL_ROOT = 'https://api.open.fec.gov/v1/'
RECEIPT_API_URL_ROOT = OPEN_FEC_API_URL_ROOT + 'schedules/schedule_a/?'
DISBURSEMENT_API_URL_ROOT = OPEN_FEC_API_URL_ROOT + 'schedules/schedule_b/?'
IND_EXP_API_URL_ROOT = OPEN_FEC_API_URL_ROOT + 'schedules/schedule_e/?'