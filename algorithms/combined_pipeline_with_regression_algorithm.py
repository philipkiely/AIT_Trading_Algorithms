"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
import quantopian.algorithm as algo
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.factors import SimpleMovingAverage
from quantopian.pipeline.data.psychsignal import stocktwits
from quantopian.pipeline.data.sentdex import sentiment
import quantopian.optimize as opt
from quantopian.pipeline.data.zacks import EarningsSurprises
from quantopian.pipeline.factors import Returns
from sklearn.linear_model import LinearRegression 
import numpy as np

def sma(n):
    return SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=n, mask=QTradableStocksUS())

def percent_change(a, b):
    return (a - b) / b



def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    context.max_leverage = 1.0
    context.max_pos_size = 0.015
    context.max_turnover = 0.65
    
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

    # Record tracking variables at the end of each day.
    algo.schedule_function(
        record_vars,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

    # Create our dynamic stock selector.
    algo.attach_pipeline(make_pipeline(), 'pipeline')


def make_pipeline():
    """
    A function to create our dynamic stock selector (pipeline). Documentation
    on pipeline can be found here:
    https://www.quantopian.com/help#pipeline-title
    """
    #coefs developed in alphalens
    coefs = [3.90190147e-06, -6.36497835e-03, 8.73288426e-05]
    base_universe = QTradableStocksUS()
        
    stocktwits_score = SimpleMovingAverage(inputs=[stocktwits.bull_minus_bear],window_length=1,)
    stocktwits_cross = SimpleMovingAverage(inputs=[stocktwits.bull_minus_bear],window_length=20,)
    stocktwits_final = (stocktwits_score - stocktwits_cross).zscore()
    
    sentdex_score = SimpleMovingAverage(inputs = [sentiment.sentiment_signal], window_length = 1,)
    sentdex_cross = SimpleMovingAverage(inputs = [sentiment.sentiment_signal], window_length = 20,)
    sentdex_final = (sentdex_score - sentdex_cross).zscore()
    
    combined_score = (stocktwits_final + sentdex_final) / 2
    
    #Philip's stuff
    #yesterday's close price.
    close = USEquityPricing.close.latest
    #10 day simple moving average
    sma_10 = sma(10)
    #actual factor
    sma_10_close = -percent_change(sma_10, close).abs()
    
    return Pipeline(columns={
        'score': -(coefs[0]*combined_score + coefs[1]*EarningsSurprises.eps_pct_diff_surp.latest + coefs[2]*sma_10_close).abs()
        })


def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = algo.pipeline_output('pipeline')

    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index


def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    alpha = context.output.score.dropna()

    if not alpha.empty:
        # Create MaximizeAlpha objective
        objective = opt.MaximizeAlpha(alpha)

        # Create position size constraint
        constrain_pos_size = opt.PositionConcentration.with_equal_bounds(
            -context.max_pos_size,
            context.max_pos_size
        )

        # Constrain target portfolio's leverage
        max_leverage = opt.MaxGrossExposure(context.max_leverage)

        # Ensure long and short books
        # are roughly the same size
        dollar_neutral = opt.DollarNeutral()

        # Constrain portfolio turnover
        max_turnover = opt.MaxTurnover(context.max_turnover)

        # Rebalance portfolio using objective
        # and list of constraints
        algo.order_optimal_portfolio(
            objective=objective,
            constraints=[
                constrain_pos_size,
                max_leverage,
                dollar_neutral,
                max_turnover,
            ]
        )



def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass


def handle_data(context, data):
    """
    Called every minute.
    """
    pass
