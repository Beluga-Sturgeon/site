import pandas as pd
import subprocess

from app.services.cnst import constants, emailvars

def readstats():
    file_path = constants.STATS_FILE_PATH

    # Read the data from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Split the first line by commas
    data = lines[0].strip().split(',')

    # Create a DataFrame from the data
    df = pd.DataFrame([data], columns=["Ticker", "Annualized Return benchmark", "Stdev of Returns benchmark", "Shape Ratio benchmark", "Maximum Drawdown benchmark", "Annualized Return model", "Stdev of Returns model", "Sharpe Ratio model", "Maximum Drawdown model"])
    return df

def readlog():
    log_file_path = constants.LOG_FILE_PATH

    # Read the last line of the log file
    with open(log_file_path, 'r') as file:
        lines = file.readlines()
        last_line = lines[-1]

    # Split the last line by commas and create a DataFrame with the specified column labels
    columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
    data = [last_line.split(',')]
    df = pd.DataFrame(data, columns=columns)
    return df

def runtest(ticker:str):
    #subprocess.run(f'ls', shell=True, check=True)
    # Define the directory you want to change to
    directory_path = "app/services/gbm-drl-quant"

    # Define the command you want to execute
    command = f".\\exec test {ticker} .\\models\\checkpoint"

    try:
        # Change the current directory to the specified path
        subprocess.run(f'cd {directory_path} && {command}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def getdata(ticker:str):
    runtest(ticker=ticker)

    log = readlog()
    stats = readstats()

    return {
        "ticker":ticker,
        "action":log["action"],
        "e_a_r" : stats["Annualized Return model"],
        "std" : stats["Stdev of Returns model"],
        "sharperatio":stats["Sharpe Ratio model"],
        "maxdrawdown":stats["Maximum Drawdown model"]
    }

if __name__ == "__main__":
    print(getdata("AAPL"))
    




