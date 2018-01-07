import csv
import pandas
import argparse
import operator
from base import Loan, Facility, Constraint, Covenant
from collections import defaultdict


def match_facilities_and_covenants(facilities, banks, covenant_data):
    for covenant in covenant_data:
        if covenant.facility_id:
            facilities[covenant.facility_id].covenants.append(covenant)
        else:
            for fac_id in banks[covenant.bank_id]:
                facilities[fac_id].covenants.append(covenant)


def load_facilities(path_to_facilities):
    facility_dict = defaultdict(Facility)
    bank_dict = defaultdict(list)
    facilities_data = pandas.read_csv(path_to_facilities)
    for _, facility in facilities_data.iterrows():
        facility_dict[int(facility['id'])] = Facility(
            int(facility['id']), 
            facility['bank_id'], 
            facility['interest_rate'], 
            facility['amount'])
        bank_dict[facility['bank_id']].append(facility['id'])
    return facility_dict, bank_dict


def load_covenants(path_to_covenants):
    covenants = []
    covenants_data = pandas.read_csv(path_to_covenants)
    for _, covenant in covenants_data.iterrows():
        cov = Covenant(covenant['facility_id'], covenant['bank_id'])
        cov.add_constraint(
            Constraint('default_likelihood', operator.gt, covenant['max_default_likelihood'])
        )
        cov.add_constraint(
            Constraint('state', operator.eq, covenant['banned_state'])
        )
        covenants.append(cov)
    return covenants


def process_loans(facilities, path_to_loans):
    loan_data = pandas.read_csv(path_to_loans)
    with open('assignments.csv', 'w') as csvfile:
        fieldnames = ['loan_id', 'facility_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for _, loan in loan_data.iterrows():
            l = Loan(loan['id'], loan['amount'], loan['interest_rate'],
                     loan['default_likelihood'], loan['state'])
            l.process(facilities)
            writer.writerow({'loan_id': l.id, 'facility_id': l.assignment})


def write_yields_csv(facilities):
    with open('yields.csv', 'w') as csvfile:
        fieldnames = ['facility_id', 'expected_yield']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for facilitity_id, facility in facilities.items():
            writer.writerow({'facility_id': facilitity_id, 'expected_yield': facility.total_yield})


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loans', help='path to loans.csv')
    parser.add_argument('--covenants', help='path to covenants.csv')
    parser.add_argument('--facilities', help='path to facilities.csv')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    facilities, banks = load_facilities(args.facilities)
    covenant_data = load_covenants(args.covenants)
    match_facilities_and_covenants(facilities, banks, covenant_data)
    process_loans(facilities, args.loans)
    write_yields_csv(facilities)
