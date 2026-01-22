import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class GEMStrategy:
    def __init__(self):
        self.notifications = []

    def execute_strategy(self):
        # Code for GEM strategy execution
        self.send_notification("GEM Strategy executed successfully.")

    def send_notification(self, message):
        self.notifications.append(message)
        self.send_email(message)

    def send_email(self, message):
        # Setup your email configuration
        sender_email = "your_email@example.com"
        receiver_email = "receiver_email@example.com"
        msg = MIMEText(message)
        msg['Subject'] = 'GEM Strategy Notification'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender_email, 'your_password')
            server.sendmail(sender_email, receiver_email, msg.as_string())

if __name__ == '__main__':
    gem_strategy = GEMStrategy()
    gem_strategy.execute_strategy()