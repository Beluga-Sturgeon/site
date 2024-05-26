import pandas as pd
import subprocess
from app.services.cnst import constants


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


def readlog(lastonly=False):
    log_file_path = constants.LOG_FILE_PATH

    # Read the last line of the log file when lastonly is True
    if lastonly:
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
            data = [lines[-1].split(',')]
            data[0][-1] = data[0][-1].rstrip()  # Remove newline character from the last element
            df = pd.DataFrame(data, columns=columns)
            return df


    # Read the entire log file when lastonly is False
    with open(log_file_path, 'r') as file:
        lines = file.readlines()
        columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
        data = [l.strip().split(',') for l in lines[1:]]  # Skip the first line if not lastonly
        df = pd.DataFrame(data, columns=columns)
        df['model'] = df['model'].str.rstrip()  # Remove newline characters from the 'model' column
        return df

def runtest(ticker:str):
    #subprocess.run(f'ls', shell=True, check=True)
    # Define the directory you want to change to

    try:
        # Change the current directory to the specified path
        subprocess.run(f'cd {constants.DIRECTORY_PATH} && {constants.QUANT_COMMAND.format(ticker)}', shell=True, check=True)
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
    




