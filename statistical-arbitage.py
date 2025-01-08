import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# Step 1: Data Collection and Preprocessing (example using random data)
# In real use cases, replace this with actual data loading.
# Example data: Date, Asset A (Price_A), Asset B (Price_B)
dates = pd.date_range(start='2020-01-01', periods=500, freq='D')
np.random.seed(42)
Price_A = np.cumsum(np.random.randn(500)) + 100  # Simulating a random walk
Price_B = np.cumsum(np.random.randn(500)) + 100  # Another random walk, with some correlation

df = pd.DataFrame({'Date': dates, 'Price_A': Price_A, 'Price_B': Price_B})
df.set_index('Date', inplace=True)

# Step 2: Cointegration Test
score, p_value, _ = coint(df['Price_A'], df['Price_B'])
print(f'Cointegration Test p-value: {p_value}')
if p_value < 0.05:
    print("The assets are cointegrated and suitable for Stat Arb.")

# Step 3: Model the Spread (using Linear Regression)
X = sm.add_constant(df['Price_B'])  # Add constant term for the regression
model = sm.OLS(df['Price_A'], X).fit()
df['spread'] = df['Price_A'] - model.predict(X)  # Spread = Actual Price_A - Predicted Price_A

# Step 4: Calculate mean and standard deviation of the spread
spread_mean = df['spread'].mean()
spread_std = df['spread'].std()

print(f'Spread Mean: {spread_mean}')
print(f'Spread Std Dev: {spread_std}')

# Step 5: Entry and Exit Signals
entry_threshold = spread_mean + 2 * spread_std  # Entry when spread > mean + 2 * std
exit_threshold = spread_mean  # Exit when spread reverts to the mean

# Step 6: Backtesting the Strategy
initial_cash = 100000  # Starting capital
portfolio_value = initial_cash
position_A = 0  # Position in Asset A
position_B = 0  # Position in Asset B

# Track the portfolio value over time for plotting
portfolio_values = []
entry_points = []
exit_points = []

# Loop through the data and simulate trades based on signals
for i in range(len(df)):
    # Generate signals based on spread
    if df['spread'][i] > entry_threshold:
        # Short Asset A and Long Asset B
        if position_A == 0 and position_B == 0:
            position_A = -1
            position_B = 1
            entry_points.append(df.index[i])
    elif df['spread'][i] < -entry_threshold:
        # Long Asset A and Short Asset B
        if position_A == 0 and position_B == 0:
            position_A = 1
            position_B = -1
            entry_points.append(df.index[i])
    elif df['spread'][i] < exit_threshold and (position_A != 0 or position_B != 0):
        # Exit positions (spread reverts to the mean)
        if position_A != 0 or position_B != 0:
            position_A = 0
            position_B = 0
            exit_points.append(df.index[i])

    # Calculate portfolio value based on positions and asset prices
    portfolio_value += (position_A * df['Price_A'][i] + position_B * df['Price_B'][i])
    portfolio_values.append(portfolio_value)

# Step 7: Results
final_portfolio_value = portfolio_value
print(f'Final Portfolio Value: {final_portfolio_value}')

# Step 8: Plotting Portfolio Performance
plt.figure(figsize=(10, 6))
plt.plot(df.index, portfolio_values, label='Portfolio Value')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.legend()
plt.show()

# Optional: Plot the spread and entry/exit thresholds
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['spread'], label='Spread')
plt.axhline(spread_mean, color='black', linestyle='--', label='Mean')
plt.axhline(entry_threshold, color='red', linestyle='--', label='Entry Threshold (+2 Std Dev)')
plt.axhline(-entry_threshold, color='blue', linestyle='--', label='Entry Threshold (-2 Std Dev)')
plt.axhline(exit_threshold, color='green', linestyle='--', label='Exit Threshold')
plt.scatter(entry_points, df['spread'][df.index.isin(entry_points)], color='red', label='Entry Points', zorder=5)
plt.scatter(exit_points, df['spread'][df.index.isin(exit_points)], color='green', label='Exit Points', zorder=5)
plt.title('Spread with Entry and Exit Thresholds')
plt.xlabel('Date')
plt.ylabel('Spread')
plt.legend()
plt.show()
