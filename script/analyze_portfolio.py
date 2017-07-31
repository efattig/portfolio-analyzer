__author__ = 'efattig'
from argparse import ArgumentParser, FileType
import csv
import numpy
from leather import Chart, Grid
from system import System
from dbservice import DBService


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("--csv-file",
                        type=FileType('r'),
                        help="the csv file containing the existing portfolio",
                        required=True)
    parser.add_argument("--az-ppa-rate-override",
                        type=float,
                        help="an override for the Arizona ppa price per kwh. Database value will be ignored",
                        required=False)
    parser.add_argument("--ca-ppa-rate-override",
                        type=float,
                        help="an override for the California ppa price per kwh. Database value will be ignored",
                        required=False)
    parser.add_argument("--ny-ppa-rate-override",
                        type=float,
                        help="an override for the New York ppa price per kwh. Database value will be ignored",
                        required=False)
    parser.add_argument("--nj-ppa-rate-override",
                        type=float,
                        help="an override for the New Jersey ppa price per kwh. Database value will be ignored",
                        required=False)
    csv_file = parser.parse_args().csv_file
    overrides = {
        'AZ' : parser.parse_args().az_ppa_rate_override,
        'CA' : parser.parse_args().ca_ppa_rate_override,
        'NY' : parser.parse_args().ny_ppa_rate_override,
        'NJ' : parser.parse_args().nj_ppa_rate_override
    }
    if csv_file.name[-4:] != ".csv":
        raise Exception("Provided file: {} did not have expected file extension: .csv".format(csv_file.name))
    return (csv_file, overrides)

def main():
    csv_file, rate_overrides = get_arguments()
    reader = csv.DictReader(csv_file)
    if reader.fieldnames != ['State', 'System Size (kW)', 'Estimated Year 1 Production (kWh)']:
        raise Exception("Column names : {} did not match expected column names".format(reader.fieldnames))
    dbservice = DBService()
    discount_rate = 0.05

    # Get cost structure info from DB
    portfolio_cost = dbservice.get_portfolio_cost()
    states = dbservice.get_states()
    upfront_incentives = dbservice.get_incentives()
    costs = dbservice.get_costs()
    per_kwh_rates = dbservice.get_per_kwh_rates()
    for state, rate in per_kwh_rates.iteritems():
        if rate_overrides[state]:
            per_kwh_rates[state] = rate_overrides[state]

    # assemble state information into simple dict for each state
    state_information = {
        state : {
            'per_system_cost' : costs[state]['per_system_costs'],
            'per_kw_cost' : costs[state]['per_kw_costs'],
            'incentives' : upfront_incentives[state],
            'per_kwh_rates' : per_kwh_rates[state],
            'maintenance_costs' : costs[state]['maintenance_costs'],
            'maintenance_cost_inflation' : costs[state]['maintenance_cost_inflation']
        }
        for state
        in states
    }

    # instantiating counters
    total_state_system_size = {state : 0 for state in states}
    total_state_system_count = {state : 0 for state in states}
    total_state_costs = {state : 0 for state in states}
    total_state_cash_streams = {state : [0] * 240 for state in states}

    # Read values from the csv into System objects
    for row in reader:
        state = row['State']
        size = float(row['System Size (kW)'])
        first_year_production = float(row['Estimated Year 1 Production (kWh)'])

        total_state_system_count[state] += 1
        total_state_system_size[state] += size
        if state not in state_information.keys():
            raise Exception('No state information found in database for the following state: {}'.format(state))
        system = System(size, first_year_production, state_information[state])
        total_state_costs[state] += system.upfront_cost
        total_state_cash_streams[state] = numpy.add(total_state_cash_streams[state],system.monthly_payment_stream)

    systems_in_portfolio = reduce((lambda x, y: x+y), total_state_system_count.values())

    # distribute the portfolio cost among the states proportional to the number of systems in that state
    for state in states:
        total_state_costs[state] += portfolio_cost * total_state_system_count[state] / systems_in_portfolio

    # get portfolio level values
    total_cash_stream = reduce((lambda x, y: numpy.add(x,y)), total_state_cash_streams.values())
    total_portfolio_cost = sum(total_state_costs.values())
    portfolio_npv = numpy.npv(discount_rate/12, [-total_portfolio_cost] + total_cash_stream.tolist())
    portfolio_pv = numpy.npv(discount_rate/12, [0] + total_cash_stream.tolist())

    # calculate state values
    state_pv = {state : numpy.npv(discount_rate/12, [0] + total_state_cash_streams[state].tolist()) for state in states}
    state_npv = {
        state : numpy.npv(discount_rate/12, [-total_state_costs[state]] + total_state_cash_streams[state].tolist())
        for state
        in states
    }

    # output results
    output_portfolio_results(portfolio_npv, portfolio_pv, total_portfolio_cost)
    output_state_results("PV", states, state_pv, total_state_system_count, total_state_system_size)
    output_state_results("Cost", states, total_state_costs, total_state_system_count, total_state_system_size)
    output_state_results("NPV", states, state_npv, total_state_system_count, total_state_system_size)

def output_portfolio_results(portfolio_npv, portfolio_pv, portfolio_cost):
    """
    Outputs the results of the script calculations to stdout, and generates charts to aid with visualization
    Converts results to lists of tuples for ease of charting
    :param float portfolio_npv: the net present value of the portfolio as a whole
    :param float portfolio_pv: the present value of the portfolio as a whole
    :param float portfolio_cost: the cost of the portfolio as a whole
    """
    print (
        "NPV of the overall portfolio is {NPV:,}\n"
        "PV of the overall portfolio is {PV:,}\n"
        "The cost of the overall portfolio is {COST:,}".format(
            NPV=round(portfolio_npv,2),
            PV=round(portfolio_pv,2),
            COST=round(portfolio_cost,2)
        )
    )

    data_to_chart = [
        ("NPV", portfolio_npv),
        ("PV", portfolio_pv),
        ("Cost", portfolio_cost)
    ]
    chart = Chart('Aggregate Portfolio Values')
    chart.add_columns(data_to_chart)
    chart.to_svg('portfolio_values.svg')


def output_state_results(name, states, statistic_dict, system_count, system_size):
    """
    Outputs the results of the script calculations for each state to stdout, and
    generates charts to aid with visualization. Converts results to lists of tuples for ease of charting
    :param str name: the name of the statistic being charted
    :param list states: a list of the states to be graphed along the y axis
    :param dict statistic_dict: a dict of the statistic to be graphed for each state
    :param dict system_count: a dict of the total number of systems in each state
    :param dict system_size: a dict of the total size of the systems in kW STC in each state
    """
    total_by_state = [
        (state , statistic_dict[state])
        for state
        in states
    ]
    per_watt_by_state = [
        (total[0], total[1] / system_size[total[0]] / 1000)
        for total
        in total_by_state
    ]
    per_system_by_state = [
        (total[0], total[1] / system_count[total[0]])
        for total
        in total_by_state
    ]

    for value in per_watt_by_state:
        print ("{NAME} per watt in {STATE} is {VALUE}".format(NAME=name, STATE=value[0], VALUE=round(value[1],2)))
    chart1 = Chart('Total {} by state'.format(name))
    chart1.add_columns(total_by_state)

    chart2 = Chart('{} per watt by state'.format(name))
    chart2.add_columns(per_watt_by_state)

    chart3 = Chart('{} per system by state'.format(name))
    chart3.add_columns(per_system_by_state)

    grid = Grid()
    grid.add_one(chart1)
    grid.add_one(chart2)
    grid.add_one(chart3)
    grid.to_svg('{}_by_state.svg'.format(name))


if __name__ == '__main__':
    main()