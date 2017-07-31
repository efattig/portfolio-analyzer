__author__ = 'efattig'
import numpy

class System(object):
    """
    An object to represent a single system in the portfolio
    """

    def __init__(self, size, first_year_production, state_information):
        """Constructor"""
        self.size = size
        self.first_year_production = first_year_production
        self.state_information = state_information
        if self.size > 100 or self.size < 0.5:
            raise Exception('System size of {} is outside expected range. '
                            'Please verify input csv lists size in kilowatts'.format(self.size))

        self.degradation_rate = 0 # hardcoding per the assignment instructions
        self.escalator = 0.029 # hardcoding per the assignment instructions
        self.term = 20 # hardcoding per the assignment instructions
        self.calculate_financials()

    def calculate_financials(self):
        """
        Calculate solar production, costs, payments, and incentives for the system over the term.
        Stores those values in instance variables
        """
        term_years = range(self.term)
        annual_production = [self.first_year_production * ((1 - self.degradation_rate) ** year) for year in term_years]
        payment_rates = [self.state_information['per_kwh_rates'] * (1 + self.escalator) ** year for year in term_years]
        annual_payments = [annual_production[year] * payment_rates[year] for year in term_years]
        annual_maintenance_cost = [
            self.size * self.state_information['maintenance_costs'] * (1 + self.state_information['maintenance_cost_inflation']) ** year
            for year
            in term_years
        ]
        annual_payment_stream = numpy.subtract(annual_payments, annual_maintenance_cost)

        self.upfront_cost = self.size * self.state_information['per_kw_cost'] + self.state_information['per_system_cost']
        self.upfront_incentive = self.size * self.state_information['incentives']
        self.monthly_payment_stream = self.convert_annual_to_monthly(annual_payment_stream)
        self.monthly_payment_stream[0] += self.upfront_incentive

    def convert_annual_to_monthly(self, cash_stream):
        """
        converts a stream of annual total payment values into a stream of monthly payments
        :param list cash_stream: a list of annual payments
        :return monthly_cash_stream: a list of monthly payments
        :rtype list
        """
        monthly_cash_stream = []
        for yearly_value in cash_stream:
            monthly_cash_stream += [yearly_value / 12] * 12
        return monthly_cash_stream