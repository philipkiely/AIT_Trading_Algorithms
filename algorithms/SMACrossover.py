"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
import quantopian.algorithm as algo
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.factors import SimpleMovingAverage
import quantopian.optimize as opt


def sma(n):
    return SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=n, mask=QTradableStocksUS())

def percent_change(a, b):
    return (a - b) / b


def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    #constraints
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

    # Base universe set to the QTradableStocksUS
    base_universe = QTradableStocksUS()

    #yesterday's close price.
    close = USEquityPricing.close.latest
    #10 day simple moving average
    sma_10 = sma(10)
    #actual factor
    sma_10_close = -percent_change(sma_10, close).abs()
    
    pipe = Pipeline(
        columns={
            'sma_10_close': sma_10_close,
        },
        screen=base_universe
    )
    return pipe


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
    alpha = context.output.sma_10_close

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
