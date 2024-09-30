# Import required libraries
import numpy as np
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from tradingview_screener import get_all_symbols
import warnings
import pandas_ta as ta
import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore')

# Function to calculate RSI
def calculate_rsi(data, length=14):
    """
    Calculate the Relative Strength Index (RSI) for the given data.
    """
    data['RSI'] = ta.rsi(data['close'], length=length)
    return data

# Initialize the data feed
tv = TvDatafeed()

# Define the list of stocks to analyze
Hisseler = get_all_symbols(market='turkey')
Hisseler = [symbol.replace('BIST:', '') for symbol in Hisseler]
Hisseler = sorted(Hisseler)

# DataFrame to store signals
Titles = ['Hisse Adı', 'Son Fiyat', 'RSI Buy Signal']
df_signals = pd.DataFrame(columns=Titles)

# Main loop to process each stock
for hisse in Hisseler:
    try:
        # Fetch historical data
        data = tv.get_hist(symbol=hisse, exchange='BIST', interval=Interval.in_daily, n_bars=100)
        data = data.reset_index()

        # Calculate RSI
        data = calculate_rsi(data)

        # Prepare the data
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        data.set_index('datetime', inplace=True)

        # Remove rows with NaN values in RSI
        data.dropna(subset=['RSI'], inplace=True)

        # Extract the last two data points
        Signals = data.tail(2).reset_index()

        # Define the buy signal logic for RSI
        # Signal when RSI crosses above 30 (from oversold territory)
        Entry = (Signals.loc[0, 'RSI'] < 30) & (Signals.loc[1, 'RSI'] >= 30)

        # Get the last closing price
        Last_Price = Signals.loc[1, 'Close']

        # Append the results to the DataFrame
        L1 = [hisse, Last_Price, Entry]
        df_signals.loc[len(df_signals)] = L1
        print(L1)
    except Exception as e:
        print(f"Error processing {hisse}: {e}")
        pass

# Filter and display stocks with a buy signal
df_True = df_signals[df_signals['RSI Buy Signal'] == True]
print("\nStocks with RSI Buy Signal:")
print(df_True)