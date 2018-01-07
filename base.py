

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
        """
        If optimization is chosen instead of just selecting
        the cheapest facility, the total amount charged by facility is
        updated. The facility that gives the minimum total
        amount charged is selected
        Arguments:
            loan {[type]} -- [description]
        """
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

    def process(self, facilities, optimization=False):
        """
        Possible candidates are selected based on a condition (cheapest loan
        or any other optimization)
        Arguments:
            facilities
        
        Keyword Arguments:
            optimization {bool} -- (default: {False})
        """
        candidates = {}
        for f_id, facility in facilities.items():
            if facility.can_process_loan(self):
                if optimization:
                    candidates[f_id] = self.amount * facility.interest_rate + \
                        facility.total_amount_charged
                else:
                    candidates[f_id] = self.amount * facility.interest_rate
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
