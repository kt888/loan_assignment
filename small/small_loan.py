import pandas
import csv


def load_data():
    loans = pandas.read_csv('loans.csv')
    #banks = pandas.read_csv('banks.csv')
    print(loans)
    covenants = pandas.read_csv('covenants.csv')
    facilities = pandas.read_csv('facilities.csv')
    fac_cov = pandas.merge(facilities, covenants, on='facility_id', how='inner')
    fac_cov['amount_charged'] = 0
    facilities['expected_yield'] = 0
    with open('assignments_2.csv', 'w') as csvfile:
        fieldnames = ['loan_id', 'facility_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for index, loan in loans.iterrows():
            cheapest_facility = get_cheapest_facilitiy_for_loan(loan, fac_cov)
            if cheapest_facility:
                fac_cov.loc[fac_cov['facility_id'] == cheapest_facility[0], 'amount'] = fac_cov['amount']-loan['amount']
                fac_cov.loc[fac_cov['facility_id'] == cheapest_facility[0], 'amount_charged'] = fac_cov['amount_charged']+loan['amount']*fac_cov['interest_rate']
                writer.writerow({'loan_id': loan['id'], 'facility_id': cheapest_facility[0]})
                calculate_yield(loan, facilities, cheapest_facility[0], cheapest_facility[3])
    write_yields_csv(facilities)


def calculate_yield(loan, facilities, facility_id, fac_interest):
    yeild_for_loan = (1-loan['default_likelihood']) * \
        loan['interest_rate'] * loan['amount'] - \
        loan['default_likelihood']*loan['amount'] - \
        loan['amount'] * fac_interest
    facilities.loc[
        facilities['facility_id'] == facility_id, 
        'expected_yield'] = round(facilities['expected_yield'] + yeild_for_loan)


def get_cheapest_facilitiy_for_loan(loan, fac_cov_df):
    posible_facilities = []
    for index, row in fac_cov_df.iterrows():
        if loan['amount'] <= row['amount'] and \
            loan['state'] != row['banned_state'] and \
                loan['default_likelihood'] <= row['max_default_likelihood']:
            amount_charged = loan['amount'] * row['interest_rate'] + row['amount_charged']
            posible_facilities.append((row['facility_id'], amount_charged, row['amount'], row['interest_rate']))
    if len(posible_facilities) > 0 and posible_facilities != []:
        print(posible_facilities)
        return min(posible_facilities, key=lambda x: x[1])


def write_yields_csv(facilities):
    header = ['facility_id', 'expected_yield']
    facilities.to_csv('yields_2.csv', columns = header, index=False)


if __name__ == "__main__":
    load_data()