# Pipeline for SMA

from quantopian.pipeline import Pipeline
from quantopian.research import run_pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.factors import SimpleMovingAverage


# Create a n-day simple moving average 
def sma(n):
    return SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=n, mask=QTradableStocksUS())


# Determine the percent change between two pricing data objects
def percent_change(a, b):
    return (a - b) / b


# Create the pipeline
def make_pipeline():
    close = USEquityPricing.close.latest
    sma_10 = sma(10)
    sma_10_close = -percent_change(sma_10, close).abs()
    return Pipeline(columns={'sma_10_close': sma_10_close})


my_pipe = make_pipeline()

pipeline_data = run_pipeline(my_pipe, start_date='2014-1-1', end_date='2016-1-1').dropna()

# Alphalens for SMA (New Cell if iPython)

from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.tears import create_full_tear_sheet


pricing_data = get_pricing(
  symbols=pipeline_data.index.levels[1], # Finds all assets that appear at least once in the pipeline
  start_date='2014-1-1',
  end_date='2016-2-1', #1 trading day after end date of pipeline
  fields='open_price'
)

merged_data = get_clean_factor_and_forward_returns(
  factor=pipeline_data['sma_10_close'],
  prices=pricing_data
)

create_full_tear_sheet(merged_data)
