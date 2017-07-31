__author__='efattig'

class DBService(object):
    """
    mock db service to represent stored values. In the real world, these values shouldn't be stored in code.
    Instead, they should be taken from the source of truth via database query or api call.
    Source of truth in this case is a docx file, which is why a mock database is used instead.
    """

    def get_portfolio_cost(self):
        """
        Mocks a call to the database to fetch the portfolio level cost
        :return portfolio_cost : the portfolio level cost
        :rtype int
        """
        portfolio_cost = 500000
        return portfolio_cost

    def get_states(self):
        """
        Mocks a call to the database to fetch the active states
        :return states : a list of valid states
        :rtype list
        """
        states = ['AZ', 'CA', 'NY', 'NJ']
        return states

    def get_incentives(self):
        """
        Mocks a call to the database to fetch the state level upfront incentives
        :return incentives : the upfront incentives for each state
        :rtype dict
        """
        incentives = {
            'AZ' : 1250,
            'CA' : 1750,
            'NY' : 1500,
            'NJ' : 1250,
        }
        return incentives

    def get_per_kwh_rates(self):
        """
        Mocks a call to the database to fetch the price per kwh for each state
        :return per_kwh_rates : the price per kwh for each state
        :rtype dict
        """
        per_kwh_rates = {
            'AZ' : 0.10,
            'CA' : 0.15,
            'NY' : 0.14,
            'NJ' : 0.12
        }
        return per_kwh_rates

    def get_costs(self):
        """
        Mocks a call to the database to fetch the cost breakdown for each state
        :return costs : the cost structure
        :rtype dict
        """
        costs = {
            'AZ' : {
                'per_system_costs'           : 2500,
                'per_kw_costs'               : 2250,
                'maintenance_costs'          : 10,
                'maintenance_cost_inflation' : 0.015
            },
            'CA' : {
                'per_system_costs'           : 2500,
                'per_kw_costs'               : 2750,
                'maintenance_costs'          : 10,
                'maintenance_cost_inflation' : 0.015
            },
            'NY' : {
                'per_system_costs'           : 2500,
                'per_kw_costs'               : 2500,
                'maintenance_costs'          : 10,
                'maintenance_cost_inflation' : 0.015
            },
            'NJ' : {
                'per_system_costs'           : 2500,
                'per_kw_costs'               : 2500,
                'maintenance_costs'          : 10,
                'maintenance_cost_inflation' : 0.015
            }
        }
        return costs