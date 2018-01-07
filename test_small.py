import pandas


def test_assignments():
    given_assignment = pandas.read_csv('small/given_assignment.csv')
    gen_assignment = pandas.read_csv('small/assignments.csv')
    given_assignment[given_assignment.loan_id ==2].values == gen_assignment [gen_assignment .loan_id ==2].values
    given_assignment[given_assignment.loan_id ==1].values == gen_assignment [gen_assignment .loan_id ==1].values


def test_yields():
    given_yield = pandas.read_csv('small/given_yields.csv')
    gen_yield = pandas.read_csv('small/yields.csv')
    given_yield[given_yield.facility_id ==2].values == gen_yield[gen_yield.facility_id ==2].values
    given_yield[given_yield.facility_id ==1].values == gen_yield[gen_yield.facility_id ==1].values


