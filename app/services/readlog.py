import pandas as pd
import subprocess
from app.services.cnst import constants


def readstats(ticker:str):
    file_path = constants.STATS_FILE_PATH.format(ticker)
    try:
        with open(file_path, 'r') as file:
            # Read the data from the file
            lines = file.readlines()
            # Split the first line by commas
            data = lines[0].strip().split(',')

            # Create a DataFrame from the data
            df = pd.DataFrame([data], columns=["Ticker", "Annualized Return benchmark", "Stdev of Returns benchmark", "Shape Ratio benchmark", "Maximum Drawdown benchmark", "Annualized Return model", "Stdev of Returns model", "Sharpe Ratio model", "Maximum Drawdown model"])
            return df
    except: 
        return None


def readlog(ticker:str, lastonly=False):
    log_file_path = constants.LOG_FILE_PATH.format(ticker)
    try:
        with open(log_file_path, 'r') as file:        
            # Read the last line of the log file when lastonly is True
            if lastonly:
                lines = file.readlines()
                columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
                data = [lines[-1].split(',')]
                data[0][-1] = data[0][-1].rstrip()  # Remove newline character from the last element
                df = pd.DataFrame(data, columns=columns)
                return df
            # Read the entire log file when lastonly is False
            lines = file.readlines()
            columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
            data = [l.strip().split(',') for l in lines[1:]]  # Skip the first line if not lastonly
            df = pd.DataFrame(data, columns=columns)
            df['model'] = df['model'].str.rstrip()  # Remove newline characters from the 'model' column
            return df
    except: 
        return None

def runtest(ticker:str):
    #subprocess.run(f'ls', shell=True, check=True)
    # Define the directory you want to change to

    try:
        # Change the current directory to the specified path
        subprocess.run(f'cd {constants.DIRECTORY_PATH} && {constants.QUANT_COMMAND.format(ticker)}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def read_portfolio(lastonly = False):
    """returns Dataframe with portfolio readings.
    
        NVDA      TSLA     AAPL       AMD     GOOGL
    0  0.19943  0.208618  0.20574  0.195329  0.190883
    """
    action_file_path = constants.PORTFOLIO_LOG_FILE_PATH
    # Read the last line of the log file when lastonly is True
    if lastonly:
        with open(action_file_path, 'r') as file:
            lines = file.readlines()
            columns = columns = lines[0].strip().split(',')
            data = [lines[-1].split(',')]
            data[0][-1] = data[0][-1].rstrip()  # Remove newline character from the last element
            df = pd.DataFrame(data, columns=columns)
            return df, columns

    # Read the entire log file when lastonly is False
    with open(action_file_path, 'r') as file:
        N = 1
        lines = file.readlines()
        while sum(list(map(int(lines[N].strip().split(','))))) == 0:
            N += 1

        columns = lines[0].strip().split(',')
        data = [l.strip().split(',') for l in lines[N:]]  # Skip the first N-1 lines.
        df = pd.DataFrame(data, columns=columns)
        df[columns[-1]] = df[columns[-1]].str.rstrip()  # Remove newline characters from the columns[-1] column
        return df
    
def portfolio_to_dict():
    """Returns `read_portfolio(True)` as a dictionary"""
    df, headers = read_portfolio(lastonly=True)
    if df.empty:
        return {}
    return dict(zip(headers, df.iloc[0]))

if __name__ == "__main__":
    print(read_portfolio(True))



