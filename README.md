# Portfolio Analyzer

A simple tool for analyzing profitability of a portfolio of solar systems.  

# Setup

The portfolio analyzer only requires two libraries: 
* numpy -- a library with several useful mathemetical and financial functions
* leather -- a library for producing simple charts

Make sure you've installed both (via `pip install numpy leather`) before running the script

The portfolio analyzer has been tested with python 2.7.9 and 2.7.13, but may not be compatible python 3

# Running the script

The script has several input arguments:
 * `--csv-file` - required. This is the supplied path to the csv file containing the portfolio you want to analyze
 * `--az-ppa-rate-override-` - optional. This oprtional float input will override the database value ppa rate for Arizona
 * `--ca-ppa-rate-override-` - optional. This oprtional float input will override the database value ppa rate for California
 * `--ny-ppa-rate-override-` - optional. This oprtional float input will override the database value ppa rate for New York
 * `--nj-ppa-rate-override-` - optional. This oprtional float input will override the database value ppa rate for New Jersey

 a sample command: `python analyze_portfolio.py --csv-file=~/files/portfolio_data/portfolio.csv`

 # Output

 The script will output npv, pv and cost for each state, as well as for the portfolio as a whole. It will also create .svg files to aid in the visualization of those values. Examples can be found in the Sample Output folder.

