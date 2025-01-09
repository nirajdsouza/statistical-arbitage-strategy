import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# Step 1: Data Collection and Preprocessing
# Fetch historical data for PepsiCo (PEP) and Coca-Cola (KO)
tickers = ['KO', 'PEP']
data = yf.download(tickers, start='2015-01-01', end='2020-01-01')

# Extract 'Close' for both tickers
data = data['Close']

# Display the first few rows of the data
print(data.head())

# Step 2: Cointegration Test
# Perform the cointegration test on the two asset prices
score, p_value, _ = coint(data['KO'], data['PEP'])
print(f'Cointegration Test p-value: {p_value}')
if p_value < 0.1:
    print("The assets are cointegrated and suitable for Stat Arb.")
else:
    print("The assets are not cointegrated.")

# Step 3: Model the Spread (using Linear Regression)
X = sm.add_constant(data['PEP'])  # Add constant term for the regression
model = sm.OLS(data['KO'], X).fit()
data['spread'] = data['KO'] - model.predict(X)  # Spread = Actual Price_KO - Predicted Price_KO

# Step 4: Calculate mean and standard deviation of the spread
spread_mean = data['spread'].mean()
spread_std = data['spread'].std()

print(f'Spread Mean: {spread_mean}')
print(f'Spread Std Dev: {spread_std}')

# Step 5: Entry and Exit Signals
entry_threshold = spread_mean + 2 * spread_std  # Entry when spread > mean + 2 * std
exit_threshold = spread_mean  # Exit when spread reverts to the mean

# Step 6: Backtesting the Strategy
initial_cash = 100000  # Starting capital
portfolio_value = initial_cash
position_KO = 0  # Position in Coca-Cola
position_PEP = 0  # Position in PepsiCo

# Track the portfolio value over time for plotting
portfolio_values = []
entry_points = []
exit_points = []

# Loop through the data and simulate trades based on signals
for i in range(len(data)):
    # Generate signals based on spread
    if data['spread'][i] > entry_threshold:
        # Short Coca-Cola and Long PepsiCo
        if position_KO == 0 and position_PEP == 0:
            position_KO = -1
            position_PEP = 1
            entry_points.append(data.index[i])
    elif data['spread'][i] < -entry_threshold:
        # Long Coca-Cola and Short PepsiCo
        if position_KO == 0 and position_PEP == 0:
            position_KO = 1
            position_PEP = -1
            entry_points.append(data.index[i])
    elif data['spread'][i] < exit_threshold and (position_KO != 0 or position_PEP != 0):
        # Exit positions (spread reverts to the mean)
        if position_KO != 0 or position_PEP != 0:
            position_KO = 0
            position_PEP = 0
            exit_points.append(data.index[i])

    # Calculate portfolio value based on positions and asset prices
    portfolio_value += (position_KO * data['KO'][i] + position_PEP * data['PEP'][i])
    portfolio_values.append(portfolio_value)

# Step 7: Results
final_portfolio_value = portfolio_value
print(f'Final Portfolio Value: {final_portfolio_value}')

# Step 8: Plotting Portfolio Performance
plt.figure(figsize=(10, 6))
plt.plot(data.index, portfolio_values, label='Portfolio Value')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.legend()
plt.show()

# Optional: Plot the spread and entry/exit thresholds
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['spread'], label='Spread')
plt.axhline(spread_mean, color='black', linestyle='--', label='Mean')
plt.axhline(entry_threshold, color='red', linestyle='--', label='Entry Threshold (+2 Std Dev)')
plt.axhline(-entry_threshold, color='blue', linestyle='--', label='Entry Threshold (-2 Std Dev)')
plt.axhline(exit_threshold, color='green', linestyle='--', label='Exit Threshold')
plt.scatter(entry_points, data['spread'][data.index.isin(entry_points)], color='red', label='Entry Points', zorder=5)
plt.scatter(exit_points, data['spread'][data.index.isin(exit_points)], color='green', label='Exit Points', zorder=5)
plt.title('Spread with Entry and Exit Thresholds')
plt.xlabel('Date')
plt.ylabel('Spread')
plt.legend()
plt.show()
