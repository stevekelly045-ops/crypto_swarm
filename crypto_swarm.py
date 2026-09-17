import ccxt
import pandas as pd
import time
import logging
import csv
import os
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class DataScoutAgent:
    """Agent 1: Ingests market data for specified crypto pairs."""
    def __init__(self, exchange_id='binance', testnet=False):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        # Switch to Binance Testnet if enabled
        if testnet:
            self.exchange.set_sandbox_mode(True)
            logging.info("[Data Scout] 🧪 Testnet/Sandbox mode enabled.")
        
    def fetch_market_data(self, symbol='BTC/USDT', timeframe='1h', limit=100):
        try:
            bars = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logging.error(f"[Data Scout] Error fetching {symbol}: {e}")
            return None


class SpyAgent:
    """Agent 2: Fetches real-time crypto news headlines via a public API."""
    def gather_intel(self, symbol):
        base_coin = symbol.split('/')[0].lower()
        try:
            # Pulling real-time public crypto news headlines
            response = requests.get("https://cryptocurrency.cv/api/news", timeout=5)
            if response.status_code == 200:
                articles = response.json()
                # Search headlines for our target coin
                coin_mentions = [art for art in articles if base_coin in art.get('title', '').lower()]
                
                if coin_mentions:
                    logging.info(f"[Spy Agent 🕵️‍♂️] Found live news intel for {symbol.split('/')[0]}!")
                    return "BULLISH_HYPE" # Found active media coverage
            
            logging.info(f"[Spy Agent 🕵️‍♂️] No major breaking headlines for {symbol}.")
            return "NEUTRAL"
        except Exception as e:
            logging.warning(f"[Spy Agent 🕵️‍♂️] News feed offline. Defaulting to NEUTRAL. Error: {e}")
            return "NEUTRAL"


class MovingAverageAgent:
    """Agent 3: Evaluates trend direction using fast/slow Moving Averages."""
    def evaluate(self, df):
        if df is None or len(df) < 25:
            return "HOLD"
        
        df['sma_fast'] = df['close'].rolling(window=5).mean()
        df['sma_slow'] = df['close'].rolling(window=20).mean()
        
        current_fast = df['sma_fast'].iloc[-1]
        current_slow = df['sma_slow'].iloc[-1]
        prev_fast = df['sma_fast'].iloc[-2]
        prev_slow = df['sma_slow'].iloc[-2]
        
        if prev_fast <= prev_slow and current_fast > current_slow:
            return "BUY"
        elif prev_fast >= prev_slow and current_fast < current_slow:
            return "SELL"
        return "HOLD"


class RSIMomentumAgent:
    """Agent 4: Evaluates momentum using the Relative Strength Index (RSI)."""
    def evaluate(self, df):
        if df is None or len(df) < 20:
            return "HOLD"
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        current_rsi = df['rsi'].iloc[-1]
        if current_rsi < 35:
            return "BUY"
        elif current_rsi > 65:
            return "SELL"
        return "HOLD"


class RiskManagementAgent:
    """Agent 5: Safety gatekeeper monitoring volatility."""
    def assess_risk(self, signal, df):
        if df is None:
            return "HOLD"
            
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        if volatility > 0.035:
            if signal != "HOLD":
                logging.warning(f"[Risk Agent] VETO! Volatility ({volatility:.5f}) is too high. Forcing HOLD.")
                return "HOLD"
        return signal


class TradeLoggerAgent:
    """Agent 6: Records decisions into a CSV file."""
    def __init__(self, filename="trade_history.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "symbol", "signal", "price"])
                
    def log_trade(self, symbol, signal, price):
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, symbol, signal, price])


class ExecutionAgent:
    """Agent 7: Handles simulation or real testnet order execution."""
    def __init__(self, simulated=True, exchange=None):
        self.simulated = simulated
        self.exchange = exchange
        self.logger = TradeLoggerAgent()
        
    def execute_trade(self, signal, symbol, current_price):
        if self.simulated:
            logging.info(f"[Execution Agent] 🟢 [SIMULATION] {signal} order processed for {symbol} at ${current_price}")
        else:
            # LIVE TESTNET EXECUTION (Requires API Keys configured)
            try:
                if signal == "BUY":
                    order = self.exchange.create_market_buy_order(symbol, 0.001) # Example amount
                    logging.info(f"[Execution Agent] 🚀 [TESTNET LIVE] BUY Order executed: {order['id']}")
                elif signal == "SELL":
                    order = self.exchange.create_market_sell_order(symbol, 0.001)
                    logging.info(f"[Execution Agent] 📉 [TESTNET LIVE] SELL Order executed: {order['id']}")
            except Exception as e:
                logging.error(f"[Execution Agent] Order execution failed: {e}")
                
        self.logger.log_trade(symbol, signal, current_price)


class SwarmCoordinator:
    """The Orchestrator managing all agents, backtesting, and live loops."""
    def __init__(self, testnet=False):
        self.coins = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        self.scout = DataScoutAgent('binance', testnet=testnet)
        self.spy_agent = SpyAgent()
        self.ma_agent = MovingAverageAgent()
        self.rsi_agent = RSIMomentumAgent()
        self.risk_agent = RiskManagementAgent()
        self.executor = ExecutionAgent(simulated=True, exchange=self.scout.exchange)
        
    def backtest(self, symbol='BTC/USDT', days_back=30):
        """Feature 2: Backtest swarm logic over past historical data."""
        logging.info(f"=== Running Backtest for {symbol} (Past {days_back} candles) ===")
        df = self.scout.fetch_market_data(symbol, timeframe='1h', limit=days_back)
        if df is None:
            return
            
        # Simulate walking through history row by row
        for i in range(25, len(df)):
            window_df = df.iloc[:i]
            price = window_df['close'].iloc[-1]
            
            ma_vote = self.ma_agent.evaluate(window_df)
            rsi_vote = self.rsi_agent.evaluate(window_df)
            
            consensus = ma_vote if ma_vote == rsi_vote else "HOLD"
            final_signal = self.risk_agent.assess_risk(consensus, window_df)
            
            if final_signal != "HOLD":
                logging.info(f"[Backtest Result] At index {i} | Price: ${price} | Signal: {final_signal}")
        logging.info("=== Backtest Complete ===\n")

    def run_live_loop(self):
        """Feature 1 & 3: Live multi-coin loop with web-scraped spy intel."""
        logging.info("=== Starting Live Multi-Agent Swarm Loop ===")
        while True:
            for symbol in self.coins:
                logging.info(f"\n--- Analyzing Market: {symbol} ---")
                
                df = self.scout.fetch_market_data(symbol)
                if df is None:
                    continue
                current_price = df['close'].iloc[-1]
                
                spy_intel = self.spy_agent.gather_intel(symbol)
                ma_vote = self.ma_agent.evaluate(df)
                rsi_vote = self.rsi_agent.evaluate(df)
                
                if ma_vote == rsi_vote:
                    consensus = ma_vote
                else:
                    consensus = "HOLD"
                    
                if spy_intel == "BULLISH_HYPE" and consensus == "HOLD":
                    consensus = "BUY"
                
                final_signal = self.risk_agent.assess_risk(consensus, df)
                self.executor.execute_trade(final_signal, symbol, current_price)
                
            logging.info("\n=== Cycle complete. Sleeping for 60 seconds... ===\n")
            time.sleep(60)

if __name__ == "__main__":
    swarm = SwarmCoordinator(testnet=False)
    
    # 1. Comment out the backtest line using a '#'
    # swarm.backtest(symbol='BTC/USDT', days_back=50)
    
    # 2. Uncomment the live loop line by removing the '#'
    swarm.run_live_loop()