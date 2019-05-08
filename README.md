# AIT Trading Algorithms

Alpha Factors and Trading Algorithms on [Quantopian](https://www.quantopian.com/) created by Philip Kiely, Richard Greenbaum, Rudolph Hernandez, and Alex Foster for our Data Mining final project.

For our project, we each created an Alpha Factor from data available on Quantopian. We then created one trading algorithm per alpha factor and one algorithm that combines all of the factors.

## Alpha Factors

An Alpha Factor is the engine in a long-short trading algorithm. These factors rank stocks in the QTradableStocksUS universe so that we can long the top picks and short the bottom ones.

- Simple Moving Average Crossover

  - The negative absolute value of the 10-day moving average premium over previous closing price.
  - Uses pricing data (LINK)

- Twitter Sentiment Momentum

  - Info
  - Data

- Freshness Weighted EPS Growth

  - Info
  - Data

- Composite Fundamentals

  - Info
  - Data

All alpha factors were evaluated using [Alphalens](https://www.quantopian.com/posts/alphalens-a-new-tool-for-analyzing-alpha-factors) and built in the [Quantopian research environment](https://www.quantopian.com/research).

## Algorithms

These algorithms put our pipelines into the standard architecture of a Quantopian trading algorithm to let us backtest the returns in the training and test period.
