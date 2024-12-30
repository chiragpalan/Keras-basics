
import yfinance as yf
import sqlite3
from datetime import datetime
import time
import pytz

# Database setup
DATABASE_PATH = "database/stocks_data.db"
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    stock_symbol TEXT,
    datetime TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    PRIMARY KEY (stock_symbol, datetime)
)
""")
conn.commit()

# Fetch Nifty50 stock data
def fetch_stock_data():
    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFC.NS"]  # Add all Nifty50 stocks here
    for symbol in symbols:
        data = yf.download(symbol, interval="5m", period="1d", progress=False)
        if not data.empty:
            for index, row in data.iterrows():
                try:
                    cursor.execute("""
                    INSERT OR IGNORE INTO stock_data (stock_symbol, datetime, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (symbol, index.isoformat(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
                except Exception as e:
                    print(f"Error inserting data for {symbol}: {e}")
    conn.commit()

if __name__ == "__main__":
    # Timezone setup
    ist = pytz.timezone("Asia/Kolkata")
    start_time = ist.localize(datetime.strptime("09:15", "%H:%M"))
    end_time = ist.localize(datetime.strptime("15:30", "%H:%M"))
    
    # Check if current time is within trading hours
    while True:
        now = datetime.now(ist)
        if start_time.time() <= now.time() <= end_time.time():
            fetch_stock_data()
            print(f"Data fetched at {now}")
        else:
            print("Market closed.")
        time.sleep(900)  # Wait for 15 minutes
