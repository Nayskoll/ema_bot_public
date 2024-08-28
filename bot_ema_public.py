import os
from dotenv import load_dotenv
from binance.client import Client
import pandas as pd
import ta
from datetime import datetime
from google.oauth2 import service_account
from google.cloud import datastore
import smtplib
from email.mime.text import MIMEText
import email_config  # external variables


def connect_to_datastore():
    try:
        # Specify your GCP project
        project_id = 'bot-ema'

        # Specify the Datastore database ID
        database_id = 'bot-ema'

        # Path to the credentials file
        credentials_path = 'credentials/google_credentials.json'

        # Initialize the credentials
        credentials = service_account.Credentials.from_service_account_file(credentials_path)

        # Create the Datastore client with the specified project and database ID
        datastore_client = datastore.Client(
            project=project_id,
            credentials=credentials,
            database=database_id
        )
        print(datastore_client)
        return datastore_client

    except Exception as e:
        subject = f'Error connecting to datastore - {connect_to_datastore.__name__}'
        body = f"An error occurred while connecting to datastore:\n\n{e}"
        send_email(subject, body)
        print(body)
        return None


def send_email(subject, body):
    """Send an email."""
    sender_email = email_config.sender_email
    receiver_email = email_config.receiver_email
    password = email_config.password

    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Port for TLS

    message = MIMEText(body)
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

def initialize():
    """Initialize the Binance client."""
    try:
        # Load environment variables
        load_dotenv()

        # Proxy information
        proxy_ip = os.getenv('PROXY_IP')
        proxy_port = os.getenv('PROXY_PORT')
        proxy_username = os.getenv('PROXY_USERNAME')
        proxy_password = os.getenv('PROXY_PASSWORD')

        # Binance client configuration
        api_key = os.getenv('BINANCE_API_KEY_PA')
        api_secret = os.getenv('BINANCE_API_SECRET_PA')

        # Configure proxy with authentication
        proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}',
            'https': f'http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}',
        }

        # Instantiate the Binance client
        client = Client(api_key, api_secret, requests_params={'proxies': proxies, 'timeout': 10})

        print(f'Authentication successful: {client}')
        return client

    except Exception as e:
        subject = f'Error in trading bot - {initialize.__name__}'
        body = f"An error occurred while logging an error:\n\n{e}"
        send_email(subject, body)
        print(body)
        return None

def log_to_datastore(entity_type, data):
    """Logs data to Google Datastore and sends an email if an error occurs.

    Args:
        entity_type (str): The type of the entity to be created or updated in Datastore.
        data (dict): The data to be stored in the Datastore entity.
    """
    try:
        # Create a key for the entity
        key = datastore_client.key(entity_type)

        # Create or update the entity with the provided data
        entity = datastore.Entity(key)
        entity.update(data)

        # Store the entity in Datastore
        datastore_client.put(entity)

        print(f"Data successfully logged to Datastore for entity type '{entity_type}'.")

    except Exception as e:
        subject = f'Error logging data to Datastore - {log_to_datastore.__name__}'
        body = f"An error occurred while logging data to Datastore:\n\n{e}"
        send_email(subject, body)
        print(body)


def log_error(error_message, function_name):
    """Logs an error to Datastore and sends an email notification."""
    try:
        log_to_datastore('ErrorLog_ETHUSDT', {'timestamp': datetime.now().isoformat(), 'error': error_message, 'function': function_name})


    except Exception as e:
        # Handle errors that occur during logging or email sending
        subject = f'Error in error logging - {log_error.__name__}'
        body = f"An error occurred while logging an error:\n\n{e}"
        send_email(subject, body)
        print(body)


def log_trade(action, price, shares, balance, timestamp, stoploss, ema9, ema100, close):
    """Logs trade details to Google Datastore and sends an email if an error occurs."""
    try:
        # Create a key for the trade entity
        key = datastore_client.key('TradeLog_ETHUSDT')

        # Create a new entity
        entity = datastore.Entity(key)
        entity.update({
            'action': action,
            'price': price,
            'shares': shares,
            'balance': balance,
            'timestamp': timestamp,
            'stoploss': stoploss,
            'ema9': ema9,
            'ema100': ema100,
            'close': close
        })

        # Save the entity in Datastore
        datastore_client.put(entity)

        print(f"Trade logged successfully: Action={action}, Price={price}, Shares={shares}, Balance={balance}, Timestamp={timestamp}, Stoploss={stoploss}")

    except Exception as e:
        subject = f'Error logging trade - {log_trade.__name__}'
        body = f"An error occurred while logging trade details to Datastore:\n\n{e}"
        send_email(subject, body)
        log_error(str(e), log_trade.__name__)
        print(body)



def get_historical_data(symbol, interval, limit):
    """
    Retrieves historical price data for a given symbol and interval from the Binance API.

    Args:
        client (Binance.Client): The Binance client object.
        symbol (str): Trading symbol, e.g., 'BTCUSDT'.
        interval (str): Time interval for klines, e.g., '1h'.
        limit (int): Number of data points to retrieve.

    Returns:
        DataFrame: A pandas DataFrame containing historical price data, or None if an error occurs.
    """
    try:
        # Fetch klines from the Binance API
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit + 1)
        columns = [
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ]

        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(klines, columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Filter the DataFrame to include only relevant columns and convert types
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        # Return the DataFrame excluding the last row (limit + 1 fetched for calculation reasons)
        return df.iloc[:-1]

    except Exception as e:
        subject = f'Error logging trade on {symbol} - {get_historical_data.__name__}'
        body = f"An error occurred while retrieving historical price data:\n\n{e}"
        send_email(subject, body)
        log_error(str(e), get_historical_data.__name__)
        print(body)
        return None


def calculate_indicators(df):
    df['EMA9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['EMA100'] = df['close'].ewm(span=100, adjust=False).mean()
    df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    df['Highest_7_Close'] = df['close'].rolling(window=7).max()
    return df


def get_current_price(symbol):
    """
    Retrieves the current price for the specified trading symbol.

    Args:
        symbol (str): Trading symbol (e.g., 'BTCUSDT').

    Returns:
        float: The current price of the symbol.
    """
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        print(f"The current price of {symbol} is {current_price}")
        return current_price
    except Exception as e:
        subject = f'Error retrieving the current price for {symbol} - {get_current_price.__name__}'
        body = f"An error occurred while retrieving the current price:\n\n{e}"
        send_email(subject, body)
        log_error(str(e), get_current_price.__name__)
        print(body)
        return None

def execute_order(side, symbol, quantity, price=None):
    """
    Executes a buy or sell order on Binance.

    Args:
        client: The Binance client instance.
        side: 'BUY' or 'SELL'
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Amount to buy or sell
        price: Optional limit price for the order

    Returns:
        A message indicating the success or failure of the order.

    """
    # Define order parameters
    order_params = {
        'symbol': symbol,
        'side': side,
        'quantity': round(quantity, 4),
        'type': 'MARKET' if price is None else 'STOP_LOSS_LIMIT',
        'timeInForce': 'GTC' if price else None
    }

    if price:
        order_params.update({
            'price': round(price / 1.01, 2),  # adjustment to make sure stop loss triggers immediately
            'stopPrice': round(price, 2)
        })

    try:


        # Create the order
        order = client.create_order(**order_params)

        return "Order executed successfully."

    except Exception as e:
        subject = f'Error executing trade on {symbol} - {execute_order.__name__}'
        body = f"An error occurred while executing a trade:\n\n{e}\n\n{order_params}"
        send_email(subject, body)
        log_error(str(e), execute_order.__name__)
        print(body)
        return None


def cancel_stoploss(symbol):
    """
    Cancels all stop-loss orders for a given symbol.

    Args:
        client: Instance of the Binance client.
        symbol: Trading symbol (e.g., 'ETHUSDT') to cancel stop-loss orders for.
    """
    try:
        # Retrieve all open orders for the specified symbol
        open_orders = client.get_open_orders(symbol=symbol)

        # Identify and cancel stop-loss orders
        cancelled_orders = []
        for order in open_orders:
            if order['type'] == 'STOP_LOSS_LIMIT':
                result = client.cancel_order(symbol=symbol, orderId=order['orderId'])
                cancelled_orders.append(result)
                print(f"Stop-loss order cancelled: {result}")

        if cancelled_orders:
            print(f"All stop-loss orders for {symbol} have been cancelled.")
        else:
            print(f"No stop-loss orders to cancel for {symbol}.")
        return cancelled_orders

    except Exception as e:
        subject = f'Error cancelling stop loss on {symbol} - {cancel_stoploss.__name__}'
        body = f"An error occurred while cancelling stop loss:\n\n{e}"
        send_email(subject, body)
        log_error(str(e), cancel_stoploss.__name__)
        print(body)
        return None


def execute_trade_logic(df, current_state, symbol):
    """
    Executes trade logic based on EMA crossover and updates trading state.

    Args:
        df (DataFrame): The DataFrame containing the latest market data.
        current_state (dict): Dictionary holding the current trading state.
        symbol (str): Trading symbol (e.g., 'ETHUSDT').

    Returns:
        dict: Updated trading state after processing potential buy or sell signals.
    """
    in_position = current_state['in_position']
    balance = current_state['balance']
    entry_price = current_state['entry_price']
    stop_loss = current_state['stop_loss']
    shares = current_state['shares']

    current_price = get_current_price(symbol)
    last_low = df['low'].iloc[-1]
    timestamp = df.index[-1]

    trade_successful = False
    trade_type = None
    exit_price = None
    ema9 = df['EMA9'].iloc[-1]
    ema100 = df['EMA100'].iloc[-1]
    highest_close_7 = df['Highest_7_Close'].iloc[-2]
    close = df['close'].iloc[-1]

    if not in_position:
        """
        The detailed implementation of the strategy has been hidden
        to protect proprietary methods and logic.
        """
        # STRATEGY LOGIC OMITTED

    elif in_position:
        """
        The detailed implementation of the strategy has been hidden
        to protect proprietary methods and logic.
        """
        # STRATEGY LOGIC OMITTED

    if trade_successful:
        return {
            'entry_price':entry_price,
            'action': trade_type,
            'in_position': in_position,
            'balance': balance,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'shares': shares,
            'last_update': datetime.now().isoformat()

        }

    # Return current state if no conditions met
    return current_state


def trading_bot(symbol, interval):
    # Create the collection name
    collection_name = f'{symbol}_{interval}'

    # Create the key for your entity
    print(f'here {datastore_client}')
    key = datastore_client.key(collection_name, 'current_state')

    # Retrieve the current state from Datastore
    entity = datastore_client.get(key)

    if not entity:
        # Initialize the state if it's the first execution
        entity = datastore.Entity(key)
        entity.update({
            'in_position': False,
            'balance': 100,  # Initial balance in usdt
            'entry_price': 0,
            'exit_price':0,
            'stop_loss': 0,
            'shares': 0,
            'action': 'INIT',
            'last_update': datetime.now().isoformat()
        })


    current_state = dict(entity)

    # Retrieve historical data
    df = get_historical_data(symbol, interval, limit=200)
    df = calculate_indicators(df)

    # Execute trading logic
    new_state = execute_trade_logic(df, current_state, symbol)

    # Update the state in Datastore
    entity.update(new_state)
    datastore_client.put(entity)

    # Logging
    print(f"Action: {new_state.get('action', 'HOLD')}")
    print(f"New state: {new_state}")

    return 'Trading bot executed successfully'

client = initialize()
datastore_client = connect_to_datastore()

trading_bot(symbol = 'ETHUSDT', interval = '15m')