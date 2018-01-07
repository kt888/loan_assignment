from loan_facility_matching import *


facilities, banks = load_facilities('test_data/test_facilities.csv')
covenants = load_covenants('test_data/test_covenants.csv')

match_facilities_and_covenants(facilities, banks, covenants)


def test_covenant_facilties_matching():
    # test if a covenant with empty facility id has been matched
    assert len(facilities[5].covenants) > 0
    assert len(facilities[1].covenants) == 2
    assert len(facilities[2].covenants) == 1


