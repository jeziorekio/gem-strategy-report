import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import resend

# Initialize Resend API
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Configuration
TICKERS = {
    'SPY': 'S&P 500 (USA)',
    'VXUS': 'World ex-US',
    'BND': 'Bonds'
}

MOMENTUM_PERIOD = 252  # 12-month trading days

class GEMStrategy:
    def __init__(self):
        self.results = {}
        self.signal = None
        self.is_rebalance_date = False
        
    def fetch_historical_data(self, ticker, period_days=252):
        """Fetch historical price data from yfinance"""
        try:
            data = yf.download(ticker, period=f'{period_days + 30}d', progress=False)
            return data['Adj Close']
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_momentum(self, ticker):
        """Calculate 12-month momentum (252 trading days)"""
        try:
            prices = self.fetch_historical_data(ticker, MOMENTUM_PERIOD)
            if prices is None or len(prices) < MOMENTUM_PERIOD:
                return None
            
            # Calculate 252-day return
            momentum = ((prices.iloc[-1] - prices.iloc[-MOMENTUM_PERIOD]) / prices.iloc[-MOMENTUM_PERIOD]) * 100
            return momentum
        except Exception as e:
            print(f"Error calculating momentum for {ticker}: {e}")
            return None
    
    def check_month_end_proximity(self, days_threshold=3):
        """Check if today is near the end of month for rebalancing alerts"""
        today = datetime.now()
        next_month = today + relativedelta(months=1)
        month_end = next_month.replace(day=1) - timedelta(days=1)
        
        days_until_month_end = (month_end - today).days
        
        if days_until_month_end <= days_threshold and days_until_month_end >= 0:
            self.is_rebalance_date = True
            return True
        return False
    
    def generate_signal(self):
        """GEM Strategy Logic - Compare momentum and select asset"""
        self.results = {}
        
        for ticker in TICKERS.keys():
            momentum = self.calculate_momentum(ticker)
            self.results[ticker] = momentum
        
        spy_momentum = self.results.get('SPY')
        vxus_momentum = self.results.get('VXUS')
        bnd_momentum = self.results.get('BND')
        
        if None in [spy_momentum, vxus_momentum, bnd_momentum]:
            print("Error: Could not calculate all momentum values")
            return None
        
        if (spy_momentum > bnd_momentum and spy_momentum > 0) or (vxus_momentum > bnd_momentum and vxus_momentum > 0):
            if spy_momentum >= vxus_momentum:
                self.signal = 'SPY'
            else:
                self.signal = 'VXUS'
        else:
            self.signal = 'BND'
        
        return self.signal
    
    def format_report(self):
        """Format momentum report for email"""
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        report = f"""
GEM STRATEGY MOMENTUM REPORT
Generated: {today}

MOMENTUM VALUES (12-Month Return):
{'='*50}
SPY (S&P 500):     {self.results['SPY']:>7.2f}%
VXUS (World ex-US): {self.results['VXUS']:>7.2f}%
BND (Bonds):       {self.results['BND']:>7.2f}%

CURRENT SIGNAL: {self.signal}
{'='*50}

ANALYSIS:
- SPY > BND:  {self.results['SPY'] > self.results['BND']}
- VXUS > BND: {self.results['VXUS'] > self.results['BND']}
- Selected Asset: {TICKERS[self.signal]}
"""
        return report
    
    def format_rebalance_alert(self):
        """Format rebalance alert with DECYZJA HANDLOWA warning"""
        report = self.format_report()
        rebalance_report = f"""
🔴 REBALANS - DECYZJA HANDLOWA 🔴
{'='*60}
{report}
{'='*60}

ACTION REQUIRED: Review allocation and execute rebalancing if necessary.
"""
        return rebalance_report
    
    def send_email(self, subject, body, is_rebalance=False):
        """Send report via Resend email service"""
        if not RESEND_API_KEY:
            print("Warning: RESEND_API_KEY not set. Skipping email.")
            print(f"Report:\n{body}")
            return
        
        try:
            recipient_email = os.environ.get('GEM_REPORT_EMAIL', 'default@example.com')
            params = {
                "from": "GEM Strategy <onboarding@resend.dev>",
                "to": recipient_email,
                "subject": subject,
                "html": f"<pre>{body}</pre>"
            }
            
            email = resend.Emails.send(params)
            print(f"Email sent successfully to {recipient_email}")
            return email
        except Exception as e:
            print(f"Error sending email: {e}")
            return None
    
    def run(self):
        """Execute full GEM strategy workflow"""
        print("Starting GEM Strategy execution...")
        
        signal = self.generate_signal()
        if signal is None:
            print("Error: Could not generate signal")
            return False
        
        is_month_end = self.check_month_end_proximity(days_threshold=3)
        
        if is_month_end:
            subject = "🔴 REBALANS - DECYZJA HANDLOWA - GEM Strategy Report"
            body = self.format_rebalance_alert()
            self.send_email(subject, body, is_rebalance=True)
            print("Rebalance alert sent!")
        else:
            subject = f"GEM Strategy Weekly Report - {datetime.now().strftime('%Y-%m-%d')}"
            body = self.format_report()
            self.send_email(subject, body, is_rebalance=False)
            print("Weekly report sent!")
        
        return True

if __name__ == '__main__':
    gem = GEMStrategy()
    success = gem.run()
    exit(0 if success else 1)