import yfinance as yf
import numpy as np
import requests
from datetime import datetime

# Function to fetch data from yfinance
def fetch_data(tickers):
    data = yf.download(tickers, period="1mo", interval="1d")
    return data['Close']

# Function to calculate momentum
def calculate_momentum(data, window=5):
    return data.pct_change(periods=window).iloc[window:]

# Function to generate buy/sell signals
def generate_signals(momentum):
    signals = np.where(momentum > 0, 'Buy', 'Sell')
    return signals

# Function to send notifications using Resend API
def send_notification(message):
    url = "https://api.resend.com/emails"
    payload = {
        "to": "recipient@example.com",
        "subject": "GEM Strategy Alert",
        "text": message,
    }
    requests.post(url, json=payload)

# Check if today is near the end of the month
def check_end_of_month():
    today = datetime.utcnow()
    return today.day > 25  # Or use more sophisticated logic

# Main logic
def main():
    tickers = ['AAPL', 'MSFT', 'GOOG']  # Example tickers
    data = fetch_data(tickers)
    momentum = calculate_momentum(data)
    signals = generate_signals(momentum)

    if check_end_of_month():
        send_notification("Rebalancing needed at the end of the month.")

    # Additional logic based on signals
    for ticker, signal in zip(tickers, signals):
        print(f"{ticker}: {signal}")
        send_notification(f"{ticker}: {signal}")

if __name__ == "__main__":
    main()