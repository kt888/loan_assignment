import csv
import pandas
import operator
from collections import defaultdict


class Facility:
    def __init__(self, facility_id, bank_id, interest_rate, amount):
        self.id = facility_id
        self.bank_id = bank_id
        self.interest_rate = interest_rate
        self.amount = amount
        self.covenants = []
        self.total_yield = 0.0
        self.total_amount_charged = 0.0  # Total amount Affirm has charged facility

    def update(self, loan):
        self.amount -= loan.amount
        self.total_amount_charged += loan.amount * self.interest_rate

    def can_process_loan(self, loan):
        if self.amount < loan.amount:
            return False
        if all(self.satisfy(loan, covenant) for covenant in self.covenants):
            return True
        return False

    def satisfy(self, loan, covenant):
        if any(constraint.opt(
                getattr(loan, constraint.variable), constraint.value)
                for constraint in covenant.constraints):
            return False
        """
        if loan.default_likelihood > covenant.max_default_likelihood:
            return False
        if loan.state == covenant.banned_state:
            return False
        """
        return True

    def update_yield(self, loan_yield):
        self.total_yield += loan_yield


class Covenant:
    def __init__(self, facility_id, bank_id):
        self.facility_id = facility_id if facility_id else None
        self.bank_id = bank_id
        self.constraints = []

    def add_constraint(self, constraint):
        self.constraints.append(constraint)


class Constraint:
    def __init__(self, variable, opt, value):
        self.variable = variable
        self.opt = opt
        self.value = value


class Loan:
    def __init__(self, loan_id, amount, interest_rate, default_likelihood, state):
        self.id = loan_id
        self.amount = amount
        self.interest_rate = interest_rate
        self.default_likelihood = default_likelihood
        self.state = state
        self.assignment = None

    def process(self, facilities):
        candidates = {}
        for f_id, facility in facilities.items():
            if facility.can_process_loan(self):
                candidates[f_id] = self.amount * facility.interest_rate + \
                    facility.total_amount_charged
        if not candidates:
            return
        selected_facility = min(candidates, key=candidates.get)
        facilities[selected_facility].update(self)
        self.assignment = selected_facility
        loan_yield = self.compute_yield(facilities[selected_facility])
        facilities[selected_facility].update_yield(loan_yield)

    def compute_yield(self, facility):
        return (1 - self.default_likelihood) * self.interest_rate * self.amount \
                - self.default_likelihood * self.amount \
                - facility.interest_rate * self.amount


def match_facilities_and_covenants(facilities, banks, covenant_data):
    for covenant in covenant_data:
        if covenant.facility_id:
            facilities[covenant.facility_id].covenants.append(covenant)
        else:
            for fac_id in banks[covenant.bank_id]:
                facilities[fac_id].covenants.append(covenant)


def load_facilities():
    facility_dict = defaultdict(Facility)
    bank_dict = defaultdict(list)
    facilities_data = pandas.read_csv('facilities.csv')
    for _, facility in facilities_data.iterrows():
        facility_dict[int(facility['id'])] = Facility(
            int(facility['id']), 
            facility['bank_id'], 
            facility['interest_rate'], 
            facility['amount'])
        bank_dict[facility['bank_id']].append(facility['id'])
    return facility_dict, bank_dict


def load_covenants():
    covenants = []
    covenants_data = pandas.read_csv('covenants.csv')
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


def process_loans(facilities):
    loan_data = pandas.read_csv('loans.csv')
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


if __name__ == '__main__':
    facilities, banks = load_facilities()
    covenant_data = load_covenants()
    match_facilities_and_covenants(facilities, banks, covenant_data)
    process_loans(facilities)
    write_yields_csv(facilities)
