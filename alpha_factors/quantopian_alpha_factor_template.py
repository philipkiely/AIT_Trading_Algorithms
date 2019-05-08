# Pipeline (first cell)

from quantopian.pipeline import Pipeline
from quantopian.research import run_pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.factors import SimpleMovingAverage #Instead of this line, import whatever data you need


def alpha_factor_function():
    return 10

def make_pipeline():
    return Pipeline(columns={
        'column_name': alpha_factor_function()
        })


my_pipe = make_pipeline()

pipeline_data = run_pipeline(my_pipe, start_date='2014-1-1', end_date='2016-1-1').dropna()

# Alphalens (second cell)

from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.tears import create_full_tear_sheet


pricing_data = get_pricing(
  symbols=pipeline_data.index.levels[1], # Finds all assets that appear at least once in the pipeline
  start_date='2014-1-1',
  end_date='2016-2-1', #1 trading day after end date of pipeline
  fields='open_price'
)

merged_data = get_clean_factor_and_forward_returns(
  factor=pipeline_data['column_name'],
  prices=pricing_data
)

create_full_tear_sheet(merged_data)
